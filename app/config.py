from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
load_dotenv(PROJECT_DIR / ".env", encoding="utf-8-sig")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_float(value: str | None, default: float) -> float:
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default


def _as_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    log_level: str
    llm_provider: str
    ollama_base_url: str
    ollama_chat_model: str
    ollama_embed_model: str
    request_timeout_s: float
    router_min_confidence: float
    rag_top_k: int
    rag_min_score: float
    rag_source_urls: tuple[str, ...]
    web_search_max_results: int
    web_search_enabled: bool
    data_dir: Path
    index_dir: Path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    urls = os.getenv(
        "RAG_SOURCE_URLS",
        ";".join(
            [
                "https://www.getnet.net/en",
                "https://www.getnet.net/en/our-solutions/online-payments",
                "https://site.getnet.com.br/pix/",
                "https://site.getnet.com.br/link-de-pagamento/",
                "https://site.getnet.com.br/conta-digital/",
            ]
        ),
    )
    return Settings(
        app_name=os.getenv("APP_NAME", "AI Hardcore Engineer - Multi-Agent Support System"),
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        llm_provider=os.getenv("LLM_PROVIDER", "disabled").lower(),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
        ollama_chat_model=os.getenv("OLLAMA_CHAT_MODEL", "llama3.2:3b"),
        ollama_embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        request_timeout_s=_as_float(os.getenv("REQUEST_TIMEOUT_S"), 12.0),
        router_min_confidence=_as_float(os.getenv("ROUTER_MIN_CONFIDENCE"), 0.55),
        rag_top_k=_as_int(os.getenv("RAG_TOP_K"), 4),
        rag_min_score=_as_float(os.getenv("RAG_MIN_SCORE"), 0.12),
        rag_source_urls=tuple(u.strip() for u in urls.split(";") if u.strip()),
        web_search_max_results=_as_int(os.getenv("WEB_SEARCH_MAX_RESULTS"), 3),
        web_search_enabled=_as_bool(os.getenv("WEB_SEARCH_ENABLED"), True),
        data_dir=Path(os.getenv("DATA_DIR", str(BASE_DIR / "data"))),
        index_dir=Path(os.getenv("INDEX_DIR", str(BASE_DIR / "data" / "vector_store"))),
    )
