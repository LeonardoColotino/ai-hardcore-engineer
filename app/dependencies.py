from __future__ import annotations

from functools import lru_cache
from app.config import get_settings
from app.agents.router import RouterAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.support import SupportAgent
from app.agents.escalation import EscalationAgent
from app.guardrails.guardrails import InputGuardrails
from app.orchestration.orchestrator import Orchestrator
from app.rag.retriever import Retriever
from app.rag.vector_store import NumpyVectorStore
from app.services.customer_data import JsonRepository
from app.services.embeddings import HashingEmbeddingService, OllamaEmbeddingService
from app.services.llm import create_llm_client
from app.services.search import DuckDuckGoSearchService
from app.tools.rag_search import RAGSearchTool
from app.tools.web_search import WebSearchTool
from app.tools.customer_lookup import CustomerLookupTool
from app.tools.transaction_lookup import TransactionLookupTool
from app.tools.payment_status import PaymentStatusTool


@lru_cache(maxsize=1)
def get_orchestrator() -> Orchestrator:
    settings = get_settings()
    llm = create_llm_client(settings)
    # Keep hashing as the default index provider so local setup is zero-cost.
    # Switch both ingestion and runtime to Ollama embeddings when desired.
    if (settings.index_dir / "embedding_provider.txt").exists():
        provider = (settings.index_dir / "embedding_provider.txt").read_text(encoding="utf-8").strip()
    else:
        provider = "hashing"
    if provider == "ollama":
        embeddings = OllamaEmbeddingService(settings.ollama_base_url, settings.ollama_embed_model, settings.request_timeout_s)
    else:
        embeddings = HashingEmbeddingService()
    store = NumpyVectorStore(settings.index_dir)
    retriever = Retriever(store, embeddings, settings.rag_top_k, settings.rag_min_score)
    rag_tool = RAGSearchTool(retriever)
    web_tool = WebSearchTool(DuckDuckGoSearchService(settings.request_timeout_s), settings.web_search_max_results, enabled=settings.web_search_enabled)
    repo = JsonRepository(settings.data_dir)
    return Orchestrator(
        router=RouterAgent(settings, llm),
        knowledge=KnowledgeAgent(rag_tool, web_tool, llm, llm_enabled=settings.llm_provider == "ollama"),
        support=SupportAgent(CustomerLookupTool(repo), TransactionLookupTool(repo), PaymentStatusTool(repo)),
        escalation=EscalationAgent(),
        guardrails=InputGuardrails(),
    )
