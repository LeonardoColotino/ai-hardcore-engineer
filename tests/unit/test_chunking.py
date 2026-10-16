import pytest
from app.rag.chunking import chunk_text, clean_text


def test_clean_text_compacts_whitespace():
    assert clean_text("a\n   b") == "a b"


def test_chunking_has_overlap_and_nonempty_chunks():
    chunks = chunk_text("word " * 1000, chunk_size=200, overlap=40)
    assert len(chunks) > 2
    assert all(c.strip() for c in chunks)


def test_invalid_chunk_config():
    with pytest.raises(ValueError):
        chunk_text("abc", 100, 100)
