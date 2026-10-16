"""New integration contracts for the consolidation; providers remain simulated."""
import json
import time
from dataclasses import replace
from unittest.mock import Mock
import pytest
from app.agents.base import AgentResult
from app.models.tools import SourceItem
from app.services.llm import (OllamaLLMClient, OpenAICompatibleClient, LLMError,
                              LLMTruncatedError, create_llm_client, reset_provider_usage, get_provider_usage)
from app.orchestration.planner import build_plan, review_knowledge


def provider_response(body):
    response = Mock()
    response.json.return_value = body
    return response


def test_structured_ollama_schema_and_usage(monkeypatch):
    response = provider_response({'message': {'content': '{"ids":[0]}'}, 'done_reason': 'stop', 'prompt_eval_count': 12, 'eval_count': 4})
    post = Mock(return_value=response)
    monkeypatch.setattr('app.services.llm.requests.post', post)
    reset_provider_usage()
    client = OllamaLLMClient('http://localhost:11434', 'demo')
    schema = {'type': 'object', 'properties': {'ids': {'type': 'array', 'items': {'type': 'integer'}}}, 'required': ['ids']}
    client.generate_structured('system', 'public question', schema)
    client.generate('system', 'public question')
    assert get_provider_usage() == {'input_tokens': 24, 'output_tokens': 8}
    assert post.call_args_list[0].kwargs['json']['format'] == schema
    assert post.call_args_list[0].kwargs['json']['options']['temperature'] == 0


@pytest.mark.parametrize('reason', ['length', 'stop'])
def test_compatible_truncation_and_private_errors(monkeypatch, reason):
    body = {'choices': [{'message': {'content': 'answer'}, 'finish_reason': reason}], 'usage': {'prompt_tokens': 10}}
    monkeypatch.setattr('app.services.llm.requests.post', Mock(return_value=provider_response(body)))
    client = OpenAICompatibleClient('http://localhost:1234/v1', 'demo')
    reset_provider_usage()
    if reason == 'length':
        with pytest.raises(LLMTruncatedError):
            client.generate('s', 'q')
    else:
        assert client.generate('s', 'q') == 'answer'
        assert get_provider_usage() == {'input_tokens': 10, 'output_tokens': None}


def test_unknown_provider_rejected(monkeypatch):
    from app.config import get_settings
    with pytest.raises(ValueError, match='Unknown'):
        create_llm_client(replace(get_settings(), llm_provider='typo'))


def test_compatible_planner_uses_structured_contract(monkeypatch):
    from evaluation.run import build_orchestrator
    from pathlib import Path
    import tempfile
    class Client:
        def generate_structured(self, system, message, schema):
            assert 'tasks' in schema['properties']
            return json.dumps({'tasks': [{'agent': 'knowledge', 'query': 'Como funciona Pix?', 'depends_on': None},
                                         {'agent': 'support', 'query': 'Quando minhas vendas serão depositadas?', 'depends_on': None}]})
    with tempfile.TemporaryDirectory() as directory:
        orch = build_orchestrator(Path(directory))
        orch.router.settings = replace(orch.router.settings, llm_provider='openai_compatible')
        orch.router.llm = Client()
        plan, origin = build_plan('Explique Pix e consulte minhas vendas', orch.router)
        assert origin == 'semantic' and [t.agent for t in plan.tasks] == ['knowledge', 'support']


@pytest.mark.parametrize('coverage,escalated', [('complete', False), ('incomplete', False), ('conflict', True)])
def test_public_review_enforces_coverage(coverage, escalated):
    class Client:
        def generate_structured(self, system, message, schema):
            assert 'private_amount' not in message
            return json.dumps({'coverage': coverage, 'support': 'supported', 'reason': 'public evidence checked'})
    knowledge = Mock(llm_enabled=True, llm=Client())
    result = AgentResult('Pix documentado.', sources=[SourceItem(title='Pix', url='https://site.getnet.com.br/pix/', snippet='Pix documentado.')])
    reviewed = review_knowledge('Como funciona o Pix?', result, knowledge)
    assert reviewed.escalated == escalated
    assert reviewed.metadata['evidence_review']['coverage'] == coverage


def test_private_review_does_not_call_remote_model():
    class Client:
        def generate_structured(self, *args):
            raise AssertionError('private query left server')
    result = AgentResult('Status demonstrativo.')
    knowledge = Mock(llm_enabled=True, llm=Client())
    assert review_knowledge('Minhas vendas cliente1988', result, knowledge).metadata['evidence_review']['status'] == 'skipped_private_query'


def test_oidc_real_signature_and_server_role(monkeypatch, tmp_path):
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from app.security import oidc_identity
    from fastapi import HTTPException
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    monkeypatch.setenv('OIDC_ISSUER', 'https://issuer.test')
    monkeypatch.setenv('OIDC_AUDIENCE', 'demo')
    monkeypatch.setenv('OIDC_JWKS_URL', 'https://issuer.test/jwks')
    identities = tmp_path / 'identity.json'
    identities.write_text(json.dumps({'external-sub': {'user_id': 'cliente1988', 'role': 'customer'}}))
    monkeypatch.setenv('OIDC_IDENTITIES_FILE', str(identities))
    client = Mock()
    client.get_signing_key_from_jwt.return_value.key = key.public_key()
    monkeypatch.setattr('app.security.jwks_client', lambda _: client)
    claim = {'sub': 'external-sub', 'iss': 'https://issuer.test', 'aud': 'demo', 'iat': int(time.time()), 'exp': int(time.time()) + 60, 'role': 'admin'}
    token = jwt.encode(claim, key, algorithm='RS256')
    assert oidc_identity(token)['role'] == 'customer'
    wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with pytest.raises(HTTPException) as exc:
        oidc_identity(jwt.encode(claim, wrong_key, algorithm='RS256'))
    assert exc.value.status_code == 401


def test_cross_encoder_order_keeps_cosine_score(monkeypatch):
    from app.rag import rerank
    from app.rag.vector_store import SearchHit
    monkeypatch.setenv('RERANKER', 'cross_encoder')
    encoder = Mock()
    encoder.predict.return_value = [-1.0, 2.0]
    monkeypatch.setattr(rerank, 'cross_encoder', lambda _: encoder)
    hits = [SearchHit('irrelevant', .9, {}), SearchHit('relevant', .2, {})]
    assert rerank.rerank('question', hits) == [hits[1], hits[0]]
    assert hits[1].score == .2


@pytest.mark.parametrize('content,finish,error', [('texto', 'stop', None), ('', 'stop', LLMError), ('texto', 'length', LLMTruncatedError)])
def test_optional_gguf_contract_without_loading_weights(monkeypatch, content, finish, error):
    from app.services.local_llm import LocalGGUFClient
    import threading
    client = LocalGGUFClient.__new__(LocalGGUFClient)
    client.lock = threading.Lock()
    client.model = Mock()
    client.model.create_chat_completion.return_value = {'choices': [{'message': {'content': content}, 'finish_reason': finish}], 'usage': {'prompt_tokens': 5, 'completion_tokens': 2}}
    if error:
        with pytest.raises(error):
            client.generate_structured('system', 'question', {'type': 'object'})
    else:
        reset_provider_usage()
        assert client.generate_structured('system', 'question', {'type': 'object'}) == content
        assert get_provider_usage() == {'input_tokens': 5, 'output_tokens': 2}
        assert client.model.create_chat_completion.call_args.kwargs['response_format']['schema'] == {'type': 'object'}
