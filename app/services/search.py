from __future__ import annotations

from dataclasses import dataclass

from ddgs import DDGS

from app.models.tools import SourceItem


class WebSearchError(RuntimeError):
    pass


@dataclass
class DuckDuckGoSearchService:
    timeout_s: float = 8.0

    def search(self, query: str, max_results: int = 3) -> list[SourceItem]:
        if not query.strip():
            raise ValueError("query must not be blank")

        try:
            results = DDGS(timeout=self.timeout_s).text(
                query,
                max_results=max_results,
            )

            items: list[SourceItem] = []

            for result in results:
                items.append(
                    SourceItem(
                        title=result.get("title", ""),
                        url=result.get("href", ""),
                        snippet=result.get("body", ""),
                    )
                )

            return items

        except Exception as exc:
            raise WebSearchError(
                f"Web search unavailable: {exc}"
            ) from exc