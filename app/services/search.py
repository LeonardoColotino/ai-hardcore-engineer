from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, unquote, urlparse
import requests
from app.services.budget import timeout as budget_timeout
from bs4 import BeautifulSoup

from app.models.tools import SourceItem
from app.services.public_query import public_query


class WebSearchError(RuntimeError):
    pass


@dataclass
class DuckDuckGoSearchService:
    timeout_s: float = 8.0

    def search(self, query: str, max_results: int = 3) -> list[SourceItem]:
        query = public_query(query)
        if not query.strip():
            raise ValueError("query must not be blank")
        try:
            response = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                timeout=budget_timeout(self.timeout_s),
                headers={"User-Agent": "Mozilla/5.0 AI-Hardcore-Engineer/2.0"},
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            items: list[SourceItem] = []
            for result in soup.select(".result"):
                link = result.select_one(".result__a")
                snippet = result.select_one(".result__snippet")
                if not link:
                    continue
                href = link.get("href", "")
                if "uddg=" in href:
                    qs = parse_qs(urlparse(href).query)
                    href = unquote(qs.get("uddg", [href])[0])
                items.append(SourceItem(title=link.get_text(" ", strip=True), url=href, snippet=snippet.get_text(" ", strip=True) if snippet else ""))
                if len(items) >= max_results:
                    break
            return items
        except requests.RequestException as exc:
            raise WebSearchError(f"Web search unavailable: {exc}") from exc
