from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
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
        if matrix.ndim != 2 or not matrix.shape[1] or not np.isfinite(matrix).all():
            raise ValueError("Embedding vectors must be a finite two-dimensional matrix")
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        matrix = matrix / norms
        np.save(self.vectors_path, matrix)
        self.docs_path.write_text(json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8")
        self.vectors = matrix
        self.documents = documents
        manifest = {"schema_version":2,"vectors_sha256":hashlib.sha256(self.vectors_path.read_bytes()).hexdigest(),"built_at":datetime.now(timezone.utc).isoformat(),"dimension":matrix.shape[1],"documents":len(documents),"corpus_sha256":hashlib.sha256(self.docs_path.read_bytes()).hexdigest(),"corpus_kind":"demo_seed" if any(d.get('metadata',{}).get('source')=='offline-seed' for d in documents) else "official"}
        (self.directory / "manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")

    def load(self) -> None:
        if not self.ready:
            raise FileNotFoundError("RAG index does not exist. Run: python -m app.rag.ingest")
        self.vectors = np.load(self.vectors_path, allow_pickle=False)
        if self.vectors.ndim != 2 or not np.isfinite(self.vectors).all():
            raise ValueError("Corrupt RAG vectors")
        self.documents = json.loads(self.docs_path.read_text(encoding="utf-8"))
        manifest_path = self.directory / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get('vectors_sha256') and manifest['vectors_sha256'] != hashlib.sha256(self.vectors_path.read_bytes()).hexdigest():
                raise ValueError("RAG vector integrity mismatch; rebuild index")
            if manifest.get('dimension') != self.vectors.shape[1] or manifest.get('corpus_sha256') != hashlib.sha256(self.docs_path.read_bytes()).hexdigest():
                raise ValueError("RAG manifest does not match corpus/vectors; rebuild index")
        if not isinstance(self.documents,list) or any(not isinstance(d,dict) or not isinstance(d.get('text'),str) for d in self.documents):
            raise ValueError("Corrupt RAG documents")
        if len(self.documents) != len(self.vectors):
            raise ValueError("RAG index is inconsistent")

    def search(self, query_vector: list[float], top_k: int = 4) -> list[SearchHit]:
        if self.vectors is None:
            self.load()
        if self.vectors is None or not len(self.documents):
            return []
        q = np.asarray(query_vector, dtype=np.float32)
        if q.ndim != 1 or q.shape[0] != self.vectors.shape[1] or not np.isfinite(q).all():
            raise ValueError("Embedding provider/dimension mismatch; rebuild index with current provider")
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
