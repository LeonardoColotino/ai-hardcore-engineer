"""Basic authenticated payment question must reach its tool, not generic fallback."""
from unittest.mock import Mock
import pytest
from fastapi.testclient import TestClient
from app.orchestration.intents import settlement
from app.agents.support import SupportAgent
from app.models.tools import ToolResult
from app.tools.customer_lookup import CustomerLookupTool
from app.tools.transaction_lookup import TransactionLookupTool
from app.tools.payment_status import PaymentStatusTool
from app.dependencies import get_orchestrator
from app.main import app
from evaluation.run import build_orchestrator

@pytest.mark.parametrize('message',[
    'Qual o status do meu último pagamento?',
    'Qual a situação do meu último pagamento?',
    'What is the status of my last payment?',
])
def test_personal_payment_status_uses_authenticated_owner(message,tmp_repo):
    assert settlement(message)
    agent=SupportAgent(CustomerLookupTool(tmp_repo),TransactionLookupTool(tmp_repo),PaymentStatusTool(tmp_repo))
    result=agent.handle(message,'u1')
    assert not result.escalated and result.tool=='payment_status'
    assert 'scheduled' in result.answer and result.metadata['records']==1

@pytest.mark.parametrize('message',[
    'Em qual solução a documentação menciona receber todos os pagamentos na mesma conta: Conta Digital ou Link de Pagamento?',
    'Como funciona o Pix para receber pagamentos?',
    'Quais funcionalidades permitem receber pagamentos na Conta Digital?',
])
def test_public_product_text_does_not_select_personal_settlement(message):
    assert not settlement(message)


def test_status_request_does_not_bypass_customer_verification():
    customer=Mock(name='customer_lookup')
    customer.name='customer_lookup'
    customer.run.return_value=ToolResult(success=False,error='not found')
    payment=Mock()
    result=SupportAgent(customer,Mock(),payment).handle('Qual o status do meu último pagamento?','unknown')
    assert result.escalated and result.tool=='customer_lookup'
    payment.run.assert_not_called()


def test_basic_payment_question_through_authenticated_http(tmp_path,api_auth):
    orch=build_orchestrator(tmp_path/'idx')
    app.dependency_overrides[get_orchestrator]=lambda:orch
    try:
        with TestClient(app) as client:
            headers=api_auth('cliente1988')
            r=client.post('/chat',headers=headers,json={'message':'Qual o status do meu último pagamento?'})
            assert r.status_code==200
            body=r.json()
            assert body['tool']=='payment_status' and not body['escalated']
            assert body['ticket_id'] is None and 'scheduled' in body['answer']
            denied=client.post('/chat',headers=headers,json={'message':'Qual o status do meu último pagamento?','user_id':'cliente2026'})
            assert denied.status_code==403
    finally:
        app.dependency_overrides.clear()
