"""Official challenge network scenario: ads must never count as guidance."""
import json
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from app.agents.knowledge import KnowledgeAgent
from app.agents.base import AgentResult
from app.models.tools import ToolResult, SourceItem
from app.models.plan import Plan, Task
from app.rag.evidence_selection import promotional, candidates_from_contexts, select_evidence
from app.rag.technical_guidance import network_guidance_query
from app.orchestration.planner import execute_plan

QUESTION="My card machine won't connect to the internet, what should I do?"
DEPENDENCY='Getnet maquininha: conexão Wi-Fi indisponível. Orientação oficial de solução do problema.'
ADVERTISEMENT='Adquira agora e venda mais!'
FACT='A maquininha tem conexão Wi-Fi e aceita pagamentos.'
ACTION='Verifique se a maquininha está conectada à rede Wi-Fi.'
ACTION2='Reinicie o roteador se a conexão de internet estiver indisponível.'

@pytest.mark.parametrize('query',[QUESTION,DEPENDENCY,'Minha maquininha não conecta à internet. O que fazer?'])
def test_original_and_public_dependency_are_network_guidance(query):
    assert network_guidance_query(query)

@pytest.mark.parametrize('text',[ADVERTISEMENT,'Compre sua maquininha agora!','Confira nossas ofertas de maquininhas!'])
def test_commercial_ctas_are_not_guidance(text):
    assert promotional(text)
    assert not candidates_from_contexts([text],question=DEPENDENCY)


def test_ads_and_connectivity_specs_do_not_call_selector():
    llm=Mock()
    answer,meta=select_evidence(llm,DEPENDENCY,[FACT+'\n'+ADVERTISEMENT])
    assert meta['abstained'] and meta['evidence_gap']=='technical_guidance_missing'
    assert ADVERTISEMENT not in answer
    llm.generate.assert_not_called()


def tool(text):
    r=ToolResult(success=True,data={'contexts':[text]},sources=[SourceItem(title='Manual máquinas',url='https://site.getnet.com.br/boas-vindas/manual-maquinas/',snippet=text)])
    return SimpleNamespace(name='rag_search',run=lambda q:r)

@pytest.mark.parametrize('enabled',[False,True])
def test_knowledge_cannot_publish_advertisement_in_any_mode(enabled):
    llm=Mock()
    result=KnowledgeAgent(tool(FACT+'\n'+ADVERTISEMENT),None,llm,enabled).handle(DEPENDENCY)
    assert result.escalated and result.metadata['evidence_gap']=='technical_guidance_missing'
    assert ADVERTISEMENT not in result.answer
    llm.generate.assert_not_called()


def test_actual_action_spans_survive_and_promotions_do_not():
    text=ACTION+'\n'+ADVERTISEMENT+'\n'+ACTION2
    candidates=candidates_from_contexts([text],question=DEPENDENCY)
    assert {x['text'] for x in candidates}=={ACTION,ACTION2}
    llm=Mock();llm.generate.return_value=json.dumps({'ids':[x['id'] for x in candidates]})
    answer,meta=select_evidence(llm,DEPENDENCY,[text])
    assert not meta.get('abstained') and ACTION in answer and ADVERTISEMENT not in answer


def test_disabled_model_fallback_keeps_only_documented_actions():
    result=KnowledgeAgent(tool(ACTION+'\n'+ADVERTISEMENT),None,None,False).handle(DEPENDENCY)
    assert not result.escalated and ACTION in result.answer and ADVERTISEMENT not in result.answer
    assert result.metadata['coverage']=='partial' and result.metadata['resolved'] is False


def test_device_overview_can_still_quote_connectivity_fact():
    candidates=candidates_from_contexts([FACT],question='Como funciona a maquininha Getnet?')
    assert [item['text'] for item in candidates]==[FACT]


def test_missing_technical_evidence_preserves_support_and_escalates(monkeypatch):
    monkeypatch.setattr('app.orchestration.planner.build_plan',lambda *a:(Plan(tasks=[Task(agent='support',query=QUESTION),Task(agent='knowledge',query='orientação',depends_on=0)]),'diagnostic_policy'))
    support=SimpleNamespace(handle=lambda *a:AgentResult('Diagnóstico demonstrativo: Wi-Fi indisponível.',tool='terminal_diagnosis',metadata={'public_diagnosis':DEPENDENCY}))
    class Knowledge:
        llm_enabled=False
        def handle(self,query):
            return KnowledgeAgent(tool(FACT+'\n'+ADVERTISEMENT),None,None,False).handle(query)
    result,agents,stages=execute_plan(QUESTION,'cliente1988',SimpleNamespace(router=None,support=support,knowledge=Knowledge()))
    assert result['escalated'] and 'Diagnóstico demonstrativo' in result['answer']
    assert 'Não encontrei orientações técnicas' in result['answer']
    assert ADVERTISEMENT not in result['answer']
    assert result['metadata']['coverage']=='partial'
    assert agents==['support','knowledge']
