"""Reproducible runtime identity, without secrets or absolute paths."""
import hashlib
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1)
def source_digest():
    root=Path(__file__).resolve().parent
    digest=hashlib.sha256()
    for p in sorted(root.rglob('*')):
        if p.is_file() and (p.suffix=='.py' or p.name=='index.html'):
            digest.update(p.relative_to(root).as_posix().encode()+b'\0'+p.read_bytes())
    return digest.hexdigest()

def runtime_identity(settings):
    manifest=settings.index_dir/'manifest.json'
    return {'release':'getnet-v4-consolidado-2026-10-15','source_sha256':source_digest(),
            'corpus_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest.exists() else None,
            'chat_model':settings.ollama_chat_model if settings.llm_provider == 'ollama' else __import__('os').getenv('LLM_MODEL', __import__('os').getenv('GGUF_MODEL_PATH', 'disabled')),'embedding_model':settings.ollama_embed_model,
            'inference_verified':False}
