"""Page-level regression over inherited official snapshots; no inference or web.

Labels are translated from the older exposed chunk dataset to page URLs.
This checks page retrieval, not exact evidence, answer quality, or new holdout.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from app.config import get_settings
from app.dependencies import get_orchestrator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reranker', choices=['none', 'lexical', 'cross_encoder'], default='none')
    parser.add_argument('--output', default='evidence/current/snapshot-page-retrieval.json')
    args = parser.parse_args()
    os.environ['RERANKER'] = args.reranker
    root = Path(__file__).resolve().parent
    label_file = root / 'gold_v4_historical.json'
    old_docs = json.loads((root / 'historical_v4_index/documents.json').read_text())
    url_by_id = {str(d['metadata']['document_id']) + ':' + str(d['metadata']['chunk_id']): d['metadata']['url'] for d in old_docs}
    cases = json.loads(label_file.read_text())
    orch = get_orchestrator()
    retriever = orch.knowledge.rag.retriever
    rows = []
    for case in cases:
        expected = {url_by_id[i] for i in case['relevant_chunk_ids']}
        hits = retriever.retrieve(case['message']).hits
        urls = [h.metadata.get('url') for h in hits]
        ranks = [i+1 for i, url in enumerate(urls) if url in expected]
        rows.append({'id': case['id'], 'query': case['message'], 'expected_urls': sorted(expected), 'retrieved_urls': urls,
                     'recall_at_k_pages': len(set(urls) & expected) / len(expected), 'reciprocal_rank': 1/min(ranks) if ranks else 0})
    manifest = get_settings().index_dir / 'manifest.json'
    report = {'category': 'exposed_page_retrieval_regression', 'label_sha256': hashlib.sha256(label_file.read_bytes()).hexdigest(),
              'corpus_manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(), 'profile': os.getenv('RAG_RETRIEVAL_PROFILE', 'hybrid'),
              'reranker': args.reranker, 'cases': len(rows), 'k': retriever.top_k,
              'mean_recall_pages': sum(x['recall_at_k_pages'] for x in rows)/len(rows),
              'mrr_pages': sum(x['reciprocal_rank'] for x in rows)/len(rows), 'rows': rows,
              'limitations': 'Previously exposed questions and page labels; no exact-span relevance, new holdout, factuality, live freshness or neural embedding quality proven.'}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
