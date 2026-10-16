"""Rebuild an offline index from inherited official snapshots, without network."""
import hashlib
import json
from pathlib import Path
from app.config import get_settings
from app.rag.ingest import section_chunks, validate_source_url
from app.rag.vector_store import NumpyVectorStore
from app.services.embeddings import HashingEmbeddingService


def main():
    settings = get_settings()
    snapshots = Path(__file__).resolve().parents[1] / 'app/data/source_snapshots'
    docs = []
    origins = []
    for path in sorted(snapshots.glob('*.json')):
        item = json.loads(path.read_text(encoding='utf-8'))
        validate_source_url(item['url'])
        origins.append({'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'url': item['url'], 'fetched_at': item.get('fetched_at')})
        for chunk_id, (section, text) in enumerate(section_chunks(item['text'], item['title'])):
            docs.append({'text': text, 'metadata': {'title': item['title'], 'url': item['url'], 'section': section,
                        'source': 'inherited-official-snapshot', 'fetched_at': item.get('fetched_at'),
                        'document_id': hashlib.sha1(item['url'].encode()).hexdigest()[:12], 'chunk_id': chunk_id}})
    if not docs:
        raise SystemExit('No source snapshots supplied')
    embeddings = HashingEmbeddingService()
    store = NumpyVectorStore(settings.index_dir)
    store.build(embeddings.embed([d['text'] for d in docs]), docs)
    (settings.index_dir / 'embedding_provider.txt').write_text('hashing', encoding='utf-8')
    path = settings.index_dir / 'manifest.json'
    manifest = json.loads(path.read_text())
    manifest.update(embedding_provider='hashing', embedding_model='hashing-384', corpus_kind='inherited_official_snapshot', sources=origins,
                    limitations='Historical documentary snapshots; not current live ingestion or neural embeddings.')
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'documents': len(docs), 'snapshot_files': len(origins), 'index_dir': str(settings.index_dir), 'corpus_sha256': manifest['corpus_sha256']}))


if __name__ == '__main__':
    main()
