from __future__ import annotations

import json
from pathlib import Path
import pytest
from app.config import Settings
from app.services.customer_data import JsonRepository
from app.services.embeddings import HashingEmbeddingService
from app.rag.vector_store import NumpyVectorStore
from app.rag.retriever import Retriever


@pytest.fixture
def tmp_repo(tmp_path: Path) -> JsonRepository:
    (tmp_path / "customers.json").write_text(json.dumps([{"user_id":"u1","name":"A","account_status":"active"}]), encoding="utf-8")
    (tmp_path / "transactions.json").write_text(json.dumps([{"user_id":"u1","reference":"T1","status":"declined","amount":"10","channel":"POS"}]), encoding="utf-8")
    (tmp_path / "payments.json").write_text(json.dumps([{"user_id":"u1","status":"scheduled","expected_date":"2026-10-06","amount":"10"}]), encoding="utf-8")
    return JsonRepository(tmp_path)


@pytest.fixture
def rag_retriever(tmp_path: Path) -> Retriever:
    emb = HashingEmbeddingService(dimension=128)
    docs = [
        {"text":"Getnet payment link can be shared on WhatsApp and social networks.","metadata":{"title":"Link","url":"https://example/link"}},
        {"text":"Getnet card machines support Pix and QR Code payments.","metadata":{"title":"Pix","url":"https://example/pix"}},
    ]
    store = NumpyVectorStore(tmp_path / "idx")
    store.build(emb.embed([d["text"] for d in docs]), docs)
    return Retriever(store, emb, top_k=2, min_score=-1.0)
