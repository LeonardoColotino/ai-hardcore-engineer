"""
Configurações globais da aplicação.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configurações da aplicação."""

    APP_NAME: str = "AI Hardcore Engineer"
    APP_VERSION: str = "1.0.0"

    MODEL_NAME: str = os.getenv(
        "MODEL_NAME",
        "llama3.2:3b"
    )
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "nomic-embed-text"
    )

    OLLAMA_URL: str = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434"
    )

    DATABASE_NAME: str = os.getenv(
        "DATABASE_NAME",
        "app/data/support.db"
    )

    VECTOR_INDEX_PATH: str = os.getenv(
        "VECTOR_INDEX_PATH",
        "app/data/getnet_docs/index.faiss"
    )

    DOCUMENTS_PATH: str = os.getenv(
        "DOCUMENTS_PATH",
        "app/data/getnet_docs/documents.json"
    )

settings = Settings()