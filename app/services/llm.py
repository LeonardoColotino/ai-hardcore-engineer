from __future__ import annotations

import json
import os
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
        raise LLMError("LLM provider is disabled. Set LLM_PROVIDER=ollama to enable generation.")


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
            "options": {"temperature": self.temperature, "num_predict": int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "96")), "num_ctx": 4096},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if schema is not None:
            payload["format"] = schema
            payload["options"]["temperature"] = 0
        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=budget_timeout(self.timeout_s))
            response.raise_for_status()
            body = response.json()
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
    return DisabledLLMClient()


def parse_json_object(text: str) -> dict:
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMError("Model did not return valid JSON") from exc
    if not isinstance(obj, dict):
        raise LLMError("Model JSON output must be an object")
    return obj
