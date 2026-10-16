from unittest.mock import Mock
import pytest, requests
from app.services.llm import OllamaLLMClient,LLMError

@pytest.mark.parametrize('failure',[requests.Timeout('timeout'),requests.ConnectionError('offline')])
def test_llm_transport_timeout(monkeypatch,failure):
    call=Mock(side_effect=failure);monkeypatch.setattr('app.services.llm.requests.post',call)
    with pytest.raises(LLMError): OllamaLLMClient('http://localhost:11434','demo',2).generate('system','question')
    assert call.call_args.kwargs['timeout']==2

@pytest.mark.parametrize('body',[{}, {'message':{'content':''}}, {'message':{'content':123}}])
def test_invalid_provider_response(monkeypatch,body):
    r=Mock();r.json.return_value=body
    monkeypatch.setattr('app.services.llm.requests.post',Mock(return_value=r))
    with pytest.raises(LLMError): OllamaLLMClient('http://localhost:11434','demo').generate('system','question')
