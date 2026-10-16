from unittest.mock import Mock
import pytest
from tests.integration.test_second_live_regressions import agent_for
from app.rag.ingest import section_chunks

@pytest.mark.parametrize('claim',[
 'O Link de Pagamento permite pagar diretamente no site do vendedor.',
 'A Conta Digital é uma conta bancária para todas as operações financeiras.',
])
def test_unrestricted_product_prose_not_published(claim):
    q='Como funciona o Link de Pagamento?' if 'Link' in claim else 'Como funciona a Conta Digital?'
    a,*_=agent_for('Link de Pagamento: aceite Pix.\nConta Digital: cartão virtual grátis.','Produto','https://site.getnet.com.br/',claim)
    r=a.handle(q)
    assert r.escalated and r.metadata['abstained']

@pytest.mark.parametrize('raw', ['{"ids":[0]}','{"ids":[0,0]}'])
def test_model_selects_documented_text_not_novel_prose(raw):
    a,rag,web,llm=agent_for('Conta Digital\nCartão virtual grátis\nReceba todos os pagamentos na mesma conta','Conta Digital','https://site.getnet.com.br/conta-digital/',raw)
    r=a.handle('Quais benefícios da Conta Digital?')
    assert not r.escalated
    assert r.metadata['generation_kind']=='llm_evidence_selection'
    assert 'conta bancária' not in r.answer
    assert len(r.metadata['selected_evidence_ids'])==1

@pytest.mark.parametrize('raw', ['{"ids":[99]}','{"ids":[true]}','{"ids":[],"answer":"inventado"}','{"ids":[-1]}'])
def test_invalid_selection_does_not_become_resolved(raw):
    a,*_=agent_for('Conta Digital\nCartão virtual grátis','Conta Digital','https://site.getnet.com.br/conta-digital/',raw)
    r=a.handle('Como funciona a Conta Digital?')
    assert r.escalated and r.metadata['abstained']

def test_procedure_sections_remain_in_one_context():
    text='[SEÇÃO] Veja como é fácil vender com o Link de Pagamento\n1\n[SEÇÃO] Acesse o Portal Minha Conta\nEntre com login.\n[SEÇÃO] Crie seu Link de Pagamento\nSelecione Produtos e Serviços.\n[SEÇÃO] Configure\nPreencha produto, frete e pagamento.\n[SEÇÃO] Pronto para vender\nClique em compartilhar ou copiar.\n[SEÇÃO] Dúvidas\nCentral de ajuda.'
    chunks=list(section_chunks(text,'Link'))
    assert len(chunks)==2
    assert all(word in chunks[0][1] for word in ['login','Produtos','frete','compartilhar'])
    assert 'Central de ajuda' not in chunks[0][1]

def test_creation_procedure_includes_configuration_and_sharing():
    text='Veja como é fácil vender com o Link de Pagamento\n1\nAcesse o Portal Minha Conta\nVocê pode acessar o portal com seu login e senha.\n2\nCrie seu Link de Pagamento\nEm Produtos e Serviços, selecione Link de Pagamento e depois Criar Link de Pagamento\n3\nConfigure\nPreencha as informações do produto, frete e opções para pagamento.\n4\nPronto para vender\nClique em compartilhar ou copiar e compartilhe por onde quiser.'
    a,*_=agent_for(text,'Link','https://site.getnet.com.br/link-de-pagamento/','Selecione Link e Criar Link.')
    r=a.handle('Como criar esse Link de Pagamento?')
    assert not r.escalated
    assert 'frete' in r.answer and 'compartilhar' in r.answer and 'login' in r.answer

