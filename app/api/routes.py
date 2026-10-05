from __future__ import annotations

from fastapi import APIRouter, Depends
from app.config import get_settings
from app.dependencies import get_orchestrator
from app.models.api import ChatRequest, ChatResponse, HealthResponse
from app.orchestration.orchestrator import Orchestrator
from app.rag.vector_store import NumpyVectorStore

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    store = NumpyVectorStore(settings.index_dir)
    return HealthResponse(status="ok", llm_provider=settings.llm_provider, rag_index_ready=store.ready)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, orchestrator: Orchestrator = Depends(get_orchestrator)) -> ChatResponse:
    return orchestrator.handle(payload)
