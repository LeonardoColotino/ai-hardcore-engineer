from app.agents.router_agent import router_agent


def test_router_support(monkeypatch):
    monkeypatch.setattr(
        "app.agents.router_agent.llm_service.generate",
        lambda prompt: "support"
    )

    route = router_agent.classify(
        "Quando vou receber o dinheiro da minha venda?"
    )

    assert route == "support"


def test_router_knowledge(monkeypatch):
    monkeypatch.setattr(
        "app.agents.router_agent.llm_service.generate",
        lambda prompt: "knowledge"
    )

    route = router_agent.classify(
        "Quais produtos a Getnet oferece?"
    )

    assert route == "knowledge"