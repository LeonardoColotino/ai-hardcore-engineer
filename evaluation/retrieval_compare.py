"""Exact-chunk ranking experiment. Synthetic relevance, not factual validation.
Run: python -m evaluation.retrieval_compare --output evidence/current/retrieval.json
Default does NOT call Ollama; --ollama is an explicit local provider experiment.
"""
import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from app.rag.retriever import Retriever
from app.rag.vector_store import NumpyVectorStore
from app.services.embeddings import HashingEmbeddingService, OllamaEmbeddingService


def evaluate(use_ollama=False):
    path=Path(__file__).parent/'fixtures/retrieval_synthetic_v1.json'
    data=json.loads(path.read_text()); embeddings=HashingEmbeddingService()
    if use_ollama:
        from app.config import get_settings
        s=get_settings();embeddings=OllamaEmbeddingService(s.ollama_base_url,s.ollama_embed_model,s.request_timeout_s)
    result={'fixture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'corpus_kind':data['kind'],'queries':len(data['queries']),'k':3,'embedding_provider':'ollama' if use_ollama else 'hashing','embedding_model':getattr(embeddings,'model','hashing-384'),'factual_quality':'not_measured','learned_reranker':'not_enabled_no_measured_benefit','profiles':{}}
    previous=os.environ.get('RAG_RETRIEVAL_PROFILE')
    try:
        with tempfile.TemporaryDirectory() as directory:
            store=NumpyVectorStore(Path(directory));store.build(embeddings.embed([d['text'] for d in data['documents']]),data['documents'])
            for profile in ('vector','lexical','hybrid'):
                os.environ['RAG_RETRIEVAL_PROFILE']=profile;rows=[]
                for case in data['queries']:
                    hits=Retriever(store,embeddings,3,-1).retrieve(case['query']).hits
                    ids=[f"{h.metadata['document_id']}:{h.metadata['chunk_id']}" for h in hits]
                    relevant=set(case['relevant']);ranks=[i+1 for i,key in enumerate(ids) if key in relevant]
                    ideal=sum(1/math.log2(i+2) for i in range(min(3,len(relevant))))
                    rows.append({'query':case['query'],'retrieved_chunk_ids':ids,'relevant_chunk_ids':case['relevant'],'recall_at_3':len(set(ids)&relevant)/len(relevant),'reciprocal_rank':1/min(ranks) if ranks else 0,'ndcg_at_3':sum(1/math.log2(r+1) for r in ranks)/ideal})
                result['profiles'][profile]={'recall_at_3':sum(x['recall_at_3'] for x in rows)/len(rows),'mrr':sum(x['reciprocal_rank'] for x in rows)/len(rows),'ndcg_at_3':sum(x['ndcg_at_3'] for x in rows)/len(rows),'cases':rows}
    finally:
        if previous is None:os.environ.pop('RAG_RETRIEVAL_PROFILE',None)
        else:os.environ['RAG_RETRIEVAL_PROFILE']=previous
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ollama',action='store_true');parser.add_argument('--output',default='evidence/current/retrieval_comparison.json');args=parser.parse_args()
    report=evaluate(args.ollama);target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({p:{k:v for k,v in x.items() if k!='cases'} for p,x in report['profiles'].items()},indent=2))
