from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"


def test_chat(monkeypatch):
    monkeypatch.setattr(
        "app.main.router_agent.handle",
        lambda user_id, message: {
            "agent": "knowledge",
            "answer": "Resposta de teste",
            "sources": []
        }
    )

    response = client.post(
        "/chat",
        json={
            "message": "Pergunta de teste",
            "user_id": "cliente1988"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["agent"] == "knowledge"
    assert data["answer"] == "Resposta de teste"