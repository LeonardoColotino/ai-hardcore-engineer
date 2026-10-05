from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class SearchHit:
    text: str
    score: float
    metadata: dict[str, Any]


class NumpyVectorStore:
    """Small persistent cosine-similarity vector store.

    For this challenge, a transparent NumPy store avoids a heavyweight runtime
    dependency while preserving the complete vector-store behavior. The interface
    can be swapped for FAISS/Qdrant without touching agents.
    """

    def __init__(self, directory: Path):
        self.directory = directory
        self.vectors_path = directory / "vectors.npy"
        self.docs_path = directory / "documents.json"
        self.vectors: np.ndarray | None = None
        self.documents: list[dict[str, Any]] = []

    @property
    def ready(self) -> bool:
        return self.vectors_path.exists() and self.docs_path.exists()

    def build(self, vectors: list[list[float]], documents: list[dict[str, Any]]) -> None:
        if not vectors or not documents or len(vectors) != len(documents):
            raise ValueError("vectors and documents must be non-empty and have the same length")
        self.directory.mkdir(parents=True, exist_ok=True)
        matrix = np.asarray(vectors, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        matrix = matrix / norms
        np.save(self.vectors_path, matrix)
        self.docs_path.write_text(json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8")
        self.vectors = matrix
        self.documents = documents

    def load(self) -> None:
        if not self.ready:
            raise FileNotFoundError("RAG index does not exist. Run: python -m app.rag.ingest")
        self.vectors = np.load(self.vectors_path)
        self.documents = json.loads(self.docs_path.read_text(encoding="utf-8"))
        if len(self.documents) != len(self.vectors):
            raise ValueError("RAG index is inconsistent")

    def search(self, query_vector: list[float], top_k: int = 4) -> list[SearchHit]:
        if self.vectors is None:
            self.load()
        if self.vectors is None or not len(self.documents):
            return []
        q = np.asarray(query_vector, dtype=np.float32)
        norm = float(np.linalg.norm(q))
        if norm == 0:
            return []
        q = q / norm
        scores = self.vectors @ q
        top_indices = np.argsort(scores)[::-1][: max(1, top_k)]
        hits: list[SearchHit] = []
        for idx in top_indices:
            doc = self.documents[int(idx)]
            hits.append(SearchHit(text=doc["text"], score=float(scores[idx]), metadata=doc.get("metadata", {})))
        return hits
