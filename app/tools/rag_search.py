from __future__ import annotations

from dataclasses import dataclass
from app.models.tools import ToolResult
from app.rag.retriever import Retriever
from app.services.embeddings import EmbeddingError


@dataclass
class RAGSearchTool:
    retriever: Retriever
    name: str = "rag_search"

    def run(self, query: str) -> ToolResult:
        if not query.strip():
            return ToolResult(success=False, error="query must not be blank")
        try:
            result = self.retriever.retrieve(query)
        except (OSError, ValueError, EmbeddingError) as exc:
            return ToolResult(success=False, error=str(exc))
        if not result.hits:
            return ToolResult(success=False, error="No sufficiently relevant RAG context found")
        return ToolResult(
            success=True,
            data={
                "query": query,
                "contexts": [h.text for h in result.hits],
                "scores": [round(h.score, 4) for h in result.hits],
            },
            sources=result.sources,
            metadata={"retrieved_documents": len(result.hits), "best_score": max(h.score for h in result.hits)},
        )
