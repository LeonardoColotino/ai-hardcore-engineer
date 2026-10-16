from unittest.mock import Mock
import pytest
from app.rag.relevance import answer_abstains
from tests.integration.test_second_live_regressions import agent_for

@pytest.mark.parametrize('text', [
 'Não é possível fornecer a cotação do euro em tempo real, pois a taxa pode variar constantemente e não há uma fonte atualizada no contexto fornecido.',
 'A informação está indisponível nas fontes consultadas.',
 'Não posso fornecer o valor atual com os dados disponíveis.',
])
def test_actual_abstentions_are_not_answers(text):
    assert answer_abstains(text)

def test_explanation_does_not_generalize_promotion():
    text='Link de Pagamento: aceite débito, crédito, Pix e boleto.\nTaxa 1,90%. Condição válida para novos clientes.\nTaxas sujeitas a alteração.'
    a,*_=agent_for(text,'Link','https://site.getnet.com.br/link-de-pagamento/','O vendedor paga uma taxa única de 1,90% sobre a venda.')
    r=a.handle('Como funciona o Link de Pagamento Getnet?')
    assert r.escalated and r.metadata['abstained']

def test_price_answer_preserves_plan_and_conditions():
    text='Link de pagamento Inicial\nR$1,00 por link pago.\nBásico\nPor\nR$28\n/mês\n60 transações de cartão por mês\n+ R$0,50 por transação excedente\nTaxa 1,90%\nCondição válida somente para novos clientes.\nTaxas sujeitas a alteração.'
    a,*_=agent_for(text,'Link','https://site.getnet.com.br/link-de-pagamento/','A taxa do Link de Pagamento é de R$ 1,00 por link pago.')
    r=a.handle('Quais taxas do Link de Pagamento?')
    assert 'Inicial' in r.answer and 'Básico' in r.answer
    assert 'novos clientes' in r.answer and 'sujeitas a alteração' in r.answer

def test_pix_modalities_are_not_an_invented_workflow():
    text='Pix\nReceba com Pix através de:\nAproximação\nBiometria* Novo\nGet Tap no celular\nQR Code na maquininha\nQUERO VENDER\n*O horário de recebimento do Pix pode variar em até um dia corrido, dependendo do modelo de Pix o qual o cliente é elegível e do horário de aprovação da venda.'
    a,*_=agent_for(text,'Pix','https://site.getnet.com.br/pix/','O Pix funciona com impressão digital e envia um QR code para o celular do vendedor instantaneamente.')
    r=a.handle('Como funciona o Pix na Getnet?')
    assert not r.escalated
    assert 'impressão digital' not in r.answer and 'instantaneamente' not in r.answer
    assert 'QR Code na maquininha' in r.answer and 'um dia corrido' in r.answer

def test_pdf_preview_does_not_authorize_invented_buttons():
    a,rag,web,llm=agent_for('2. Qual é a função de cada botão? Sua Get Clássica pode variar em até 4 modelos, mas a tecnologia será a mesma. Get Clássica - S920 Avança','Get Clássica','https://site.getnet.com.br/manual.pdf','Os botões são Avançar, Cancelar, Fazer Compra e Fazer Pagamento.')
    r=a.handle('Como funciona Get Clássica?')
    assert r.escalated and r.metadata['abstained']

def test_nested_heading_stays_with_section_marker(monkeypatch):
    from app.rag.ingest import fetch_page,section_chunks
    response=Mock();response.content=b'<html><title>Produtos</title><body><main><h2><span>Inicial</span></h2><div>R$1 por link</div><h2><div>Condicoes</div></h2><div>Somente novos clientes.</div></main></body></html>'
    monkeypatch.setattr('app.rag.ingest.socket.getaddrinfo',lambda *a,**k:[(2,1,6,'',('8.8.8.8',443))])
    response.status_code=200;response.headers={'Content-Type':'text/html'};response.iter_content.return_value=[response.content]
    monkeypatch.setattr('app.rag.ingest.requests.get',Mock(return_value=response))
    title,text=fetch_page('https://site.getnet.com.br/',1)
    sections=list(section_chunks(text,title))
    assert [s for s,t in sections]==['Inicial','Condicoes']
    assert '[SEÇÃO]' not in ''.join(t for s,t in sections)

