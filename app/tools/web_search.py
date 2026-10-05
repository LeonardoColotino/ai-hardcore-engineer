from __future__ import annotations

from dataclasses import dataclass
from app.models.tools import ToolResult
from app.services.search import DuckDuckGoSearchService, WebSearchError


@dataclass
class WebSearchTool:
    service: DuckDuckGoSearchService
    max_results: int = 3
    enabled: bool = True
    name: str = "web_search"

    def run(self, query: str) -> ToolResult:
        if not self.enabled:
            return ToolResult(success=False, error="Web search is disabled")
        try:
            sources = self.service.search(query, self.max_results)
            if not sources:
                return ToolResult(success=False, error="No web results found")
            return ToolResult(success=True, data={"query": query, "count": len(sources)}, sources=sources)
        except (ValueError, WebSearchError) as exc:
            return ToolResult(success=False, error=str(exc))
