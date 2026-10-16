from unittest.mock import Mock
import pytest
from app.agents.knowledge import KnowledgeAgent
from app.models.tools import ToolResult, SourceItem
from app.rag.relevance import relevant, answer_abstains

@pytest.mark.parametrize('text', ['Não há cotação do euro disponível no contexto fornecido.', 'O valor solicitado não está disponível nas fontes.', 'A previsão não consta nos trechos consultados.'])
def test_missing_live_value_is_abstention(text):
    assert answer_abstains(text)

@pytest.mark.parametrize('body', ['Venda usando sua rede social com o Link de Pagamento.', 'Conecte seu negócio com soluções de comércio online.', 'Seamless integration with your existing ecosystem.'])
def test_network_marketing_is_not_terminal_diagnosis(body):
    assert not relevant('Getnet maquininha internet conexão', body, 'Online Payments', 'https://www.getnet.net/en/our-solutions/online-payments')

def agent_for(text,title,url,answer):
    rag=Mock();rag.name='rag_search'
    rag.run.return_value=ToolResult(success=True,data={'contexts':[text]},sources=[SourceItem(title=title,url=url,snippet=text)])
    web=Mock();web.run.return_value=ToolResult(success=False,error='No evidence')
    llm=Mock();llm.generate.return_value=answer
    return KnowledgeAgent(rag,web,llm,True),rag,web,llm

def test_account_question_without_brand_uses_rag():
    a,rag,web,llm=agent_for('Conta Digital: cartão virtual grátis e recebimento na mesma conta.','Conta Digital','https://site.getnet.com.br/conta-digital/','{"ids":[0]}')
    r=a.handle('Como funciona a Conta Digital?')
    assert r.tool=='rag_search' and not r.escalated
    rag.run.assert_called_once();web.run.assert_not_called()

def test_pix_cross_sell_does_not_authorize_get_tap_claim():
    a,*_=agent_for('Pix: receba com QR Code.\nVenda mais: Maquininhas Link de Pagamento Get Tap.','Pix','https://site.getnet.com.br/pix/','O Pix funciona com QR Code e com Get Tap no celular.')
    r=a.handle('Como funciona o Pix na Getnet?')
    assert r.escalated and r.metadata.get('abstained')

def test_catalog_separates_products_from_slogan_and_legal_entity():
    a,rag,web,llm=agent_for('Conta Digital: cartão virtual grátis. Maquininhas Link de pagamento Get Tap. Getnet Adquirência e Serviços para Meios de Pagamento SA.','Conta Digital','https://site.getnet.com.br/conta-digital/','Produtos: Cartão virtual grátis e Getnet Adquirência.')
    r=a.handle('Quais soluções de pagamento a Getnet oferece?')
    assert not r.escalated
    assert 'Cartão virtual' not in r.answer and 'Adquirência' not in r.answer
    assert 'Get Tap' in r.answer and 'Link de Pagamento' in r.answer

def test_actual_terminal_connection_evidence_is_accepted():
    assert relevant('maquininha internet conexão', 'Confira Wi-Fi e dados móveis.', 'Get Smart', 'https://site.getnet.com.br/get-smart/')

def test_heading_scoped_chunks_do_not_mix_product_sections():
    from app.rag.ingest import section_chunks
    chunks=list(section_chunks('[SEÇÃO] Link de Pagamento\nCompartilhe o link.\n[SEÇÃO] Conta Digital\nCartão virtual grátis.', 'Produtos'))
    assert chunks[0][0]=='Link de Pagamento'
    assert 'Cartão virtual' not in chunks[0][1]
    assert chunks[1][0]=='Conta Digital'

def test_line_boundaries_survive_chunking():
    from app.rag.chunking import chunk_text
    assert '\n' in chunk_text('Pix: QR Code.\nOutros produtos: Get Tap.')[0]

def test_euro_missing_numeric_evidence_escalates():
    a,*_=agent_for('Cotação do euro: consulte o site.', 'Euro', 'https://example.test/euro', 'Não há cotação do euro disponível no contexto fornecido.')
    a.web.run.return_value=a.rag.run.return_value
    r=a.handle('Qual é a cotação do euro hoje?')
    assert r.escalated and r.metadata['abstained']

def test_html_headings_become_real_section_metadata(monkeypatch):
    from app.rag.ingest import fetch_page,section_chunks
    response=Mock();response.content=b'<html><title>Produtos</title><body><main><h2>Conta Digital</h2><div>Cartao virtual gratis</div><h2>Link de Pagamento</h2><div>Compartilhe o link</div></main></body></html>'
    monkeypatch.setattr('app.rag.ingest.socket.getaddrinfo',lambda *a,**k:[(2,1,6,'',('8.8.8.8',443))])
    response.status_code=200;response.headers={'Content-Type':'text/html'};response.iter_content.return_value=[response.content]
    monkeypatch.setattr('app.rag.ingest.requests.get',Mock(return_value=response))
    title,text=fetch_page('https://site.getnet.com.br/',1)
    chunks=list(section_chunks(text,title))
    assert [s for s,c in chunks]==['Conta Digital','Link de Pagamento']
    assert 'Cartao virtual' not in chunks[1][1]
