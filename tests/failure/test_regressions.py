from dataclasses import replace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.agents.knowledge import KnowledgeAgent
from app.agents.router import RouterAgent
from app.config import get_settings
from app.models.api import ChatRequest
from app.models.routing import AgentName
from app.models.tools import SourceItem, ToolResult
from app.services.embeddings import EmbeddingError
from app.services.llm import DisabledLLMClient, LLMError
from app.tools.rag_search import RAGSearchTool
from evaluation.run import build_orchestrator


@pytest.mark.parametrize('message', ['  a  ', '   ', 123])
def test_input_validation_after_trim(message):
    with pytest.raises(ValidationError):
        ChatRequest(message=message, user_id='cliente1988')


def test_embedding_outage_returns_tool_failure():
    retriever = Mock()
    retriever.retrieve.side_effect = EmbeddingError('unavailable')
    result = RAGSearchTool(retriever).run('Getnet products')
    assert not result.success


def test_web_failure_is_called_once_and_escalates():
    rag = Mock(name='rag'); rag.name = 'rag_search'
    rag.run.return_value = ToolResult(success=False, error='missing index')
    web = Mock(name='web'); web.name = 'web_search'
    web.run.return_value = ToolResult(success=False, error='network unavailable')
    result = KnowledgeAgent(rag, web, DisabledLLMClient()).handle('Getnet products')
    assert result.escalated
    assert result.metadata['fallback'] == 'no_evidence'
    web.run.assert_called_once()


def test_snippetless_web_does_not_claim_resolution():
    web = Mock(); web.name = 'web_search'
    web.run.return_value = ToolResult(success=True, sources=[SourceItem(title='No text', url='https://example.test', snippet='')])
    result = KnowledgeAgent(Mock(), web, DisabledLLMClient()).handle('weather today')
    assert result.escalated


@pytest.mark.parametrize('output', ['not json', '{"agent":"wrong","confidence":0.9,"reason":"test"}'])
def test_invalid_llm_route_falls_back(output):
    llm = Mock(); llm.generate.return_value = output
    settings = replace(get_settings(), llm_provider='ollama')
    result = RouterAgent(settings, llm).route('Qual é a capital da Argentina?')
    assert result.agent == AgentName.KNOWLEDGE
    assert result.source != 'llm'


def test_llm_outage_uses_deterministic_route():
    llm = Mock(); llm.generate.side_effect = LLMError('unavailable')
    result = RouterAgent(replace(get_settings(), llm_provider='ollama'), llm).route('Quando minhas vendas serão depositadas?')
    assert result.agent == AgentName.SUPPORT


@pytest.mark.parametrize('message', ['Minha transação foi recusada', 'Minhas vendas não caíram', 'Minha maquininha não conecta'])
def test_portuguese_support_inflections(message):
    result = RouterAgent(replace(get_settings(), llm_provider='disabled'), DisabledLLMClient()).route(message)
    assert result.agent == AgentName.SUPPORT


def test_portuguese_pix_policy_is_knowledge():
    result = RouterAgent(replace(get_settings(), llm_provider='disabled'), DisabledLLMClient()).route('Como funciona o Pix?')
    assert result.agent == AgentName.KNOWLEDGE


def test_handoff_preserves_reason_and_origin(tmp_path, caplog):
    orchestrator = build_orchestrator(tmp_path / 'index')
    with caplog.at_level('INFO'):
        result = orchestrator.handle(ChatRequest(message='When will my sales be deposited?', user_id='unknown'))
    assert result.metadata['previous_agent'] == 'support'
    assert result.metadata['previous_tool'] == 'customer_lookup'
    assert result.metadata['handoff_reason'] == 'customer_not_verified'
    assert result.metadata['ticket_created'] is False
    record = next(r for r in caplog.records if r.getMessage() == 'request_completed')
    assert record.event_data['handoff_reason'] == 'customer_not_verified'
    assert record.event_data['resolved'] is False


def test_offline_evaluation_never_invokes_configured_ollama(tmp_path, monkeypatch):
    import evaluation.run as runner
    monkeypatch.setattr(runner, 'get_settings', lambda: replace(get_settings(), llm_provider='ollama'))
    orchestrator = runner.build_orchestrator(tmp_path / 'index')
    assert orchestrator.router.settings.llm_provider == 'disabled'


def test_portuguese_settlement_uses_payment_tool(tmp_path):
    result = build_orchestrator(tmp_path / 'index').handle(ChatRequest(message='Minhas vendas não caíram', user_id='cliente1988'))
    assert result.agent == 'support'
    assert result.tool == 'payment_status'


def test_ollama_index_provider_is_not_changed_by_disabled_chat(tmp_path, monkeypatch):
    import app.dependencies as dependencies
    index = tmp_path / 'index'
    index.mkdir()
    (index / 'embedding_provider.txt').write_text('ollama')
    monkeypatch.setattr(dependencies, 'get_settings', lambda: replace(get_settings(), llm_provider='disabled', index_dir=index))
    dependencies.get_orchestrator.cache_clear()
    try:
        orchestrator = dependencies.get_orchestrator()
        from app.services.embeddings import OllamaEmbeddingService
        assert isinstance(orchestrator.knowledge.rag.retriever.embeddings, OllamaEmbeddingService)
    finally:
        dependencies.get_orchestrator.cache_clear()