def test_pix_avoids_ctas_and_repeating_modalities():
    text='Receba com Pix através de:\nAproximação\nBiometria* Novo\nGet Tap no celular\nQR Code na maquininha\nQUERO VENDER\n*O horário de recebimento do Pix pode variar em até um dia corrido, dependendo do modelo de Pix.'
    a,rag,web,llm=agent_for(text,'Pix','https://site.getnet.com.br/pix/','unused')
    rag.run.return_value.data['contexts'].append(text.replace('\n','\n '))
    rag.run.return_value.sources.append(rag.run.return_value.sources[0])
    r=a.handle('Como funciona o Pix na Getnet?')
    assert r.answer.count('QR Code na maquininha')==1
    assert 'QUERO VENDER' not in r.answer
    assert r.answer.count('um dia corrido')==1

def test_commercial_summary_removes_simulator_placeholders():
    text='Link de pagamento Inicial\nR$1,00 por link pago.\nBásico\nR$28\n/mês\n60 transações por mês\n+ R$0,50 por transação excedente\nQuero contratar\nSimule o recebimento\nValor da venda\nR$\n0\n,00\nTaxa 1,90%\nCondição válida somente para novos clientes.\nTaxas sujeitas a alteração.'
    a,*_=agent_for(text,'Link','https://site.getnet.com.br/link-de-pagamento/','unused')
    r=a.handle('Quais taxas do Link de Pagamento?')
    assert 'Quero contratar' not in r.answer and 'Valor da venda' not in r.answer and 'Simule' not in r.answer
    assert 'Inicial' in r.answer and 'Básico' in r.answer and 'novos clientes' in r.answer

def test_selected_source_index_survives_filtered_pricing_context():
    from app.models.tools import SourceItem
    a,rag,web,llm=agent_for('Link de Pagamento: Taxa 1,90%.','Link','https://site.getnet.com.br/link-de-pagamento/','{"ids":[0]}')
    rag.run.return_value.data['contexts'].append('Link de Pagamento aceita Pix.')
    rag.run.return_value.sources.append(SourceItem(title='Link',url='https://site.getnet.com.br/link-de-pagamento/',snippet='Link de Pagamento aceita Pix.'))
    r=a.handle('Como funciona o Link de Pagamento?')
    assert not r.escalated
    chosen=r.metadata['selected_evidence'][0]
    assert chosen['source_index']==1
    assert chosen['text'] in r.sources[chosen['source_index']].snippet

def test_empty_selection_is_explicit_abstention():
    a,*_=agent_for('Conta Digital\nCartão virtual grátis','Conta Digital','https://site.getnet.com.br/conta-digital/','{"ids":[]}')
    r=a.handle('Como funciona a Conta Digital?')
    assert r.escalated and r.metadata['fallback']=='selection_no_relevant_evidence'

@pytest.mark.parametrize('raw',['{"ids":[0],"answer":"inventado"}','{"ids":[0.0]}'])
def test_model_cannot_smuggle_text_or_float_ids(raw):
    a,*_=agent_for('Conta Digital\nCartão virtual grátis','Conta Digital','https://site.getnet.com.br/conta-digital/',raw)
    r=a.handle('Como funciona a Conta Digital?')
    assert r.escalated and 'inventado' not in r.answer

def test_complete_tutorial_outranks_higher_vector_offer(tmp_path):
    from app.rag.retriever import Retriever
    from app.rag.vector_store import SearchHit
    store=Mock();store.directory=tmp_path
    offer=SearchHit(text='Link de Pagamento: oferta por R$ 1,00.',score=.99,metadata={'title':'Link','url':'https://site.getnet.com.br/link-de-pagamento/','section':'Oferta'})
    tutorial=SearchHit(text='Link de Pagamento: acesse o portal, selecione Criar Link, configure produto e frete e clique em compartilhar.',score=.2,metadata={'title':'Link','url':'https://site.getnet.com.br/link-de-pagamento/','section':'Veja como vender'})
    store.search.return_value=[offer,tutorial]
    embeddings=Mock();embeddings.embed.return_value=[[1.,0.]]
    result=Retriever(store,embeddings,1,.12).retrieve('Como criar um Link de Pagamento?')
    assert result.hits==[tutorial]
