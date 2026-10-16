"""Regression contracts for live false rejections; provider responses are mocked."""
import json
from types import SimpleNamespace
import pytest
from app.agents.base import AgentResult
from app.models.tools import SourceItem
from app.models.plan import Plan, Task
from app.orchestration.planner import review_knowledge, execute_plan

class Client:
    def __init__(self, support='supported', coverage='incomplete', reason='Missing fees'):
        self.support, self.coverage, self.reason = support, coverage, reason
        self.payload = None
    def generate_structured(self, system, message, schema):
        self.payload = json.loads(message)
        return json.dumps(dict(support=self.support, coverage=self.coverage, reason=self.reason))

def result():
    text = 'O vendedor envia o link e o comprador escolhe o pagamento.'
    return AgentResult(text, sources=[SourceItem(title='Getnet', url='https://site.getnet.com.br/link-de-pagamento/', snippet='Resumo curto.')], metadata={'selected_evidence': [{'id': 0, 'source_index': 0, 'text': text}]})

@pytest.mark.parametrize('reason', ['Missing fees and deadlines', 'Missing generation or personalization steps'])
def test_supported_partial_retains_answer_without_handoff(reason):
    client = Client(reason=reason)
    r = review_knowledge('Como funciona o Link de Pagamento?', result(), SimpleNamespace(llm_enabled=True, llm=client))
    assert not r.escalated
    assert r.answer.startswith('O vendedor envia o link') and 'Resposta parcial' in r.answer
    assert r.metadata['resolved'] is False and r.metadata['outcome'] == 'partial'
    assert client.payload['evidence'][0]['text'].endswith('escolhe o pagamento.')
    assert client.payload['evidence'][0]['url'].endswith('/link-de-pagamento/')

@pytest.mark.parametrize('support,coverage', [('unsupported','complete'), ('uncertain','incomplete'), ('supported','conflict')])
def test_unsupported_or_conflicting_claims_still_escalate(support, coverage):
    r = review_knowledge('Como funciona Pix?', result(), SimpleNamespace(llm_enabled=True, llm=Client(support, coverage)))
    assert r.escalated and r.metadata['abstained']
    assert not r.answer.startswith('O vendedor envia')

def test_missing_support_field_is_not_silently_accepted():
    class LegacyClient:
        def generate_structured(self, *args):
            return '{"coverage":"complete","reason":"ok"}'
    r = review_knowledge('Como funciona Pix?', result(), SimpleNamespace(llm_enabled=True, llm=LegacyClient()))
    assert r.escalated and r.metadata['fallback'] == 'evidence_review_failed'

def test_empty_evidence_does_not_call_model():
    client = Client()
    r = review_knowledge('Como funciona Pix?', AgentResult('Pix'), SimpleNamespace(llm_enabled=True, llm=client))
    assert r.escalated and client.payload is None

def test_partial_stays_partial_in_final_assembly(monkeypatch):
    monkeypatch.setattr('app.orchestration.planner.build_plan', lambda *args: (Plan(tasks=[Task(agent='knowledge', query='Como funciona Pix?')]), 'test'))
    knowledge = SimpleNamespace(llm_enabled=True, llm=Client(), handle=lambda query: result())
    r, _, stages = execute_plan('Como funciona Pix?', 'cliente1988', SimpleNamespace(router=None, knowledge=knowledge))
    assert not r['escalated'] and r['metadata']['coverage'] == 'partial'
    assert r['metadata']['outcome'] == 'partial' and not r['metadata']['resolved']
    assert stages[0]['review'] == 'partial_answer_retained'
