from __future__ import annotations

from dataclasses import dataclass
import os
import re
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
            expected_provider = "ollama" if hasattr(self.embeddings, "model") else "hashing"
            if manifest.get("embedding_provider") and manifest["embedding_provider"] != expected_provider:
                raise ValueError("Embedding provider changed; rebuild the index")
            saved_model = manifest.get("embedding_model")
            if saved_model and hasattr(self.embeddings,'model') and saved_model != self.embeddings.model:
                raise ValueError("Embedding model changed; rebuild the index")
        from app.orchestration.intents import products
        aliases = {'Link de Pagamento':'payment link online payment links','Conta Digital':'digital account','maquininha':'card machines','antecipação':'receivables advance','crediário':'installment sales installments crediário'}
        expanded = query + ' ' + ' '.join(aliases.get(p,'') for p in products(query))
        vector = self.embeddings.embed([expanded])[0]
        raw = self.store.search(vector, max(self.top_k, min(40, self.top_k * 8)))
        profile = os.getenv("RAG_RETRIEVAL_PROFILE", "hybrid")
        if profile not in {"vector", "lexical", "hybrid"}:
            raise ValueError("Unknown retrieval profile")
        from .rerank import bm25, rerank
        if profile != 'vector':
            documents = self.store.documents
            if not isinstance(documents, list):
                documents = [{'text': h.text, 'metadata': h.metadata} for h in raw]
            lex = bm25(query, documents)
            lexical = [SearchHit(documents[i]['text'], score, documents[i].get('metadata', {})) for i, score in lex]
            if profile == 'lexical':
                raw = lexical
            else:
                fused = {}
                dense_scores = {h.text: h.score for h in raw}
                for ranking in (raw, lexical):
                    for rank, hit in enumerate(ranking, 1):
                        entry = fused.setdefault(hit.text, [hit, 0.0])
                        entry[1] += 1.0 / (60 + rank)
                import numpy as np
                if isinstance(self.store.vectors, np.ndarray):
                    q = np.asarray(vector, dtype=np.float32)
                    q = q / (np.linalg.norm(q) or 1.0)
                    dense_scores.update({d['text']: float(score) for d, score in zip(self.store.documents, self.store.vectors @ q)})
                raw = [SearchHit(entry[0].text, dense_scores.get(entry[0].text, 0.0), entry[0].metadata) for entry in sorted(fused.values(), key=lambda e: e[1], reverse=True)]
        mode = os.getenv('RERANKER', 'none')
        if mode != 'none':
            raw = rerank(query, raw)
        from app.orchestration.intents import normalized
        procedure = bool(re.search(r'como.*(?:criar|crio|gerar)|how.*create', normalized(query)))
        if procedure:
            raw.sort(key=lambda h: int(bool(re.search(r'veja como|passo a passo|tutorial', normalized(str(h.metadata.get('section', ''))))) and all(w in normalized(h.text) for w in ('criar', 'compartilh'))), reverse=True)
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
