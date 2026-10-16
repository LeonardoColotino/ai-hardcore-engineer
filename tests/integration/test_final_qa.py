"""Independent QA cases frozen before changes; API/SQLite real, specialists simulated."""
from concurrent.futures import ThreadPoolExecutor
import sqlite3
from unittest.mock import Mock
import pytest
from app.agents.base import AgentResult
from app.persistence import Store
from tests.integration.test_audit_regressions import client, send


@pytest.mark.parametrize('message', [
    'Quando minhas vendas serão depositadas? Além disso, explique o Link de Pagamento.',
    'Explique o Link de Pagamento; também preciso saber quando minhas vendas serão depositadas.',
])
def test_mixed_failure_preserves_payment(client, api_auth, message):
    from app.dependencies import get_orchestrator
    from app.main import app
    orch=app.dependency_overrides[get_orchestrator]()
    orch.support.handle=Mock(return_value=AgentResult(answer='Dados demonstrativos: repasse R$ 314,15 previsto para 2030-01-02.',tool='payment_status'))
    orch.knowledge.handle=Mock(return_value=AgentResult(answer='Não há evidência disponível.',tool='rag_search',escalated=True,metadata={'fallback':'no_evidence'}))
    result=send(client,api_auth('cliente1988'),message)
    assert orch.support.handle.called and orch.knowledge.handle.called
    assert '314,15' in result['answer'] and '2030-01-02' in result['answer']
    assert result['escalated'] and result['ticket_id']
    assert '314,15' in Store().messages(result['session_id'],'cliente1988')[-1]['content']


def test_active_handoff_blocks_specialists_until_resolved(client,api_auth):
    from app.dependencies import get_orchestrator
    from app.main import app
    h=api_auth('cliente1988'); op=api_auth('operador')
    first=send(client,h,'Preciso falar com um operador humano')
    orch=app.dependency_overrides[get_orchestrator]()
    orch.support.handle=Mock(wraps=orch.support.handle)
    orch.knowledge.handle=Mock(wraps=orch.knowledge.handle)
    followup=send(client,h,'Minhas vendas foram depositadas?',first['session_id'])
    assert followup['ticket_id']==first['ticket_id']
    orch.support.handle.assert_not_called();orch.knowledge.handle.assert_not_called()
    tid=first['ticket_id']
    assert client.post('/tickets/'+tid+'/reply',headers=op,json={'status':'IN_PROGRESS'}).status_code==200
    assert client.post('/tickets/'+tid+'/reply',headers=op,json={'status':'RESOLVED','reply':'Pode retomar a consulta automatizada.'}).status_code==200
    send(client,h,'Minhas vendas foram depositadas?',first['session_id'])
    assert orch.support.handle.called


def test_concurrent_active_ticket_singleton(api_auth):
    store=Store();sid=store.session('cliente1988')['session_id']
    with ThreadPoolExecutor(max_workers=8) as pool:
        ids=list(pool.map(lambda _:Store().ticket(sid,'cliente1988','synthetic QA reason'),range(16)))
    assert len(set(ids))==1
    assert len(store.tickets({'sub':'cliente1988','role':'customer'}))==1


def test_resolution_rolls_back_if_history_write_fails(api_auth):
    store=Store();sid=store.session('cliente1988')['session_id']
    tid=store.ticket(sid,'cliente1988','synthetic rollback')
    op={'sub':'operador','role':'operator'}
    store.transition(tid,op,'IN_PROGRESS','')
    with store.db() as c:
        c.execute("CREATE TRIGGER fail_human BEFORE INSERT ON messages WHEN NEW.role='human' BEGIN SELECT RAISE(ABORT, 'synthetic disk failure'); END")
    with pytest.raises(sqlite3.IntegrityError):
        store.transition(tid,op,'RESOLVED','Resposta sintética')
    assert Store().get_ticket(tid,op)['status']=='IN_PROGRESS'
    assert Store().messages(sid,'cliente1988')==[]


def test_concurrent_resolution_never_duplicates_human_reply(api_auth):
    from fastapi import HTTPException
    store=Store();sid=store.session('cliente1988')['session_id'];tid=store.ticket(sid,'cliente1988','qa')
    op={'sub':'operador','role':'operator'};store.transition(tid,op,'IN_PROGRESS','')
    def resolve(_):
        try:return Store().transition(tid,op,'RESOLVED','Resposta única')['status']
        except HTTPException as exc:return exc.status_code
    with ThreadPoolExecutor(max_workers=2) as pool: outcomes=list(pool.map(resolve,range(2)))
    assert outcomes.count('RESOLVED')==1
    assert len([m for m in store.messages(sid,'cliente1988') if m['role']=='human'])==1


