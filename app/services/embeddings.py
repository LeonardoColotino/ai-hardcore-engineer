from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Protocol

import numpy as np
import requests


class EmbeddingError(RuntimeError):
    pass


class EmbeddingService(Protocol):
    dimension: int
    def embed(self, texts: list[str]) -> list[list[float]]: ...


@dataclass
class HashingEmbeddingService:
    """Deterministic local embedding for offline development/tests.

    It uses hashed unigram+bigram features. It is deliberately simple, transparent,
    reproducible, and can be replaced by Ollama without changing the RAG pipeline.
    """
    dimension: int = 384

    def _vector(self, text: str) -> list[float]:
        tokens = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", text.lower())
        features = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
        v = np.zeros(self.dimension, dtype=np.float32)
        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            n = int.from_bytes(digest, "big")
            idx = n % self.dimension
            sign = 1.0 if (n >> 1) & 1 else -1.0
            v[idx] += sign
        norm = float(np.linalg.norm(v))
        if norm:
            v /= norm
        return v.tolist()

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]


@dataclass
class OllamaEmbeddingService:
    base_url: str
    model: str
    timeout_s: float = 12.0
    dimension: int = 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            response = requests.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": texts},
                timeout=self.timeout_s,
            )
            response.raise_for_status()
            payload = response.json()
            vectors = payload.get("embeddings")
            if not isinstance(vectors, list) or len(vectors) != len(texts):
                raise EmbeddingError("Ollama returned an invalid embedding response")
            if vectors and not self.dimension:
                self.dimension = len(vectors[0])
            return vectors
        except requests.RequestException as exc:
            raise EmbeddingError(f"Could not reach Ollama embeddings endpoint: {exc}") from exc
        except (ValueError, TypeError) as exc:
            raise EmbeddingError(f"Invalid Ollama embedding response: {exc}") from exc
