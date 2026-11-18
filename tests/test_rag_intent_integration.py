
from app.rag_pipeline import ask_question


def test_greeting_bypasses_rag(monkeypatch):

    def fail_if_called(*args, **kwargs):
        raise AssertionError("RAG retrieval should not run for greetings")

    monkeypatch.setattr(
        "app.rag_pipeline.decide_retrieval_strategy",
        fail_if_called
    )

    result = ask_question("Hi")

    assert "Hello!" in result["answer"]
    assert result["sources"] == []


def test_empty_question_returns_validation_message():

    result = ask_question("")

    assert result["answer"] == "Please enter a valid question."
    assert result["sources"] == []
