from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from app.dependencies import get_orchestrator
from app.config import get_settings
from app.rag.vector_store import NumpyVectorStore
from app.models.api import ChatRequest
from app.security import identity,customer,login
from app.persistence import Store
import hashlib, logging, re, threading, time, uuid
from app.orchestration.supervisor import Supervisor, limit, metrics, rates, latency_samples, rate_lock
router=APIRouter()
class Login(BaseModel):
    username:str=Field(max_length=120)
    password:str=Field(max_length=200)
class Chat(BaseModel):
    model_config=ConfigDict(extra='forbid')
    message:str=Field(min_length=2,max_length=4000)
    session_id:str|None=Field(default=None,max_length=64)
    user_id:str|None=Field(default=None,max_length=120)
class Reply(BaseModel):
    status:str
    reply:str=Field(default='',max_length=4000)

@router.get('/health')
def health():
    s=get_settings()
    return {'status':'ok','llm_provider':s.llm_provider,'rag_index_ready':NumpyVectorStore(s.index_dir).ready}
@router.get('/ready')
def ready():
    s=get_settings()
    store=NumpyVectorStore(s.index_dir)
    checks={'index':False,'llm':s.llm_provider=='disabled'}
    issues=[]
    try:
        store.load()
        checks['index']=True
    except (OSError,ValueError,TypeError) as exc:
        issues.append('RAG index missing/corrupt; run ingestion')
    if s.llm_provider=='ollama':
        import requests
        try:
            r=requests.get(s.ollama_base_url+'/api/tags',timeout=2)
            r.raise_for_status()
            names={m.get('name') for m in r.json().get('models',[])}
            checks['llm']=s.ollama_chat_model in names
            if not checks['llm']: issues.append('Configured chat model missing')
        except (requests.RequestException,ValueError,TypeError):
            issues.append('Ollama unreachable or invalid response')
    from fastapi.responses import JSONResponse
    return JSONResponse({'status':'ready' if all(checks.values()) else 'not_ready','checks':checks,'issues':issues,'generation_enabled':s.llm_provider!='disabled'},status_code=200 if all(checks.values()) else 503)
@router.post('/auth/login')
def auth(payload:Login):
    # bounded, shared login bucket: demonstration only
    limit('login')
    return login(payload.username,payload.password)
@router.post('/sessions')
def create(who=Depends(customer)): return Store().session(who['sub'])
@router.get('/sessions')
def sessions(who=Depends(customer)): return Store().sessions(who['sub'])
@router.get('/sessions/{sid}/messages')
def history(sid:str,who=Depends(customer)): return Store().messages(sid,who['sub'])
@router.get('/tickets')
def tickets(who=Depends(identity)): return Store().tickets(who)
@router.get('/tickets/{tid}')
def ticket(tid:str,who=Depends(identity)): return Store().get_ticket(tid,who)
@router.post('/tickets/{tid}/reply')
def reply(tid:str,payload:Reply,who=Depends(identity)): return Store().transition(tid,who,payload.status,payload.reply)
@router.get('/metrics')
def stats(who=Depends(identity)):
    if who['role'] not in ('operator','admin'): raise HTTPException(403,'Somente operador')
    n=metrics['requests']+metrics['errors']
    from app.observability.tools import failures
    import numpy as np
    with rate_lock:
        samples=list(latency_samples)
        snapshot=dict(metrics)
    completed=snapshot['requests']
    return {**snapshot,'tool_failures':dict(failures),'success_rate':(n-snapshot['errors'])/n if n else None,'mean_latency_ms':snapshot['duration_ms_total']/completed if completed else None,'p50_latency_ms':float(np.percentile(samples,50)) if samples else None,'p95_latency_ms':float(np.percentile(samples,95)) if samples else None,'latency_sample_count':len(samples),'latency_sample_limit':1000,'answered_rate':snapshot['answered']/completed if completed else None,'abstention_rate':snapshot['abstentions']/completed if completed else None,'fallback_rate':snapshot['fallbacks']/completed if completed else None,'escalation_rate':snapshot['escalations']/completed if completed else None,'quality_grounded_rate':None,'denominators':{'technical_success':n,'outcomes':completed,'latency':'last 1000 completed requests; per-process'},'quality_note':'Answered is a technical outcome; factual resolution/groundedness require live review.'}
@router.post('/chat')
def chat(payload:Chat,who=Depends(customer),orch=Depends(get_orchestrator)):
    return Supervisor().handle(payload,who,orch)
