
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ask_endpoint_success(monkeypatch):
    # Mock the RAG pipeline so this test focuses on the API.
    def mock_ask_question(question):
        return {
            "answer": "Employees receive 20 days of annual paid leave.",
            "sources": ["leave_policy.txt"]
        }

    monkeypatch.setattr("app.main.ask_question", mock_ask_question)

    response = client.post(
        "/ask",
        json={"question": "How many annual leave days do employees receive?"}
    )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "Employees receive 20 days of annual paid leave."
    )
    assert response.json()["sources"] == ["leave_policy.txt"]


def test_ask_endpoint_rejects_empty_question():
    response = client.post("/ask", json={"question": ""})

    assert response.status_code == 422


def test_ask_endpoint_rejects_missing_question():
    response = client.post("/ask", json={})

    assert response.status_code == 422
