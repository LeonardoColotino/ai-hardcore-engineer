from __future__ import annotations
import re


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or " ").strip()


def chunk_text(text: str, chunk_size: int = 1800, overlap: int = 140) -> list[str]:
    """Keep section/procedure blocks together; oversized blocks use word boundaries.

    A heading starts a new section, so unrelated product sections never overlap.
    Oversized sections carry their heading and an explicit continuation marker.
    """
    if chunk_size <= overlap or overlap < 0:
        raise ValueError("chunk_size must be greater than overlap")
    if not text.strip():
        return []
    sections = re.split(r"(?m)(?=^#{1,6} )", text)
    chunks = []
    for section in sections:
        lines = [clean_text(line) for line in section.splitlines() if line.strip()]
        if not lines:
            continue
        heading = lines[0] if lines[0].startswith('#') else ''
        prefix = heading + '\n[continuação da seção]\n' if heading else ''
        current = ''
        for block in lines:
            # Ordinary steps/rows stay intact. Bound a single pathological paragraph.
            while len(block) > chunk_size:
                boundary = block.rfind(' ', 0, chunk_size)
                boundary = boundary if boundary > chunk_size // 2 else chunk_size
                if current.strip():
                    chunks.append(current.strip())
                chunks.append((prefix + block[:boundary]).strip())
                block = block[max(1, boundary-overlap):].lstrip()
                current = ''
            if current and len(current) + len(block) + 1 > chunk_size:
                chunks.append(current.strip())
                current = prefix
            current += ('\n' if current else '') + block
        if current.strip():
            chunks.append(current.strip())
    return chunks
