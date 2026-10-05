from __future__ import annotations

import re


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or " ").strip()
    return text


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 140) -> list[str]:
    text = clean_text(text)
    if not text:
        return []
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        if end < len(text):
            boundary = max(text.rfind(". ", start, end), text.rfind("; ", start, end))
            if boundary > start + chunk_size // 2:
                end = boundary + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks
