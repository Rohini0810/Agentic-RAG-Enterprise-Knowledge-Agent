
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "X-Request-ID" in response.headers


def test_ask_endpoint_success(monkeypatch):

    captured = {}

    # Mock RAG pipeline and capture the request ID.
    def mock_ask_question(question, request_id=None):
        captured["question"] = question
        captured["request_id"] = request_id

        return {
            "answer": "Employees receive 20 days of annual paid leave.",
            "sources": ["leave_policy.txt"]
        }

    monkeypatch.setattr(
        "app.main.ask_question",
        mock_ask_question
    )

    response = client.post(
        "/ask",
        json={
            "question": "How many annual leave days do employees receive?"
        }
    )

    assert response.status_code == 200

    assert response.json()["answer"] == (
        "Employees receive 20 days of annual paid leave."
    )

    assert response.json()["sources"] == ["leave_policy.txt"]

    # Verify request ID tracking.
    assert "X-Request-ID" in response.headers
    assert captured["request_id"] == response.headers["X-Request-ID"]
    assert captured["question"] == (
        "How many annual leave days do employees receive?"
    )


def test_ask_endpoint_rejects_empty_question():
    response = client.post(
        "/ask",
        json={"question": ""}
    )

    assert response.status_code == 422


def test_ask_endpoint_rejects_missing_question():
    response = client.post(
        "/ask",
        json={}
    )

    assert response.status_code == 422


def test_request_ids_are_unique(monkeypatch):

    def mock_ask_question(question, request_id=None):
        return {
            "answer": "Test answer",
            "sources": []
        }

    monkeypatch.setattr(
        "app.main.ask_question",
        mock_ask_question
    )

    response_1 = client.post(
        "/ask",
        json={"question": "First enterprise question"}
    )

    response_2 = client.post(
        "/ask",
        json={"question": "Second enterprise question"}
    )

    request_id_1 = response_1.headers["X-Request-ID"]
    request_id_2 = response_2.headers["X-Request-ID"]

    assert request_id_1 != request_id_2
