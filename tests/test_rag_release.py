"""Simulated HTTP/LLM checks; no live provider claims."""
import json
from unittest.mock import Mock
import pytest
from app.rag.ingest import fetch_page, validate_source_url
from app.rag.chunking import chunk_text
from app.rag.vector_store import NumpyVectorStore
from app.rag.retriever import Retriever
from app.services.embeddings import HashingEmbeddingService
from app.agents.knowledge import KnowledgeAgent

@pytest.mark.parametrize('url',['http://site.getnet.com.br','https://evil.getnet.com.br','https://getnet.net@localhost','https://site.getnet.com.br:444/a'])
def test_source_allowlist(url):
    with pytest.raises(ValueError): validate_source_url(url)

def response(body,status=200,headers=None):
    obj=Mock(status_code=status,headers=headers or {});obj.iter_content.return_value=[body];return obj

def test_redirect_private_never_requested(monkeypatch):
    monkeypatch.setattr('app.rag.ingest.socket.getaddrinfo',lambda *a,**k:[(2,1,6,'',('8.8.8.8',443))])
    get=Mock(return_value=response(b'',302,{'Location':'http://127.0.0.1/private'}))
    monkeypatch.setattr('app.rag.ingest.requests.get',get)
    with pytest.raises(ValueError):fetch_page('https://site.getnet.com.br',2)
    assert get.call_count==1

def test_dns_private_block(monkeypatch):
    monkeypatch.setattr('app.rag.ingest.socket.getaddrinfo',lambda *a,**k:[(2,1,6,'',('127.0.0.1',443))])
    get=Mock();monkeypatch.setattr('app.rag.ingest.requests.get',get)
    with pytest.raises(ValueError):fetch_page('https://site.getnet.com.br',2)
    get.assert_not_called()

def test_html_procedure_tables(monkeypatch):
    monkeypatch.setattr('app.rag.ingest.socket.getaddrinfo',lambda *a,**k:[(2,1,6,'',('8.8.8.8',443))])
    html=b'<title>Fixture</title><main><h2>Procedimento</h2><ol><li>Abra</li><li>Confira</li><li>Envie</li></ol><table><tr><th>Prazo</th><td>2 dias se aprovado</td></tr></table></main>'
    monkeypatch.setattr('app.rag.ingest.requests.get',Mock(return_value=response(html)))
    _,text=fetch_page('https://site.getnet.com.br',2);chunks=chunk_text(text)
    assert len(chunks)==1 and '## Procedimento' in chunks[0]
    assert '3. Envie' in chunks[0] and 'Prazo | 2 dias se aprovado' in chunks[0]

def test_provider_mismatch(tmp_path):
    emb=HashingEmbeddingService();store=NumpyVectorStore(tmp_path)
    store.build(emb.embed(['fixture']),[{'text':'fixture','metadata':{}}])
    path=tmp_path/'manifest.json';m=json.loads(path.read_text());m['embedding_provider']='ollama';path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='provider changed'):Retriever(store,emb,2,0).retrieve('fixture')

def test_numeric_gate_complete_steps():
    llm=Mock();agent=KnowledgeAgent(Mock(),Mock(),llm,True,answer_mode="prose");llm.generate.return_value='A taxa é 9%.'
    _,meta=agent._answer_from_context('Como funciona?',['A taxa depende do contrato.'])
    assert meta['fallback']=='unsupported_quantity'
    llm.generate.return_value='1. Abra o portal.\n2. Preencha os dados.\n3. Confira e compartilhe.'
    answer,meta=agent._answer_from_context('Como criar o Link de Pagamento?',['Link de Pagamento: 1. Abra o portal. 2. Preencha os dados. 3. Confira e compartilhe.'])
    assert '3. Confira' in answer and not meta.get('abstained')
    assert '45 palavras' not in llm.generate.call_args[0][0]

def test_comparison_missing_side():
    llm=Mock();agent=KnowledgeAgent(Mock(),Mock(),llm,True)
    _,meta=agent._answer_from_context('Qual a diferença entre Get Smart e Get Clássica?',['Get Smart oferece Wi-Fi.'])
    assert meta['fallback']=='comparison_side_missing';llm.generate.assert_not_called()
