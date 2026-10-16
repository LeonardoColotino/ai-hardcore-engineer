"""Optional local Ollama experiment: identical retrieved passages, different answer mode.

No automatic quality grade. Does not modify .env, corpus or customer conversations.
"""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import time
from app.config import get_settings
from app.dependencies import get_orchestrator
from app.rag.evidence_records import build_records
from app.rag.relevance import relevant
from app.services.public_query import public_query
from app.agents.base import AgentResult
from app.orchestration.planner import review_knowledge


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args=parser.parse_args()
    if get_settings().llm_provider != 'ollama':
        raise SystemExit('Este experimento requer LLM_PROVIDER=ollama; nenhuma chamada foi feita.')
    agent=get_orchestrator().knowledge
    questions=[
        'O cartão virtual grátis é da Conta Digital ou do Link de Pagamento?',
        'O Link de Pagamento ou a Conta Digital lista cartão virtual grátis?',
        'Quais funcionalidades a Conta Digital da Getnet oferece?',
    ]
    output=Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows=[]
    def save():
        temporary=output.with_suffix(output.suffix+'.tmp')
        temporary.write_text(json.dumps({'quality_status':'pending_human_review','same_retrieval_for_both_modes':True,'rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
        temporary.replace(output)
    for question in questions:
        query=public_query(question)
        retrieval=agent.rag.run(query)
        if not retrieval.success:
            rows.append({'question':query,'error':'retrieval_failed','detail':retrieval.error}); save(); continue
        original=retrieval.data.get('contexts',[])
        accepted=[i for i,text in enumerate(original) if i < len(retrieval.sources) and relevant(query,text,retrieval.sources[i].title,retrieval.sources[i].url)]
        sources=[retrieval.sources[i] for i in accepted]
        contexts=[original[i] for i in accepted]
        chunks=retrieval.data.get('chunks',[])
        records=build_records(contexts,sources,[chunks[i] if i < len(chunks) else {} for i in accepted])
        row={'question':query,'records':[r.model_dump() for r in records],'modes':[]}
        rows.append(row)
        for mode in ['evidence','prose']:
            candidate=replace(agent,answer_mode=mode)
            started=time.perf_counter()
            try:
                answer,metadata=candidate._answer_from_context(query,contexts,records=records)
                metadata['evidence_records']=[r.model_dump() for r in records]
                before=AgentResult(answer=answer,sources=sources,escalated=bool(metadata.get('abstained')),metadata=metadata)
                reviewed=review_knowledge(query,before,candidate)
                row['modes'].append({'mode':mode,'answer_before_review':answer,'answer_after_review':reviewed.answer,'escalated':reviewed.escalated,'metadata':reviewed.metadata,'duration_ms':round((time.perf_counter()-started)*1000,2)})
            except Exception as exc:
                row['modes'].append({'mode':mode,'error_type':type(exc).__name__})
            save()
    print('Captura salva; revisar atribuição, cobertura, idioma, fontes e latência manualmente.')

if __name__=='__main__':
    main()
