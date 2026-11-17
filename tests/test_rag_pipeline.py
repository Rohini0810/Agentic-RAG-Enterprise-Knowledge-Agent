
from app.rag_pipeline import ask_question


def test_ask_question_generates_answer(monkeypatch):
    """Test the single-query retrieval path and answer generation."""

    retrieved_documents = [
        {
            "document": "Employees receive 20 days of annual leave.",
            "metadata": {"source": "leave_policy.txt"},
            "rerank_score": 4.5
        },
        {
            "document": "Leave requests require manager approval.",
            "metadata": {"source": "leave_policy.txt"},
            "rerank_score": 3.2
        }
    ]

    # Force the router to select single-query retrieval.
    monkeypatch.setattr(
        "app.rag_pipeline.decide_retrieval_strategy",
        lambda question: {
            "strategy": "single_query",
            "reason": "One information requirement"
        }
    )

    # Mock the retrieval function used by single_query.
    monkeypatch.setattr(
        "app.rag_pipeline.advanced_retrieve",
        lambda **kwargs: retrieved_documents
    )

    monkeypatch.setattr(
        "app.rag_pipeline.generate_answer",
        lambda question, context: "Employees receive 20 days of annual leave."
    )

    response = ask_question("How many annual leave days do employees receive?")

    assert response["answer"] == (
        "Employees receive 20 days of annual leave."
    )

    assert response["sources"] == ["leave_policy.txt"]


def test_ask_question_handles_empty_retrieval(monkeypatch):
    """Test that the pipeline handles empty multi-query results."""

    monkeypatch.setattr(
        "app.rag_pipeline.decide_retrieval_strategy",
        lambda question: {
            "strategy": "multi_query",
            "reason": "Multiple information requirements"
        }
    )

    monkeypatch.setattr(
        "app.rag_pipeline.multi_query_retrieve",
        lambda **kwargs: []
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("LLM should not be called for empty retrieval")

    monkeypatch.setattr(
        "app.rag_pipeline.generate_answer",
        fail_if_called
    )

    response = ask_question("Unknown question")

    assert response["answer"] == (
        "I couldn't find relevant information."
    )

    assert response["sources"] == []


def test_ask_question_uses_configured_threshold(monkeypatch):
    """Test that multi-query retrieval receives the configured parameters."""

    captured_arguments = {}

    def fake_retrieve(**kwargs):
        captured_arguments.update(kwargs)

        return [
            {
                "document": "Employees receive 20 days of annual leave.",
                "metadata": {"source": "leave_policy.txt"},
                "rerank_score": 4.5
            }
        ]

    monkeypatch.setattr(
        "app.rag_pipeline.decide_retrieval_strategy",
        lambda question: {
            "strategy": "multi_query",
            "reason": "Multiple information requirements"
        }
    )

    monkeypatch.setattr(
        "app.rag_pipeline.multi_query_retrieve",
        fake_retrieve
    )

    monkeypatch.setattr(
        "app.rag_pipeline.generate_answer",
        lambda question, context: "20 days."
    )

    ask_question("What is the expense claim deadline and approval process?")

    assert captured_arguments["score_threshold"] == -5
    assert captured_arguments["candidate_count"] == 10
    assert captured_arguments["top_k"] == 3
