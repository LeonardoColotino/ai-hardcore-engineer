from __future__ import annotations

from dataclasses import dataclass
from app.models.tools import SourceItem
from app.services.embeddings import EmbeddingService
from .vector_store import NumpyVectorStore, SearchHit


@dataclass
class RetrievalResult:
    hits: list[SearchHit]
    sources: list[SourceItem]


class Retriever:
    def __init__(self, store: NumpyVectorStore, embeddings: EmbeddingService, top_k: int, min_score: float):
        self.store = store
        self.embeddings = embeddings
        self.top_k = top_k
        self.min_score = min_score

    def retrieve(self, query: str) -> RetrievalResult:
        vector = self.embeddings.embed([query])[0]
        raw = self.store.search(vector, self.top_k)
        filtered: list[SearchHit] = []
        seen: set[str] = set()
        for hit in raw:
            source_key = f"{hit.metadata.get('url', '')}|{hit.text[:100]}"
            if hit.score < self.min_score or source_key in seen:
                continue
            seen.add(source_key)
            filtered.append(hit)
        sources = [
            SourceItem(
                title=str(hit.metadata.get("title", "Getnet source")),
                url=str(hit.metadata.get("url", "")),
                snippet=hit.text[:220],
                score=round(hit.score, 4),
            )
            for hit in filtered
        ]
        return RetrievalResult(hits=filtered, sources=sources)
