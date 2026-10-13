from __future__ import annotations

from dataclasses import dataclass
from app.models.tools import SourceItem
from app.services.embeddings import EmbeddingService
from .vector_store import NumpyVectorStore, SearchHit
from .relevance import relevant


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
        import json
        manifest_path = self.store.directory / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            saved_model = manifest.get("embedding_model")
            if saved_model and hasattr(self.embeddings,'model') and saved_model != self.embeddings.model:
                raise ValueError("Embedding model changed; rebuild the index")
        from app.orchestration.intents import products
        aliases = {'Link de Pagamento':'payment link online payment links','Conta Digital':'digital account','maquininha':'card machines','antecipação':'receivables advance','crediário':'installment sales installments crediário'}
        expanded = query + ' ' + ' '.join(aliases.get(p,'') for p in products(query))
        vector = self.embeddings.embed([expanded])[0]
        raw = self.store.search(vector, max(self.top_k, min(40, self.top_k * 8)))
        import re
        from .relevance import normalized
        terms = set(re.findall(r"[a-z0-9]{3,}", normalized(expanded))) - {'como','funciona','quais','getnet','para','the','with','does','what'}
        def lexical(hit):
            tokens = set(re.findall(r"[a-z0-9]{3,}",normalized(hit.text)))
            return len(terms & tokens) / max(1,len(terms))
        # Reciprocal rank fusion preserves vector and keyword ranks independently.
        vector_rank = {id(h):i for i,h in enumerate(raw)}
        keyword_rank = {id(h):i for i,h in enumerate(sorted(raw,key=lexical,reverse=True))}
        procedure_request = bool(re.search(r'como.*(?:criar|crio|gerar)|how.*create',normalized(query)))
        def tutorial_priority(hit):
            section=normalized(str(hit.metadata.get('section','')))
            body=normalized(hit.text)
            return int(procedure_request and bool(re.search(r'veja como|passo a passo|tutorial',section)) and all(word in body for word in ('criar','compartilh')))
        raw.sort(key=lambda h: tutorial_priority(h) + 1/(20+vector_rank[id(h)]) + 1/(20+keyword_rank[id(h)]), reverse=True)
        filtered: list[SearchHit] = []
        seen: set[str] = set()
        for hit in raw:
            source_key = f"{hit.metadata.get('url', '')}|{hit.text[:100]}"
            if hit.score < self.min_score or source_key in seen or not relevant(query,hit.text,str(hit.metadata.get("title","")),str(hit.metadata.get("url",""))):
                continue
            seen.add(source_key)
            filtered.append(hit)
            if len(filtered) >= self.top_k:
                break
        sources = [
            SourceItem(
                title=str(hit.metadata.get("title", "Getnet source")),
                url=str(hit.metadata.get("url", "")),
                snippet=hit.text,
                score=round(hit.score, 4),
            )
            for hit in filtered
        ]
        return RetrievalResult(hits=filtered, sources=sources)
