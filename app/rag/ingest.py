from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
import logging
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

from app.config import get_settings
from app.observability.logging import configure_logging, log_event
from app.services.embeddings import HashingEmbeddingService, OllamaEmbeddingService
from app.rag.chunking import chunk_text, clean_text
from app.rag.vector_store import NumpyVectorStore

logger = logging.getLogger(__name__)


def fetch_page(url: str, timeout: float) -> tuple[str, str]:
    headers = {"User-Agent": "AI-Hardcore-Engineer-Challenge/3.0"}
    response = requests.get(url, timeout=timeout, headers=headers)
    response.raise_for_status()

    # Parse os bytes para respeitar a codificação declarada no HTML.
    soup = BeautifulSoup(response.content, "html.parser")
    title = clean_text(
        soup.title.get_text(" ", strip=True)
        if soup.title else urlparse(url).netloc
    )

    # Remova componentes de interface, preservando o conteúdo dos produtos.
    selectors = (
        "script, style, noscript, svg, header, footer, nav, "
        "form, dialog, button, "
        "[role='navigation'], [role='dialog'], [role='banner'], "
        "[role='contentinfo']"
    )
    for tag in list(soup.select(selectors)):
        if tag.parent is not None:
            tag.decompose()

    main = soup.select_one("main, [role='main'], #main, .site-main")
    root = main if main is not None else soup.body
    if root is None:
        root = soup

    # Preserve real heading boundaries for section-scoped chunks.
    for heading in root.find_all(['h1','h2','h3','h4','h5','h6']):
        heading_text = clean_text(heading.get_text(' '))
        heading.clear()
        heading.append('[SEÇÃO] ' + heading_text)
    # Every visible text node is retained, including DIV/SPAN descriptions.
    for tag in root.find_all(['h1','h2','h3','h4','h5','h6','p','li','div','section','article','br']):
        tag.insert_before("\n")
        tag.insert_after("\n")
    lines = [clean_text(line) for line in root.get_text(" ",strip=False).splitlines()]
    blocks = []
    for line in lines:
        if line and (not blocks or blocks[-1] != line):
            blocks.append(line)
    text = "\n".join(blocks)
    if not text:
        raise ValueError(f"Página sem conteúdo após limpeza: {url}")

    return title, text


def seed_documents() -> list[dict]:
    """Small offline corpus used only if --seed is explicitly requested."""
    seeds = [
        {
            "title": "Getnet online payments",
            "url": "https://www.getnet.net/en/our-solutions/online-payments",
            "text": "Getnet offers online payment solutions including payment links that can be shared through WhatsApp, SMS or social networks, and checkout solutions for ecommerce.",
        },
        {
            "title": "Getnet Pix and account",
            "url": "https://site.getnet.com.br/conta-digital/",
            "text": "Getnet digital account features include Pix transfers and receipts, QR Code payments, and receivables advance options for eligible customers.",
        },
        {
            "title": "Getnet card machines (offline demonstration)",
            "url": "https://site.getnet.com.br/",
            "text": "Getnet card machines include products such as Get Clássica and Get Smart. They support contactless payments, Pix and QR Code; connectivity varies by model and can include Wi-Fi and mobile data.",
        },
        {
            "title": "Getnet installment sales",
            "url": "https://site.getnet.com.br/ofertas/",
            "text": "Getnet solutions support credit sales in installments and offer options such as crediário depending on the contracted product and commercial conditions.",
        },
    ]
    docs = []
    for i, item in enumerate(seeds):
        docs.append({
            "text": item["text"],
            "metadata": {
                "title": item["title"],
                "url": item["url"],
                "source": "offline-seed",
                "document_id": f"seed-{i}",
                "chunk_id": 0,
            },
        })
    return docs


def section_chunks(text: str, title: str):
    """Keep a tutorial and its action subheadings in one source context."""
    import re
    from app.orchestration.intents import normalized
    section,lines=title,[]
    tutorial=False
    def emit():
        for chunk in chunk_text('\n'.join(lines)):
            yield section,chunk
    for line in text.splitlines():
        if line.startswith('[SEÇÃO] '):
            heading=line[len('[SEÇÃO] '):].strip() or title
            h=normalized(heading)
            child_action=bool(re.search(r'^(?:\d+[ .-]*)?(?:acesse|crie|configure|pronto para|compartilh|acessar|criar|configurar)',h))
            if tutorial and child_action:
                lines.append(heading)
                continue
            if lines:
                yield from emit()
            section=heading;lines=[heading]
            tutorial=bool(re.search(r'veja como|passo a passo|tutorial|como.*(?:criar|vender)',h))
        else:
            lines.append(line)
    if lines:
        yield from emit()


def ingest(use_seed: bool = False, use_ollama_embeddings: bool = False) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    docs: list[dict] = []
    if use_seed:
        docs = seed_documents()
    else:
        for url in settings.rag_source_urls:
            try:
                title, text = fetch_page(url, settings.request_timeout_s)
                doc_id = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
                for chunk_id, (section, chunk) in enumerate(section_chunks(text, title)):
                    docs.append({
                        "text": chunk,
                        "metadata": {
                            "title": title,
                            "url": url,
                            "source": "getnet-web",
                            "fetched_at":datetime.now(timezone.utc).isoformat(),
                            "section":section,
                            "product":urlparse(url).path.rstrip("/").split("/")[-1],
                            "document_id": doc_id,
                            "chunk_id": chunk_id,
                        },
                    })
                log_event(logger, "rag_source_ingested", url=url, chunks=sum(1 for d in docs if d["metadata"].get("url") == url))
            except Exception as exc:
                log_event(logger, "rag_source_failed", url=url, error=str(exc))
    docs = list({hashlib.sha256(d['text'].encode()).hexdigest(): d for d in docs}.values())
    if not docs:
        raise RuntimeError("No documents were ingested")

    if use_ollama_embeddings:
        embeddings = OllamaEmbeddingService(settings.ollama_base_url, settings.ollama_embed_model, settings.request_timeout_s)
    else:
        embeddings = HashingEmbeddingService()
    vectors = embeddings.embed([d["text"] for d in docs])
    store = NumpyVectorStore(settings.index_dir)
    store.build(vectors, docs)
    (settings.index_dir / "embedding_provider.txt").write_text("ollama" if use_ollama_embeddings else "hashing", encoding="utf-8")
    manifest_path = settings.index_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(embedding_provider="ollama" if use_ollama_embeddings else "hashing",embedding_model=settings.ollama_embed_model if use_ollama_embeddings else "hashing-384",source_urls=list(settings.rag_source_urls) if not use_seed else [])
    manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    log_event(logger, "rag_index_built", documents=len(docs), index_dir=str(settings.index_dir), embedding_provider=type(embeddings).__name__)
    print(f"RAG index created with {len(docs)} chunks at {settings.index_dir}")
    return len(docs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Getnet sources into the local vector store")
    parser.add_argument("--seed", action="store_true", help="Build an offline demo index instead of fetching websites")
    parser.add_argument("--ollama-embeddings", action="store_true", help="Use Ollama embeddings instead of deterministic local hashing")
    args = parser.parse_args()
    ingest(use_seed=args.seed, use_ollama_embeddings=args.ollama_embeddings)


if __name__ == "__main__":
    main()
