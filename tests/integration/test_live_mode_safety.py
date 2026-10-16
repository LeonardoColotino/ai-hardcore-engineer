"""Replay captured real-provider failures; no live provider is called by this suite."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from app.agents.knowledge import KnowledgeAgent
from app.agents.base import AgentResult
from app.models.tools import SourceItem, ToolResult
from app.rag.evidence_records import EvidenceRecord, verified_attribution, unsupported_label_relation
from app.orchestration.planner import review_knowledge

ROWS=json.loads((Path(__file__).parents[1]/'fixtures/live_mode_failures.json').read_text())

def rag(row):
    records=row['records']
    result=ToolResult(success=True,data={'contexts':[r['text'] for r in records], 'chunks':[{'metadata':{'product':r['product'],'section':r['section']}} for r in records]},sources=[SourceItem(title=r['product'] or 'Getnet',url=r['url'],snippet=r['text']) for r in records])
    return SimpleNamespace(name='rag_search',run=lambda q: result)

class OverSelect:
    def generate_structured(self,system,message,schema):
        if 'TRECHOS:\n' not in message:
            raise AssertionError('Narrow quoted association must not require a generative exclusivity verdict')
        candidates=json.loads(message.split('TRECHOS:\n',1)[1])
        return json.dumps({'ids':[r['id'] for r in candidates if r['text'] in ['Cartão virtual grátis','Antecipação de recebíveis','Receba todos os pagamentos na mesma conta']][:3]})

@pytest.mark.parametrize('row',ROWS[:2])
def test_real_overselection_and_unrequested_exclusivity_are_contained(row):
    agent=KnowledgeAgent(rag(row),None,OverSelect(),True)
    result=agent.handle(row['question'])
    assert not result.escalated
    assert [x['text'] for x in result.metadata['selected_evidence']]==['Cartão virtual grátis']
    assert '**Conta Digital**: Cartão virtual grátis' in result.answer
    assert 'Antecipação' not in result.answer and 'pagamentos na mesma conta' not in result.answer
    reviewed=review_knowledge(row['question'],result,agent)
    assert not reviewed.escalated
    assert reviewed.metadata['evidence_review']['status']=='verified_source_attribution'
    assert 'Resposta parcial' not in reviewed.answer
    assert 'Isso não demonstra' in reviewed.answer

@pytest.mark.parametrize('row',ROWS)
def test_all_captured_wrong_prose_answers_are_withheld(row):
    class Prose:
        def generate(self,*args): return row['prose']
    agent=KnowledgeAgent(rag(row),None,Prose(),True,answer_mode='prose')
    result=agent.handle(row['question'])
    assert result.escalated and result.metadata['abstained']
    assert result.answer != row['prose']
    assert result.metadata['fallback'] in {'generated_abstention_withheld','unsupported_feature_relation'}
    assert 'há um cartão virtual grátis oferecido pelo Link' not in result.answer
    assert 'Cartão virtual grátis: permite receber' not in result.answer


def test_exclusivity_remains_a_semantic_question():
    agent=KnowledgeAgent(rag(ROWS[0]),None,OverSelect(),True)
    result=agent.handle('O cartão virtual grátis é exclusivo da Conta Digital ou do Link de Pagamento?')
    assert not verified_attribution('O cartão virtual grátis é exclusivo da Conta Digital ou do Link de Pagamento?',result)

@pytest.mark.parametrize('tamper',['answer','product','source_id'])
def test_attribution_shortcut_rejects_forged_lineage(tamper):
    question=ROWS[0]['question']
    agent=KnowledgeAgent(rag(ROWS[0]),None,OverSelect(),True)
    result=agent.handle(question)
    if tamper=='answer': result.answer+=' O outro produto não oferece o recurso.'
    else: result.metadata['selected_evidence'][0][tamper]='invented'
    assert not verified_attribution(question,result)


def test_exact_source_relation_is_not_rejected_as_conflation():
    text='Recurso exemplo: permite receber pagamentos na mesma conta.'
    record=EvidenceRecord(text=text,product='Conta Digital',section='Conta Digital',source_id='test',url='https://site.getnet.com.br/conta-digital/',source_index=0)
    assert not unsupported_label_relation(text,[record],'Quais funcionalidades da Conta Digital?')


def test_focus_rule_is_not_specific_to_virtual_cards():
    class SelectBoth:
        def generate_structured(self,system,message,schema):
            candidates=json.loads(message.split('TRECHOS:\n',1)[1])
            return json.dumps({'ids':[r['id'] for r in candidates][:3]})
    from tests.integration.test_product_attribution import tool
    agent=KnowledgeAgent(tool(['Receba todos os pagamentos na mesma conta','Personalize o link com a imagem do produto.']),None,SelectBoth(),True)
    result=agent.handle('A imagem do produto é recurso da Conta Digital ou do Link de Pagamento?')
    assert len(result.metadata['selected_evidence'])==1
    assert result.metadata['selected_evidence'][0]['product']=='Link de Pagamento'
