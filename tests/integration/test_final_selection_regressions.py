from unittest.mock import Mock
import pytest
from app.services.llm import OllamaLLMClient
from app.rag.evidence_selection import select_evidence


def test_ollama_selection_enforces_schema_in_request(monkeypatch):
    response=Mock();response.json.return_value={'message':{'content':'{"ids":[0]}'},'done_reason':'stop'}
    post=Mock(return_value=response);monkeypatch.setattr('app.services.llm.requests.post',post)
    schema={'type':'object','properties':{'ids':{'type':'array','items':{'type':'integer','enum':[0]}}},'required':['ids'],'additionalProperties':False}
    assert OllamaLLMClient('http://localhost:11434','model').generate_structured('s','u',schema)=='{"ids":[0]}'
    payload=post.call_args.kwargs['json']
    assert payload['format']==schema and payload['options']['temperature']==0


def test_selector_uses_structured_capability_and_valid_id_enum():
    class Client:
        schema=None
        def generate(self,*args):raise AssertionError('Unconstrained path must not be used')
        def generate_structured(self,system,user,schema):
            self.schema=schema
            return '{"ids":[0]}'
    client=Client()
    answer,meta=select_evidence(client,'Como funciona a Conta Digital?', ['Conta Digital\nCartão virtual grátis'])
    assert meta['generation_kind']=='llm_evidence_selection'
    assert client.schema['properties']['ids']['items']['enum']==[0]
    assert 'Cartão virtual grátis' in answer

@pytest.mark.parametrize('text',[
 'Veja como funciona .',
 'Esse valor corresponde aos serviços oferecidos pela Getnet.',
 'A Getnet tem soluções físicas e digitais para alavancar o seu negócio.',
 'através do aplicativo com o antifraude da Getnet',
])
def test_nonanswers_do_not_get_selected_as_explanations(text):
    llm=Mock();llm.generate.return_value='{"ids":[0]}'
    answer,meta=select_evidence(llm,'Como funciona Get Smart?', [text])
    assert meta['abstained'] and meta['fallback']=='no_selectable_evidence'
    llm.generate.assert_not_called()


def test_real_device_fact_can_be_selected():
    llm=Mock();llm.generate.return_value='{"ids":[0]}'
    text='Get Smart oferece conexão Wi-Fi e aceita cartões de débito e crédito.'
    answer,meta=select_evidence(llm,'Como funciona Get Smart?', [text])
    assert not meta.get('abstained') and text in answer


def test_general_link_explanation_does_not_choose_creation_menu():
    llm=Mock();llm.generate.return_value='{"ids":[0]}'
    answer,meta=select_evidence(llm,'Como funciona o Link de Pagamento?', ['Em Produtos e Serviços, selecione Link de Pagamento e depois Criar Link de Pagamento\nAceite débito, crédito, Pix e boleto'])
    assert 'Aceite débito' in answer and 'selecione' not in answer


def test_selection_failure_has_safe_diagnostic_without_raw_output():
    llm=Mock();llm.generate.return_value='{"ids":[999]}'
    _,meta=select_evidence(llm,'Como funciona a Conta Digital?', ['Cartão virtual grátis'])
    assert meta['abstained'] and meta['selection_failure_reason']=='invalid_reference'
    assert 'raw_output' not in meta
