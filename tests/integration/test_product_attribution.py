"""Source lineage and attribution contracts; model outputs are simulated."""
import json
from types import SimpleNamespace
import pytest
from app.agents.knowledge import KnowledgeAgent
from app.models.tools import SourceItem, ToolResult
from app.rag.evidence_records import build_records
from app.orchestration.planner import review_knowledge

class Select:
    def __init__(self, needle='Cartão virtual grátis'):
        self.needle=needle
        self.payload=None
    def generate_structured(self, system, message, schema):
        if 'TRECHOS:\n' in message:
            self.payload=json.loads(message.split('TRECHOS:\n',1)[1])
            return json.dumps({'ids':[item['id'] for item in self.payload if self.needle in item['text']][:1]})
        self.review=json.loads(message)
        return json.dumps({'support':'supported','coverage':'complete','reason':'Scope checked'})

def tool(texts, pages=None, sections=None):
    pages=pages or ['Conta Digital','Link de Pagamento']
    sections=sections or pages
    urls={'Conta Digital':'https://site.getnet.com.br/conta-digital/','Link de Pagamento':'https://site.getnet.com.br/link-de-pagamento/','Pix':'https://site.getnet.com.br/pix/'}
    sources=[SourceItem(title=page,url=urls[page],snippet=text) for page,text in zip(pages,texts)]
    chunks=[{'text':text,'metadata':{'section':section,'product':page,'document_id':'doc'+str(i),'chunk_id':i}}
        for i,(text,page,section) in enumerate(zip(texts,pages,sections))]
    result=ToolResult(success=True,data={'contexts':texts,'chunks':chunks},sources=sources)
    return SimpleNamespace(name='rag_search',run=lambda q:result)

@pytest.mark.parametrize('question',[
    'O cartão virtual grátis é uma funcionalidade da Conta Digital ou do Link de Pagamento?',
    'O cartão virtual grátis é do Link de Pagamento ou da Conta Digital?',
    'Essa funcionalidade de cartão virtual grátis pertence ao Link de Pagamento ou à Conta Digital?',
])
def test_feature_has_named_source_scope_in_both_product_orders(question):
    llm=Select()
    agent=KnowledgeAgent(tool(['Cartão virtual grátis','Personalize o link com a imagem do produto.']),None,llm,True)
    result=agent.handle(question)
    assert not result.escalated
    assert '**Conta Digital**: Cartão virtual grátis' in result.answer
    assert 'não consegui confirmar essa associação com Link de Pagamento' in result.answer
    assert 'Isso não demonstra' in result.answer
    selected=result.metadata['selected_evidence'][0]
    assert selected['product']=='Conta Digital' and selected['section']=='Conta Digital'
    assert selected['url'].endswith('/conta-digital/') and selected['source_id']
    reviewed=review_knowledge(question,result,agent)
    assert not reviewed.escalated
    assert reviewed.metadata['evidence_review']['status']=='verified_source_attribution'
    assert not hasattr(llm,'review')

@pytest.mark.parametrize('feature,owner,other',[
    ('Personalize o link com a imagem do produto.','Link de Pagamento','Conta Digital'),
    ('Receba todos os pagamentos na mesma conta','Conta Digital','Link de Pagamento'),
    ('Compartilhe a cobrança por WhatsApp com seu cliente.','Link de Pagamento','Conta Digital'),
])
def test_mapping_is_not_a_hardcoded_virtual_card_answer(feature,owner,other):
    question=f'Esse recurso pertence à {owner} ou à {other}?'
    r=KnowledgeAgent(tool([feature,'Outro trecho informativo sem o recurso.'],[owner,other]),None,Select(feature),True).handle(question)
    assert f'**{owner}**: {feature}' in r.answer
    assert f'não consegui confirmar essa associação com {other}' in r.answer


def test_section_scope_overrides_cross_selling_page():
    records=build_records(['Personalize o link com a imagem do produto.'],
        [SourceItem(title='Conta Digital',url='https://site.getnet.com.br/conta-digital/')],
        [{'metadata':{'product':'conta-digital','section':'Link de Pagamento'}}])
    assert records[0].product=='Link de Pagamento' and records[0].scope_basis=='section'


def test_mixed_section_does_not_infer_owner_from_page_title():
    records=build_records(['Cartão virtual grátis'],
        [SourceItem(title='Conta Digital',url='https://site.getnet.com.br/conta-digital/')],
        [{'metadata':{'product':'conta-digital','section':'Conta Digital e Link de Pagamento'}}])
    assert records[0].product is None


