from types import SimpleNamespace

from app.retrieval_router import decide_retrieval_strategy


def mock_llm_response(content):
    """Create a fake response with the same structure as the Ollama response."""
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content)
            )
        ]
    )


def test_router_selects_single_query(monkeypatch):
    """A question with one information requirement should use single_query."""

    monkeypatch.setattr(
        "app.retrieval_router.client.chat.completions.create",
        lambda **kwargs: mock_llm_response(
            '{"strategy": "single_query", "reason": "One information requirement"}'
        )
    )

    result = decide_retrieval_strategy("How many annual leave days do employees receive?")

    assert result["strategy"] == "single_query"


def test_router_selects_multi_query(monkeypatch):
    """A question with multiple information requirements should use multi_query."""

    monkeypatch.setattr(
        "app.retrieval_router.client.chat.completions.create",
        lambda **kwargs: mock_llm_response(
            '{"strategy": "multi_query", "reason": "Two information requirements"}'
        )
    )

    result = decide_retrieval_strategy(
        "Can I work remotely and what security rules apply?"
    )

    assert result["strategy"] == "multi_query"


def test_router_falls_back_on_invalid_json(monkeypatch):
    """Invalid JSON from the LLM should trigger the fallback strategy."""

    monkeypatch.setattr(
        "app.retrieval_router.client.chat.completions.create",
        lambda **kwargs: mock_llm_response("This is not valid JSON")
    )

    result = decide_retrieval_strategy("What is the leave policy?")

    assert result["strategy"] == "multi_query"
    assert "falling back" in result["reason"].lower()


def test_router_falls_back_on_unsupported_strategy(monkeypatch):
    """An unsupported strategy should trigger the fallback."""

    monkeypatch.setattr(
        "app.retrieval_router.client.chat.completions.create",
        lambda **kwargs: mock_llm_response(
            '{"strategy": "vector_search", "reason": "Unsupported strategy"}'
        )
    )

    result = decide_retrieval_strategy("What is the leave policy?")

    assert result["strategy"] == "multi_query"
    assert "falling back" in result["reason"].lower()
    
import pytest


def test_router_rejects_empty_question():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        decide_retrieval_strategy("")


def test_router_rejects_whitespace_question():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        decide_retrieval_strategy("   ")