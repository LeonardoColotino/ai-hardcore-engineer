from __future__ import annotations

import json
import os
from contextvars import ContextVar

usage_context = ContextVar("llm_usage", default=None)
provider_usage = ContextVar("provider_usage", default=None)

def reset_provider_usage():
    provider_usage.set(None)

def get_provider_usage():
    return provider_usage.get()

def record_usage(provider, model, counts):
    valid = {k: v for k, v in counts.items() if isinstance(v, int) and not isinstance(v, bool) and v >= 0}
    if valid:
        previous = provider_usage.get() or {}
        provider_usage.set({k: (previous.get(k) or 0) + valid[k] if k in valid else previous.get(k) for k in ('input_tokens', 'output_tokens')})
    rows = usage_context.get()
    if rows is not None:
        rows.append({'provider': provider, 'model': model, **counts})

from dataclasses import dataclass
from typing import Protocol
import requests
from app.services.budget import timeout as budget_timeout

from app.config import Settings


class LLMError(RuntimeError):
    pass


class LLMTruncatedError(LLMError):
    """Provider stopped at output token limit, not a complete answer."""

    pass


class LLMClient(Protocol):
    def generate(self, system: str, user: str) -> str: ...


@dataclass
class DisabledLLMClient:
    def generate(self, system: str, user: str) -> str:
        raise LLMError(
            "LLM provider is disabled. Set LLM_PROVIDER=ollama to enable generation."
        )


@dataclass
class OllamaLLMClient:
    base_url: str
    model: str
    timeout_s: float = 12.0
    temperature: float = 0.1

    def generate(self, system: str, user: str) -> str:
        return self._generate(system, user)

    def generate_structured(self, system: str, user: str, schema: dict) -> str:
        return self._generate(system, user, schema)

    def _generate(self, system: str, user: str, schema: dict | None = None) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "768")),
                "num_ctx": int(os.getenv("LLM_CONTEXT_TOKENS", "4096")),
            },
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if schema is not None:
            payload["format"] = schema
            payload["options"]["temperature"] = 0
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=budget_timeout(self.timeout_s),
            )
            response.raise_for_status()
            body = response.json()
            record_usage('ollama', self.model, {'input_tokens': body.get('prompt_eval_count'), 'output_tokens': body.get('eval_count')})
            content = body.get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                raise LLMError("Ollama returned an invalid chat response")
            if body.get("done_reason") == "length":
                raise LLMTruncatedError("Output token budget reached")
            return content.strip()
        except requests.RequestException as exc:
            raise LLMError(f"Could not reach Ollama: {exc}") from exc
        except (ValueError, TypeError, KeyError) as exc:
            raise LLMError(f"Invalid Ollama response: {exc}") from exc


def create_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_provider == "ollama":
        return OllamaLLMClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_chat_model,
            timeout_s=settings.request_timeout_s,
        )
    if settings.llm_provider == "llama_cpp":
        from app.services.local_llm import LocalGGUFClient

        return LocalGGUFClient()
    if settings.llm_provider in ("openai_compatible", "openai-compatible"):
        return OpenAICompatibleClient(
            os.getenv("LLM_BASE_URL", "http://localhost:1234/v1").rstrip("/"),
            os.getenv("LLM_MODEL", "gpt-4.1-mini"),
            settings.request_timeout_s,
        )
    if settings.llm_provider != "disabled":
        raise ValueError("Unknown LLM_PROVIDER")
    return DisabledLLMClient()


def parse_json_object(text: str) -> dict:
    cleaned = (
        text.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMError("Model did not return valid JSON") from exc
    if not isinstance(obj, dict):
        raise LLMError("Model JSON output must be an object")
    return obj


@dataclass
class OpenAICompatibleClient:
    """Also accepts local compatible servers; credentials come only from env."""

    base_url: str
    model: str
    timeout_s: float = 30

    def generate(self, system, user):
        return self._request(system, user)

    def generate_structured(self, system, user, schema):
        return self._request(system, user, schema)

    def _request(self, system, user, schema=None):
        headers = {"Content-Type": "application/json"}
        key = os.getenv("LLM_API_KEY", "")
        if key:
            headers["Authorization"] = "Bearer " + key
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
            "max_tokens": int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "768")),
        }
        if schema:
            # Strict compatible APIs require every object property to be required.
            # Our schemas have no nullable optional fields; remove default annotations.
            schema = json.loads(json.dumps(schema))

            def strict_object(node):
                if isinstance(node, dict):
                    node.pop("default", None)
                    if node.get("type") == "object":
                        node["required"] = list(node.get("properties", {}))
                        node["additionalProperties"] = False
                    for value in node.values():
                        strict_object(value)
                elif isinstance(node, list):
                    for value in node:
                        strict_object(value)

            strict_object(schema)
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "agent_output",
                    "strict": True,
                    "schema": schema,
                },
            }
        try:
            response = requests.post(
                self.base_url + "/chat/completions",
                headers=headers,
                json=payload,
                timeout=budget_timeout(self.timeout_s),
            )
            response.raise_for_status()
            body = response.json()
            choice = body["choices"][0]
            if choice.get("finish_reason") == "length":
                raise LLMTruncatedError("Output token budget reached")
            text = choice["message"]["content"]
            if not isinstance(text, str) or not text.strip():
                raise ValueError("empty output")
            counts = body.get('usage') or {}
            record_usage('openai_compatible', self.model, {'input_tokens': counts.get('prompt_tokens'), 'output_tokens': counts.get('completion_tokens')})
            return text.strip()
        except (
            requests.RequestException,
            KeyError,
            IndexError,
            ValueError,
            TypeError,
        ) as exc:
            # Do not surface provider body or headers containing secrets.
            raise LLMError(
                "Compatible provider unavailable or invalid response"
            ) from exc