def test_ticket_and_history_owner_isolation_after_restart(api_auth):
    from fastapi import HTTPException
    store=Store();sid=store.session('cliente1988')['session_id'];tid=store.ticket(sid,'cliente1988','qa')
    store.add(sid,'user','private synthetic message')
    for action in [lambda:Store().messages(sid,'cliente2026'),lambda:Store().get_ticket(tid,{'sub':'cliente2026','role':'customer'})]:
        with pytest.raises(HTTPException) as exc:action()
        assert exc.value.status_code==404

@pytest.mark.parametrize('failed_position',[0,1,2])
def test_task_failure_at_any_position_preserves_other_outputs(monkeypatch,failed_position):
    from app.models.plan import Plan,Task
    from app.orchestration.planner import execute_plan
    plan=Plan(tasks=[Task(agent='support',query=f'task number {i}') for i in range(3)])
    monkeypatch.setattr('app.orchestration.planner.build_plan',lambda *a:(plan,'qa_forced'))
    orch=Mock()
    def handle(query,owner):
        assert owner=='trusted-identity'
        i=int(query[-1])
        if i==failed_position: raise TimeoutError('synthetic unavailable')
        return AgentResult(answer=f'Validated output {i}',tool='payment_status')
    orch.support.handle.side_effect=handle
    result,_,_=execute_plan('synthetic tasks','trusted-identity',orch)
    for i in range(3):
        if i!=failed_position: assert f'Validated output {i}' in result['answer']
    assert result['escalated'] and result['metadata']['coverage']=='partial'
    assert result['metadata']['task_outcomes'][failed_position]['status']=='failed'


@pytest.mark.parametrize('private_query',[
    'Pesquisar CPF 123.456.789-00',
    'cliente1988 pagamento R$ 314,15',
    'account_status active expected_date 2030-01-02',
    'Link de Pagamento joao@example.com',
    'token abcdef12345',
])
def test_private_query_blocked_before_search(private_query):
    from app.tools.web_search import WebSearchTool
    service=Mock();tool=WebSearchTool(service)
    result=tool.run(private_query)
    assert not result.success
    service.search.assert_not_called()


def test_api_idempotency_retry_and_conflict(client,api_auth):
    h=api_auth('cliente1988')
    payload={'message':'Quando minhas vendas serão depositadas?','idempotency_key':'qa-idempotency-001'}
    first=client.post('/chat',headers=h,json=payload)
    second=client.post('/chat',headers=h,json=payload)
    assert first.status_code==second.status_code==200
    assert first.json()==second.json()
    assert len(Store().messages(first.json()['session_id'],'cliente1988'))==2
    conflict=client.post('/chat',headers=h,json={**payload,'message':'Mensagem diferente'})
    assert conflict.status_code==409


def test_concurrent_idempotency_requests_one_turn(client,api_auth):
    h=api_auth('cliente1988');payload={'message':'Quando minhas vendas serão depositadas?','idempotency_key':'qa-concurrent-001'}
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:client.post('/chat',headers=h,json=payload),range(4)))
    assert all(r.status_code in (200,409) for r in results)
    successes=[r.json() for r in results if r.status_code==200]
    assert successes and len({r['request_id'] for r in successes})==1
    assert len(Store().messages(successes[0]['session_id'],'cliente1988'))==2


def test_trace_and_feedback_ownership(client,api_auth):
    h=api_auth('cliente1988');other=api_auth('cliente2026')
    response=send(client,h,'Quando minhas vendas serão depositadas?');rid=response['request_id']
    assert client.get('/traces/'+rid,headers=h).status_code==200
    assert client.get('/traces/'+rid,headers=other).status_code==404
    assert client.post('/feedback/'+rid,headers=other,json={'rating':1}).status_code==404
    assert client.post('/feedback/'+rid,headers=h,json={'rating':1}).status_code==200
    assert client.post('/feedback/'+rid,headers=h,json={'rating':99}).status_code==422
    trace=client.get('/traces/'+rid,headers=h).json()
    assert 'answer' not in trace and 'original_message' not in trace and 'trusted_user_id' not in trace