def test_cross_sell_without_explicit_section_is_unconfirmed():
    records=build_records(['Link de Pagamento: personalize com a imagem do produto.'],
        [SourceItem(title='Conta Digital',url='https://site.getnet.com.br/conta-digital/')])
    assert records[0].product is None


def test_missing_feature_does_not_become_negative_product_claim():
    question='O recurso inexistente de reconhecimento facial pertence à Conta Digital ou ao Link de Pagamento?'
    r=KnowledgeAgent(tool(['Cartão virtual grátis','Personalize o link com a imagem do produto.']),None,Select('reconhecimento facial'),True).handle(question)
    assert r.escalated and r.metadata['abstained']
    assert 'não oferece' not in r.answer


def test_filtering_keeps_source_indices_and_identity():
    rag=tool(['Pix permite pagamentos por QR Code.','Cartão virtual grátis','Personalize o link com a imagem do produto.'],
        ['Pix','Conta Digital','Link de Pagamento'])
    r=KnowledgeAgent(rag,None,Select(),True).handle('Cartão virtual grátis é funcionalidade da Conta Digital ou do Link de Pagamento?')
    item=r.metadata['selected_evidence'][0]
    assert item['source_index']==0 and r.sources[0].url.endswith('/conta-digital/')
    assert item['url']==r.sources[item['source_index']].url


def test_prose_experiment_receives_the_same_structured_records():
    class Prose:
        def generate(self, system, user):
            self.prompt=user
            return 'A fonte da Conta Digital lista cartão virtual grátis.'
    llm=Prose()
    r=KnowledgeAgent(tool(['Cartão virtual grátis','Personalize o link com a imagem do produto.']),None,llm,True,answer_mode='prose').handle('O cartão virtual grátis é da Conta Digital ou do Link de Pagamento?')
    assert not r.escalated
    records=json.loads(llm.prompt.split('associação não confirmada):\n',1)[1])
    assert records[0]['product']=='Conta Digital' and records[0]['source_id']
    assert r.metadata['generation_kind']=='llm'


def test_identical_feature_in_two_sources_keeps_both_product_relations():
    class SelectAll(Select):
        def generate_structured(self, system, message, schema):
            items=json.loads(message.split('TRECHOS:\n',1)[1])
            return json.dumps({'ids':[x['id'] for x in items if x['text']=='Cartão virtual grátis']})
    r=KnowledgeAgent(tool(['Cartão virtual grátis','Cartão virtual grátis']),None,SelectAll(),True).handle('O cartão virtual grátis é da Conta Digital ou do Link de Pagamento?')
    assert '**Conta Digital**: Cartão virtual grátis' in r.answer
    assert '**Link de Pagamento**: Cartão virtual grátis' in r.answer
    assert len({x['source_id'] for x in r.metadata['selected_evidence']})==2
    assert 'não consegui confirmar' not in r.answer


def test_unknown_section_scope_is_visible_without_false_attribution():
    rag=tool(['Cartão virtual grátis','Personalize o link com a imagem do produto.'],sections=['Conta Digital e Link de Pagamento','Link de Pagamento'])
    r=KnowledgeAgent(rag,None,Select(),True).handle('O cartão virtual grátis é da Conta Digital ou do Link de Pagamento?')
    assert '**Produto não confirmado neste trecho**: Cartão virtual grátis' in r.answer
    assert '**Conta Digital**: Cartão virtual grátis' not in r.answer


def test_unpaired_context_never_borrows_another_source():
    r=ToolResult(success=True,data={'contexts':['Cartão virtual grátis','Informação sem fonte.']},sources=[SourceItem(title='Conta Digital',url='https://site.getnet.com.br/conta-digital/',snippet='Cartão virtual grátis')])
    agent=KnowledgeAgent(SimpleNamespace(name='rag_search',run=lambda q:r),None,Select(),True)
    output=agent.handle('Quais funcionalidades a Conta Digital oferece?')
    assert len(output.metadata['evidence_records'])==1
    assert output.metadata['evidence_records'][0]['text']=='Cartão virtual grátis'


def test_provider_cannot_invent_source_or_product_identifiers():
    class Invalid(Select):
        def generate_structured(self,*args):
            return '{"ids":[999],"product":"Link de Pagamento"}'
    r=KnowledgeAgent(tool(['Cartão virtual grátis','Personalize o link com a imagem do produto.']),None,Invalid(),True).handle('O cartão virtual grátis é da Conta Digital ou do Link de Pagamento?')
    assert r.escalated and r.metadata['fallback']=='invalid_evidence_selection'
