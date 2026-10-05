from app.agents.router import RouterAgent
from app.models.routing import AgentName
from app.services.llm import DisabledLLMClient
from app.config import Settings
from pathlib import Path


def settings() -> Settings:
    return Settings("x","test","INFO","disabled","http://localhost:11434","m","e",1,0.55,4,0.1,(),3,True,Path('.'),Path('.'))


def test_router_getnet_product():
    d = RouterAgent(settings(), DisabledLLMClient()).route("What's the difference between Get Smart and Get Clássica?")
    assert d.agent == AgentName.KNOWLEDGE
    assert d.confidence >= .55


def test_router_general_current_question():
    d = RouterAgent(settings(), DisabledLLMClient()).route("What's the euro exchange rate today?")
    assert d.agent == AgentName.KNOWLEDGE


def test_router_support_account_specific():
    d = RouterAgent(settings(), DisabledLLMClient()).route("When will the money from my sales be deposited?")
    assert d.agent == AgentName.SUPPORT


def test_router_machine_troubleshooting():
    d = RouterAgent(settings(), DisabledLLMClient()).route("My card machine won't connect to the internet")
    assert d.agent == AgentName.SUPPORT


def test_router_ambiguous_escalates():
    d = RouterAgent(settings(), DisabledLLMClient()).route("Can you help me with something?")
    assert d.agent == AgentName.ESCALATION


def test_router_payment_link_in_english():
    d = RouterAgent(settings(), DisabledLLMClient()).route("Can I sell through WhatsApp using the Payment Link?")
    assert d.agent == AgentName.KNOWLEDGE


def test_router_general_knowledge_question():
    d = RouterAgent(settings(), DisabledLLMClient()).route("What is the capital of Argentina?")
    assert d.agent == AgentName.KNOWLEDGE


def test_router_pix_policy_question_is_knowledge():
    d = RouterAgent(settings(), DisabledLLMClient()).route("Do I need a bank account to receive my sales via Pix?")
    assert d.agent == AgentName.KNOWLEDGE