def test_exchange_page_title_is_not_current_numeric_data():
    from app.models.tools import ToolResult,SourceItem
    a,rag,web,llm=agent_for('ignored','Link','https://site.getnet.com.br/link-de-pagamento/','A cotação varia.')
    web.run.return_value=ToolResult(success=True,sources=[SourceItem(url='https://example.test/euro',title='Euro',snippet='Saiba quanto vale 1 € e consulte a cotação hoje.')])
    r=a.handle('Qual é a cotação do euro hoje?')
    assert r.escalated and r.metadata['fallback']=='current_measurement_missing'
    llm.generate.assert_not_called()

def test_current_data_gate_accepts_documented_numeric_values():
    from app.rag.answer_policy import missing_current_measurement
    assert not missing_current_measurement('Qual é a cotação do euro hoje?', ['EUR: R$ 6,15.'])
    assert not missing_current_measurement('Qual o clima amanhã?', ['Temperatura máxima: 25°C.'])

def test_source_price_is_not_sent_to_model_for_usage_question():
    a,rag,web,llm=agent_for('Link de Pagamento aceita Pix.','Link','https://site.getnet.com.br/link-de-pagamento/','{"ids":[0]}')
    rag.run.return_value.data['contexts'].append('Link de Pagamento: Taxa 1,90%.')
    from app.models.tools import SourceItem
    rag.run.return_value.sources.append(SourceItem(title='Link',url='https://site.getnet.com.br/link-de-pagamento/',snippet='Link de Pagamento: Taxa 1,90%.'))
    r=a.handle('Como funciona o Link de Pagamento?')
    assert not r.escalated
    assert '1,90%' not in llm.generate.call_args.args[1]

def test_receipt_modalities_quote_instead_of_calling_free_generation():
    a,rag,web,llm=agent_for('Pix\nReceba com Pix através de:\nQR Code na maquininha\nQUERO VENDER','Pix','https://site.getnet.com.br/pix/','Não usar')
    r=a.handle('Como funciona o Pix?')
    assert r.metadata['generation_kind']=='payment_modalities_extraction'
    llm.generate.assert_not_called()

import json
from pathlib import Path
from app.agents.knowledge import KnowledgeAgent
from app.models.tools import ToolResult,SourceItem

CAPTURE_FIXTURES=json.loads((Path(__file__).parents[1]/'fixtures/round2_problematic_answers.json').read_text(encoding='utf-8'))

@pytest.mark.parametrize('row',CAPTURE_FIXTURES,ids=lambda row:row['case'])
def test_replay_captured_bad_answer_is_rejected_or_source_scoped(row):
    sources=[SourceItem(**s) for s in row['sources']]
    result=ToolResult(success=True,data={'contexts':[s.snippet for s in sources]},sources=sources)
    rag=Mock();rag.name='rag_search';rag.run.return_value=result if row['tool']=='rag_search' else ToolResult(success=False,error='No local source')
    web=Mock();web.name='web_search';web.run.return_value=result
    llm=Mock();llm.generate.return_value=row['bad_answer']
    r=KnowledgeAgent(rag,web,llm,True).handle(row['question'])
    if row['case'] in ('D02','D04','D13'):
        assert r.escalated and r.metadata['abstained']
    elif row['case']=='D14':
        assert not r.escalated
        assert 'impressão digital' not in r.answer and 'instantaneamente' not in r.answer
        assert all(excerpt in '\n\n'.join(s.snippet for s in sources) for excerpt in r.metadata['evidence_excerpts'])
    elif row['case']=='D20':
        assert not r.escalated
        assert 'Inicial' in r.answer and 'Básico' in r.answer and 'Condição válida' in r.answer
        assert 'Taxas sujeitas a alteração' in r.answer
