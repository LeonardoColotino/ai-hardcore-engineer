from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from app.dependencies import get_orchestrator
from app.config import get_settings
from app.rag.vector_store import NumpyVectorStore
from app.models.api import ChatRequest
from app.security import identity,customer,login
from app.persistence import Store
import hashlib, json, logging, re, threading, time, uuid
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
    idempotency_key:str|None=Field(default=None,min_length=8,max_length=100,pattern=r'^[A-Za-z0-9_-]+$')
class Reply(BaseModel):
    status:str
    reply:str=Field(default='',max_length=4000)

@router.get('/health')
def health():
    s=get_settings()
    from app.release import runtime_identity
    return {'status':'ok','llm_provider':s.llm_provider,'rag_index_ready':NumpyVectorStore(s.index_dir).ready,**runtime_identity(s)}
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
    if s.llm_provider in ('openai_compatible', 'openai-compatible'):
        import requests, os
        try:
            base = os.getenv('LLM_BASE_URL', 'http://localhost:1234/v1').rstrip('/')
            key = os.getenv('LLM_API_KEY', '')
            response = requests.get(base + '/models', headers={'Authorization': 'Bearer ' + key} if key else {}, timeout=2)
            response.raise_for_status()
            model = os.getenv('LLM_MODEL', 'gpt-4.1-mini')
            checks['llm'] = any(item.get('id') == model for item in response.json().get('data', []))
            if not checks['llm']: issues.append('Configured compatible model not listed')
        except (requests.RequestException, ValueError, TypeError):
            issues.append('Compatible provider unavailable; this is not an inference test')
    elif s.llm_provider == 'llama_cpp':
        from pathlib import Path
        import os, importlib.util
        checks['llm'] = Path(os.getenv('GGUF_MODEL_PATH', '__missing__')).is_file() and importlib.util.find_spec('llama_cpp') is not None
        if not checks['llm']: issues.append('GGUF file or optional package missing')
    elif s.llm_provider not in ('disabled', 'ollama'):
        issues.append('Unknown LLM_PROVIDER')
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
    if payload.user_id is not None and payload.user_id != who['sub']:
        raise HTTPException(403,'Identidade incompatível')
    store=Store()
    if payload.session_id: store.check(payload.session_id,who['sub'])
    if payload.idempotency_key:
        fingerprint=hashlib.sha256(json.dumps({'message':payload.message,'session':payload.session_id},sort_keys=True).encode()).hexdigest()
        cached=store.reserve_request(who['sub'],payload.idempotency_key,fingerprint)
        if cached is not None: return cached
    result=Supervisor().handle(payload,who,orch)
    store.save_trace(result['request_id'],result['session_id'],who['sub'],result['metadata'])
    if payload.idempotency_key: store.finish_request(who['sub'],payload.idempotency_key,result)
    return result

@router.get('/traces/{request_id}')
def trace(request_id:str,who=Depends(identity)):
    return Store().trace(request_id,who)

class Feedback(BaseModel):
    rating:int=Field(ge=-1,le=1)

@router.post('/feedback/{request_id}')
def feedback(request_id:str,payload:Feedback,who=Depends(customer)):
    return Store().record_feedback(request_id,who['sub'],payload.rating)


@router.get('/tickets/{tid}/messages')
def ticket_messages(tid:str,who=Depends(identity)):
    store=Store()
    row=store.get_ticket(tid,who)
    if who['role'] not in ('operator','admin'): raise HTTPException(403,'Somente operador')
    return store.messages(row['session'],row['owner'])
