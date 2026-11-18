
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


def test_out_of_scope_question_skips_retrieval(monkeypatch):
    from app import rag_pipeline

    def unexpected_retrieval(*args, **kwargs):
        raise AssertionError("Retrieval should not run for out-of-scope questions")

    monkeypatch.setattr(
        rag_pipeline,
        "decide_retrieval_strategy",
        unexpected_retrieval
    )

    result = rag_pipeline.ask_question("What's the weather today?")

    assert result["sources"] == []
    assert "Enterprise Knowledge Assistant" in result["answer"]
