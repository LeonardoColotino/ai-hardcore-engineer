"""
Serviço responsável pela comunicação com o modelo local via Ollama.
"""

import requests

from app.config import settings


class LLMService:
    """Cliente simples para comunicação com o Ollama."""

    def __init__(self) -> None:
        self.base_url = settings.OLLAMA_URL
        self.model = settings.MODEL_NAME

    def generate(self, prompt: str) -> str:
        """
        Envia um prompt para o Ollama e retorna a resposta gerada.

        Args:
            prompt: Texto que será enviado ao modelo.

        Returns:
            Resposta textual gerada pelo modelo.

        Raises:
            RuntimeError: Caso não seja possível comunicar com o Ollama.
        """

        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=60
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise RuntimeError(
                "Não foi possível comunicar com o Ollama."
            ) from exc

        data = response.json()

        return data.get(
            "response",
            ""
        ).strip()


llm_service = LLMService()