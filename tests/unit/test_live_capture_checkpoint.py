import json
from unittest.mock import Mock
import pytest
import requests
from evaluation import live


def test_unavailable_service_preserves_failure_record(tmp_path, monkeypatch):
    target = tmp_path / 'capture.json'
    monkeypatch.setattr('sys.argv', ['live', '--output', str(target), '--repetitions', '1'])
    monkeypatch.setattr(live.requests, 'get', Mock(side_effect=requests.ConnectionError('sensitive URL must not be echoed')))
    with pytest.raises(SystemExit):
        live.main()
    data = json.loads(target.read_text())
    assert data['status'] == 'failed'
    assert data['error_type'] == 'ConnectionError'
    assert data['rows'] == []
    assert data['quality_status'] == 'pending_factual_review'
    assert 'sensitive' not in target.read_text()


def test_interruption_preserves_current_scenario_completed_turn(tmp_path, monkeypatch):
    from argparse import Namespace
    target = tmp_path / 'capture.json'
    response = Mock()
    response.json.return_value = {'llm_provider': 'ollama'}
    monkeypatch.setattr(live.requests, 'get', Mock(return_value=response))
    login = Mock()
    login.json.return_value = {'access_token': 'secret'}
    answer = Mock(status_code=200)
    answer.json.return_value = {'session_id':'s', 'metadata': {'generation_kind':'llm'}}
    monkeypatch.setattr(live.requests, 'post', Mock(side_effect=[login, answer, KeyboardInterrupt]))
    monkeypatch.setenv('DEMO_PASSWORD', 'private')
    with pytest.raises(KeyboardInterrupt):
        live.capture(Namespace(timeout=1, repetitions=1), 'http://localhost',
                     [{'id':'x','turns':['first','second']}], target, {'rows':[]})
    data = json.loads(target.read_text())
    assert len(data['rows'][0]['results']) == 1
    assert 'secret' not in target.read_text() and 'private' not in target.read_text()
