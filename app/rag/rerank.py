"""Hybrid retrieval and independently configurable second-stage reranking."""

from __future__ import annotations
import math
import os
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from app.rag.vector_store import SearchHit


def tokens(text):
    clean = unicodedata.normalize("NFKD", text.lower())
    clean = "".join(c for c in clean if not unicodedata.combining(c))
    stop = {
        "a",
        "o",
        "e",
        "de",
        "da",
        "do",
        "em",
        "the",
        "is",
        "of",
        "to",
        "como",
        "qual",
        "getnet",
        "com",
        "para",
    }
    return [t for t in re.findall(r"[a-z0-9]+", clean) if t not in stop]


def bm25(query, documents):
    lists = [tokens(d["text"]) for d in documents]
    n = len(lists)
    if not n:
        return []
    avg = sum(map(len, lists)) / n or 1
    df = Counter(t for ts in lists for t in set(ts))
    result = []
    for i, ts in enumerate(lists):
        tf = Counter(ts)
        score = 0
        for t in set(tokens(query)):
            frequency = tf[t]
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            score += (
                idf
                * frequency
                * 2.2
                / (frequency + 1.2 * (0.25 + 0.75 * len(ts) / avg))
            )
        if score > 0:
            result.append((i, score))
    return sorted(result, key=lambda x: x[1], reverse=True)


@lru_cache(maxsize=1)
def cross_encoder(model):
    from sentence_transformers import CrossEncoder

    # No code downloaded from arbitrary model repos is executed.
    return CrossEncoder(
        model,
        trust_remote_code=False,
        revision=os.getenv(
            "RERANKER_REVISION", "1427fd652930e4ba29e8149678df786c240d8825"
        ),
    )


def rerank(query, hits):
    mode = os.getenv("RERANKER", "lexical")
    if mode == "cross_encoder":
        model = os.getenv(
            "RERANKER_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
        )
        scores = cross_encoder(model).predict([(query, h.text) for h in hits])
        return [
            h
            for _, h in sorted(
                zip(map(float, scores), hits), key=lambda x: x[0], reverse=True
            )
        ]
    if mode != "lexical":
        raise ValueError("Unknown RERANKER")
    # Lightweight second stage: query coverage + exact phrase matching.
    # This is a lexical scorer, explicitly NOT a learned semantic reranker.
    q = set(tokens(query))

    def score(hit):
        d = set(tokens(hit.text + " " + str(hit.metadata.get("title", ""))))
        return len(q & d) / max(1, len(q)) + 0.05 * hit.score

    return sorted(hits, key=score, reverse=True)

