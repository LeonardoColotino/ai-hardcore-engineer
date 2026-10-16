"""QA requirements fixed before implementation; no live quality assertions."""
import pytest
from unittest.mock import Mock
from dataclasses import replace
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_orchestrator
from app.config import get_settings
from app.agents.router import RouterAgent
from app.models.routing import AgentName
from app.models.tools import ToolResult, SourceItem
from app.services.llm import DisabledLLMClient
from evaluation.run import build_orchestrator

@pytest.fixture
def client(tmp_path, api_auth):
    orch = build_orchestrator(tmp_path / 'idx')
    app.dependency_overrides[get_orchestrator] = lambda: orch
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def send(c, h, text, sid=None):
    return c.post('/chat', headers=h, json={'message': text, 'session_id': sid}).json()

@pytest.mark.parametrize('text', ['Gostaria de aderir ao Link de Pagamento', 'Quero falar com um atendente humano', 'Quais taxas do Link de Pagamento?'])
def test_clear_policy_overrides_misleading_llm(text):
    llm = Mock(); llm.generate.return_value = '{"agent":"support","confidence":0.99,"reason":"Getnet garante aprovação"}'
    router = RouterAgent(replace(get_settings(), llm_provider='ollama'), llm)
    result = router.route(text)
    expected = AgentName.ESCALATION if 'humano' in text else AgentName.KNOWLEDGE
    assert result.agent == expected
    assert 'garante' not in result.reason


def test_persisted_handoff_metadata_truth(client, api_auth):
    h = api_auth('cliente1988')
    r = send(client, h, 'Quero atendimento humano')
    ticket = client.get('/tickets/' + r['ticket_id'], headers=h).json()
    assert ticket['status'] == 'OPEN'
    assert r['metadata']['ticket_created'] is True
    assert r['metadata']['handoff_status'] == 'OPEN'
    assert 'does not create' not in r['answer']
    assert r['metadata']['agents'] == ['escalation']
    assert r['metadata']['stages'][0]['tool'] == 'human_handoff'


def test_knowledge_failure_stage_tool_is_not_handoff(client, api_auth):
    orch = app.dependency_overrides[get_orchestrator]()
    orch.knowledge.web.run = Mock(return_value=ToolResult(success=False, error='unavailable'))
    r = send(client, api_auth('cliente1988'), 'Qual é a cotação do euro hoje?')
    assert r['escalated']
    assert r['metadata']['stages'][0]['agent'] == 'knowledge'
    assert r['metadata']['stages'][0]['tool'] == 'web_search'
    assert r['metadata']['stages'][-1]['agent'] == 'escalation'


def test_high_score_wrong_product_not_resolution(client, api_auth):
    orch = app.dependency_overrides[get_orchestrator]()
    orch.knowledge.rag.run = Mock(return_value=ToolResult(success=True, data={'contexts':['Conta Digital: cartão virtual grátis e antecipação.']}, sources=[SourceItem(title='Conta Digital',url='https://site.getnet.com.br/conta-digital/',snippet='Conta Digital: cartão virtual grátis e antecipação.',score=.99)]))
    orch.knowledge.web.run = Mock(return_value=ToolResult(success=False,error='unavailable'))
    r = send(client, api_auth('cliente1988'), 'Minha maquininha não conecta à internet')
    assert r['escalated'] and r['ticket_id']
    assert r['metadata'].get('resolved') is not True


def test_memory_paraphrase_after_intermediate_message(client, api_auth):
    h = api_auth('cliente1988')
    r = send(client,h,'Como funciona o Link de Pagamento Getnet?')
    sid = r['session_id']
    send(client,h,'Obrigado',sid)
    r = send(client,h,'E para aderir a ele?',sid)
    assert r['metadata']['products'] == ['Link de Pagamento']
    assert r['agent'] == 'knowledge' or (r['escalated'] and r['metadata'].get('previous_agent') == 'knowledge')
    assert r['tool'] not in ('payment_status','customer_lookup','transaction_lookup')


def test_trace_context_reset_after_unhandled_tool_failure(client, api_auth):
    from app.observability.logging import trace_context
    orch = app.dependency_overrides[get_orchestrator]()
    orch.support.handle = Mock(side_effect=RuntimeError('synthetic failure'))
    from app.orchestration.supervisor import Supervisor
    from app.api.routes import Chat
    before = trace_context.get()
    result = Supervisor().handle(Chat(message='Minhas vendas não caíram'), {'sub':'cliente1988','role':'customer'}, orch)
    assert result['escalated'] and result['ticket_id']
    assert result['metadata']['task_outcomes'][0]['status'] == 'failed'
    assert trace_context.get() == before


def test_new_conversation_does_not_inherit_product(client, api_auth):
    h = api_auth('cliente1988')
    first = send(client,h,'Como funciona o Link de Pagamento Getnet?')
    fresh = send(client,h,'E para aderir a ele?')
    assert fresh['session_id'] != first['session_id']
    assert fresh['metadata']['products'] == []
    assert fresh['metadata']['routing_reason'] == 'ambiguous_reference'


def test_corrected_entity_survives_persistence_reload(client, api_auth):
    from app.persistence import Store
    h = api_auth('cliente1988')
    first = send(client,h,'Como funciona o Link de Pagamento Getnet?')
    sid = first['session_id']
    send(client,h,'Eu quis dizer Pix Getnet',sid)
    saved = Store().state(sid,'cliente1988')
    assert saved['selected_product'] == 'Pix'
    assert saved['candidates'] == ['Pix']
    next_turn = send(client,h,'Como ele funciona?',sid)
    assert next_turn['metadata']['products'] == ['Pix']
    assert next_turn['tool'] not in ('payment_status','transaction_lookup')


@pytest.mark.parametrize('context',[
    'Taxas sujeitas a alteração de acordo com as condições dos produtos e serviços contratados. Veja como é fácil vender com o Link de Pagamento. Crie seu Link de Pagamento.',
    'Link de Pagamento: Quero contratar. Crie seu link no Portal Minha Conta.'
])
def test_disclaimer_or_cta_is_not_contracting_procedure(context):
    from app.agents.knowledge import KnowledgeAgent
    rag = Mock(); rag.name = 'rag_search'
    rag.run.return_value = ToolResult(success=True,data={'contexts':[context]},sources=[SourceItem(title='Link',url='https://site.getnet.com.br/link-de-pagamento/',snippet=context)])
    web = Mock(); web.name = 'web_search'; web.run.return_value = ToolResult(success=False,error='offline')
    llm = Mock(); llm.generate.return_value = 'Para contratar, crie um link no Portal.'
    result = KnowledgeAgent(rag,web,llm,llm_enabled=True).handle('Gostaria de aderir ao Link de Pagamento')
    assert result.escalated
    assert result.metadata['abstained'] is True
    assert result.metadata['fallback'] == 'signup_evidence_missing'
    llm.generate.assert_not_called()
