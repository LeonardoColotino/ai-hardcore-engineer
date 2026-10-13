"""Regressions from development capture; no claim of live model quality."""
import pytest
from unittest.mock import Mock
from app.rag.relevance import relevant, answer_abstains
from app.models.tools import ToolResult, SourceItem
from app.agents.knowledge import KnowledgeAgent
from app.services.llm import DisabledLLMClient, OllamaLLMClient, LLMError
from app.orchestration.intents import human_request, products
from tests.integration.test_audit_regressions import client, send

@pytest.mark.parametrize('text',[
 'Não posso confirmar essa informação com as fontes disponíveis.',
 'O contexto não fornece informações suficientes para responder.',
 'Infelizmente, não consegui encontrar a cotação nos snippets.',
 'Lamento, mas não consegui encontrar informações sobre o clima.',
])
def test_abstention_is_not_resolution(text):
 assert answer_abstains(text)

@pytest.mark.parametrize('question,text,title,url',[
 ('Como funciona Get Smart?','Pix usa biometria','Pix','https://site.getnet.com.br/pix/'),
 ('Como funciona Get Clássica?','Conta Digital oferece cartão virtual','Conta','https://site.getnet.com.br/conta-digital/'),
 ('Como funciona Pix Getnet?','Link de Pagamento e antecipação de recebíveis','Link','https://site.getnet.com.br/link-de-pagamento/'),
])
def test_other_product_is_not_evidence(question,text,title,url):
 assert not relevant(question,text,title,url)

def test_general_human_question_not_request():
 assert not human_request('A Getnet oferece atendimento humano?')
 assert human_request('Quero falar com um atendente humano')

def test_plural_products_recognized():
 assert 'maquininha' in products('Maquininhas')
 assert 'Get Tap' in products('Get Tap')

def test_social_message_preserves_state_without_ticket(client,api_auth):
 h=api_auth('cliente1988'); first=send(client,h,'Como funciona o Link de Pagamento?')
 r=send(client,h,'Obrigado',first['session_id'])
 assert not r['escalated'] and r['ticket_id'] is None
 assert r['metadata']['products']==['Link de Pagamento']

def test_deposit_followup_uses_same_identity(client,api_auth):
 h=api_auth('cliente1988'); first=send(client,h,'Minhas vendas não caíram')
 r=send(client,h,'Qual a previsão do depósito?',first['session_id'])
 assert r['tool']=='payment_status' and not r['escalated']
 assert '2026-10-05' in r['answer']

def test_comparison_keeps_two_entities(client,api_auth):
 h=api_auth('cliente1988');r=send(client,h,'Como funciona Get Smart?');sid=r['session_id']
 send(client,h,'Como funciona Get Clássica?',sid)
 r=send(client,h,'Qual das duas tem conectividade melhor?',sid)
 assert set(r['metadata']['products'])=={'Get Smart','Get Clássica'}
 assert r['metadata'].get('previous_agent',r['agent'])=='knowledge'

def test_html_div_content_survives(monkeypatch):
 from app.rag.ingest import fetch_page
 response=Mock();response.content=b'<html><title>Link</title><body><nav>MENU</nav><main><h2>Crie seu Link</h2><div>Acesse Produtos e Servicos e preencha produto e frete.</div><p>Compartilhe.</p></main></body></html>'
 monkeypatch.setattr('app.rag.ingest.requests.get',Mock(return_value=response))
 _,text=fetch_page('https://site.getnet.com.br/link-de-pagamento/',1)
 assert 'preencha produto e frete' in text and 'MENU' not in text

def test_ollama_length_finish_not_success(monkeypatch):
 response=Mock();response.json.return_value={'message':{'content':'Passo 1. O cliente clica no'},'done_reason':'length','eval_count':96}
 monkeypatch.setattr('app.services.llm.requests.post',Mock(return_value=response))
 with pytest.raises(LLMError): OllamaLLMClient('http://localhost:11434','model').generate('s','u')

def test_buyer_requirement_not_inferred_from_advertising():
 rag=Mock();rag.name='rag_search'
 text='Link de Pagamento: personalize e compartilhe. Aceita Pix.'
 rag.run.return_value=ToolResult(success=True,data={'contexts':[text]},sources=[SourceItem(title='Link',url='https://site.getnet.com.br/link-de-pagamento/',snippet=text)])
 web=Mock();llm=Mock();llm.generate.return_value='Não, quem não compra precisa de conta Getnet.'
 r=KnowledgeAgent(rag,web,llm,True).handle('Quem compra precisa de conta Getnet no Link de Pagamento?')
 assert r.escalated and r.metadata['abstained']
 llm.generate.assert_not_called()
