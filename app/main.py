from __future__ import annotations

from fastapi import FastAPI
from app.api.routes import router
from app.config import get_settings
from app.observability.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="4.0.0",
    description="Multi-agent support system with RAG, tools, guardrails, observability and deterministic evaluation.",
)
app.include_router(router)

from fastapi.staticfiles import StaticFiles
from pathlib import Path
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="chat")

@app.middleware("http")
async def failure_metrics(request, call_next):
    from app.orchestration.supervisor import metrics, rate_lock
    try:
        response = await call_next(request)
    except Exception:
        from fastapi.responses import JSONResponse
        return JSONResponse({'detail':'Falha interna. Consulte o histórico antes de reenviar.'},status_code=500)
    return response
