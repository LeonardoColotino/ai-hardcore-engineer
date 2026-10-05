from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol
import requests

from app.config import Settings


class LLMError(RuntimeError):
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
        payload = {
            "model": self.model,
            "stream": False,
            "options": {"temperature": self.temperature},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout_s)
            response.raise_for_status()
            body = response.json()
            content = body.get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                raise LLMError("Ollama returned an invalid chat response")
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
