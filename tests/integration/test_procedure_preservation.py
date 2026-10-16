"""Replay source context captured in the user's real Docker retrieval, no live model."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from app.agents.knowledge import KnowledgeAgent
from app.agents.base import AgentResult
from app.models.tools import SourceItem
from app.orchestration.planner import review_knowledge
from app.rag.answer_policy import procedure_excerpt

FIXTURE=json.loads((Path(__file__).parents[1]/'fixtures/live_procedure_context.json').read_text())
class NoGeneration:
    def generate(self, *args):
        raise AssertionError('A complete source procedure must not be replaced by generated fragments')
    def generate_structured(self, *args):
        raise AssertionError('A verified quotation must not need another model call')

def source():
    return SourceItem(title='Link de Pagamento', url=FIXTURE['url'], snippet=FIXTURE['text'])

@pytest.mark.parametrize('question', [
    'Como funciona o Link de Pagamento da Getnet?',
    'Como faço para criar o Link de Pagamento da Getnet?',
    'Como faço para criar esse link? [Contexto da conversa: Getnet Link de Pagamento]',
])
def test_real_retrieved_procedure_is_preserved_without_generation(question):
    knowledge=KnowledgeAgent(None, None, NoGeneration(), True)
    answer, metadata=knowledge._answer_from_context(question, [FIXTURE['text'], 'Aceite débito, crédito, Pix, Wallet e boleto'])
    assert metadata['generation_kind']=='procedure_evidence_extraction'
    assert all('\n'+str(i)+'\n' in answer for i in range(1,5))
    assert 'Criar Link de Pagamento' in answer and 'compartilhar ou copiar' in answer
    result=review_knowledge(question, AgentResult(answer, sources=[source()], metadata=metadata), knowledge)
    assert not result.escalated
    assert result.metadata['evidence_review']['status']=='verified_source_procedure'
    assert result.answer==answer and 'Resposta parcial' not in answer

@pytest.mark.parametrize('tamper', ['answer','source','missing_block'])
def test_tampered_procedure_does_not_bypass_review(tamper):
    question='Como criar o Link de Pagamento?'
    answer, metadata=procedure_excerpt(question,[FIXTURE['text']])
    sources=[source()]
    if tamper=='answer': answer+=' Taxa de 99 reais.'
    if tamper=='source': sources[0].snippet='Apenas anúncio, sem procedimento.'
    if tamper=='missing_block': metadata['evidence_excerpts']=[]
    result=review_knowledge(question,AgentResult(answer,sources=sources,metadata=metadata),SimpleNamespace(llm_enabled=True,llm=NoGeneration()))
    assert result.escalated and result.metadata['fallback']=='procedure_provenance_failed'


def test_signup_is_not_replaced_by_creation_tutorial():
    assert procedure_excerpt('Como contratar o Link de Pagamento?', [FIXTURE['text']]) is None


def test_incomplete_source_does_not_become_complete_procedure():
    text=FIXTURE['text'].split('4\n')[0]
    assert procedure_excerpt('Como criar o Link de Pagamento?', [text]) is None
