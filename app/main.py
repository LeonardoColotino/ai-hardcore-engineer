from __future__ import annotations

from fastapi import FastAPI
from app.api.routes import router
from app.config import get_settings
from app.observability.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="Multi-agent support system with RAG, tools, guardrails, observability and deterministic evaluation.",
)
app.include_router(router)
