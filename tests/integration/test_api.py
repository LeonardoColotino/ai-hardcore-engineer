from fastapi.testclient import TestClient
from app.main import app
import pytest
from pathlib import Path
from evaluation.run import build_orchestrator
from app.dependencies import get_orchestrator


@pytest.fixture(autouse=True)
def offline_api(tmp_path):
    orchestrator = build_orchestrator(tmp_path / "index")
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    yield
    app.dependency_overrides.clear()

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_chat_validation():
    r = client.post("/chat", json={"message":"", "user_id":"x"})
    assert r.status_code == 422


def test_support_flow_uses_scoped_data():
    r = client.post("/chat", json={"message":"When will the money from my sales be deposited?", "user_id":"cliente1988"})
    assert r.status_code == 200
    body = r.json()
    assert body["agent"] == "support"
    assert body["tool"] == "payment_status"
    assert "scheduled" in body["answer"].lower()


def test_unknown_customer_escalates():
    r = client.post("/chat", json={"message":"When will my sales be deposited?", "user_id":"unknown"})
    assert r.status_code == 200
    body = r.json()
    assert body["agent"] == "escalation"
    assert body["escalated"] is True
