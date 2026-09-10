"""
Retriever da base de conhecimento Getnet.

Responsabilidade:
buscar os chunks semanticamente mais relevantes
para uma pergunta.
"""

import json
import os

import faiss
import numpy as np

from app.config import settings
from app.rag.ingest import create_embedding


class Retriever:
    """Busca informações na base vetorial."""

    def __init__(self) -> None:

        self.index = None
        self.documents = []

    def load(self) -> None:
        """
        Carrega o índice FAISS e os documentos.
        """

        if not os.path.exists(
            settings.VECTOR_INDEX_PATH
        ):

            raise RuntimeError(
                "Índice FAISS não encontrado. "
                "Execute primeiro: "
                "python -m app.rag.ingest"
            )

        if not os.path.exists(
            settings.DOCUMENTS_PATH
        ):

            raise RuntimeError(
                "Arquivo de documentos não encontrado."
            )

        self.index = faiss.read_index(
            settings.VECTOR_INDEX_PATH
        )

        with open(
            settings.DOCUMENTS_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            self.documents = json.load(file)
    def search(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict]:
        """
        Busca os documentos mais próximos semanticamente.

        Args:
            query:
                Pergunta do usuário.

            top_k:
                Quantidade máxima de resultados.

        Returns:
            Lista dos documentos mais relevantes.
        """

        if self.index is None:
            self.load()

        embedding = create_embedding(
            query
        )

        vector = np.array(
            [embedding],
            dtype="float32"
        )

        faiss.normalize_L2(vector)

        scores, indexes = self.index.search(
            vector,
            top_k
        )

        results = []

        for score, document_index in zip(
            scores[0],
            indexes[0]
        ):

            if document_index == -1:
                continue

            document = self.documents[
                document_index
            ]

            results.append(
                {
                    "content": document["content"],
                    "source": document["source"],
                    "score": float(score)
                }
            )

        return results
retriever = Retriever()