"""Optional zero-API-cost GGUF provider, loaded only when configured."""

import os
import threading
from app.services.llm import LLMError, LLMTruncatedError, record_usage
from app.services.budget import timeout


class LocalGGUFClient:
    def __init__(self):
        from llama_cpp import Llama

        path = os.getenv("GGUF_MODEL_PATH", "")
        if not path:
            raise ValueError("GGUF_MODEL_PATH required for llama_cpp")
        self.model = Llama(
            model_path=path,
            n_ctx=int(os.getenv("GGUF_CONTEXT", "8192")),
            n_threads=int(os.getenv("GGUF_THREADS", "4")),
            verbose=False,
        )
        self.lock = threading.Lock()

    def generate(self, system, user):
        return self._generate(system, user)

    def generate_structured(self, system, user, schema):
        return self._generate(system, user, schema)

    def _generate(self, system, user, schema=None):
        # Synchronous inference cannot be force-cancelled. Deadline is enforced
        # between stages; output tokens and context cap compute per request.
        import requests

        try:
            timeout(1)
        except requests.Timeout as exc:
            raise LLMError("Local request budget exhausted") from exc
        options = (
            {"response_format": {"type": "json_object", "schema": schema}}
            if schema
            else {}
        )
        try:
            with self.lock:
                timeout(1)  # recheck budget after waiting for the model
                result = self.model.create_chat_completion(
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0,
                    max_tokens=int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "512")),
                    **options,
                )
            choice = result["choices"][0]
            if choice["finish_reason"] == "length":
                raise LLMTruncatedError("GGUF output token limit")
            u = result.get('usage') or {}
            record_usage('llama_cpp', os.path.basename(os.getenv('GGUF_MODEL_PATH', '')), {'input_tokens': u.get('prompt_tokens'), 'output_tokens': u.get('completion_tokens')})
            content = choice.get('message', {}).get('content')
            if not isinstance(content, str) or not content.strip():
                raise LLMError('Local model returned empty or invalid content')
            return choice["message"]["content"]
        except LLMError:
            raise
        except (ValueError, KeyError, RuntimeError, TypeError, IndexError, requests.Timeout) as exc:
            raise LLMError("Local model inference failed") from exc
