"""
Pipeline de ingestão da base de conhecimento da Getnet.

Responsabilidades:
- Baixar páginas da Getnet
- Extrair texto
- Dividir texto em chunks
- Criar embeddings
- Armazenar vetores no FAISS
"""

import json
import os

import faiss
import numpy as np
import requests
from bs4 import BeautifulSoup

from app.config import settings


GETNET_URLS = [
    "https://www.getnet.net/",
    "https://www.getnet.net/en",
]


def fetch_page(url: str) -> str:
    """
    Baixa uma página web e extrai seu conteúdo textual.
    """

    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Remove elementos que não ajudam no RAG.
    for element in soup(
        ["script", "style", "nav", "footer"]
    ):
        element.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return text
def split_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
) -> list[str]:
    """
    Divide um texto em pequenos blocos com sobreposição.
    """

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks
def create_embedding(text: str) -> list[float]:
    """
    Cria embedding utilizando o Ollama local.
    """

    url = f"{settings.OLLAMA_URL}/api/embed"

    payload = {
        "model": settings.EMBEDDING_MODEL,
        "input": text
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

    except requests.RequestException as exc:

        raise RuntimeError(
            "Erro ao gerar embedding com Ollama."
        ) from exc

    data = response.json()

    embeddings = data.get("embeddings")

    if not embeddings:
        raise RuntimeError(
            "O Ollama não retornou embeddings."
        )

    return embeddings[0]

def ingest():
    """
    Executa todo o pipeline de ingestão.
    """

    documents = []

    print("Iniciando ingestão...")

    for url in GETNET_URLS:

        print(f"Processando: {url}")

        try:

            text = fetch_page(url)

        except requests.RequestException as exc:

            print(
                f"Não foi possível acessar {url}: {exc}"
            )

            continue

        chunks = split_text(text)

        for chunk in chunks:

            documents.append(
                {
                    "source": url,
                    "content": chunk
                }
            )

    if not documents:
        raise RuntimeError(
            "Nenhum documento foi encontrado."
        )

    print(
        f"{len(documents)} chunks encontrados."
    )

    embeddings = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        print(
            f"Criando embedding "
            f"{index}/{len(documents)}"
        )

        embedding = create_embedding(
            document["content"]
        )

        embeddings.append(embedding)

    matrix = np.array(
        embeddings,
        dtype="float32"
    )

    # Normalização para busca por similaridade.
    faiss.normalize_L2(matrix)

    dimension = matrix.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(matrix)

    os.makedirs(
        os.path.dirname(
            settings.VECTOR_INDEX_PATH
        ),
        exist_ok=True
    )

    faiss.write_index(
        index,
        settings.VECTOR_INDEX_PATH
    )

    with open(
        settings.DOCUMENTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            documents,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("Ingestão concluída.")
if __name__ == "__main__":
    ingest()