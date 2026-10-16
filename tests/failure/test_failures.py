from pathlib import Path
from app.rag.vector_store import NumpyVectorStore
from app.services.embeddings import HashingEmbeddingService
from app.rag.retriever import Retriever
from app.tools.rag_search import RAGSearchTool
from app.services.customer_data import JsonRepository
from app.tools.customer_lookup import CustomerLookupTool


def test_missing_rag_index_is_handled(tmp_path: Path):
    tool = RAGSearchTool(Retriever(NumpyVectorStore(tmp_path / "missing"), HashingEmbeddingService(), 3, 0.1))
    result = tool.run("Getnet")
    assert not result.success
    assert "index" in result.error.lower()


def test_data_access_failure_is_hidden_from_user(tmp_path: Path):
    result = CustomerLookupTool(JsonRepository(tmp_path / "no-data")).run("u1")
    assert not result.success
    assert "could not access" in result.error.lower()
