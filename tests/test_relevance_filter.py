
from app.advanced_retrieval import advanced_retrieve


def test_advanced_retrieval_filters_irrelevant_results(monkeypatch):

    candidates = [
        {"id": "1", "document": "Relevant leave policy"},
        {"id": "2", "document": "Irrelevant expense policy"}
    ]

    ranked_results = [
        {**candidates[0], "rerank_score": 8.5},
        {**candidates[1], "rerank_score": -7.2}
    ]

    monkeypatch.setattr(
        "app.advanced_retrieval.hybrid_search",
        lambda **kwargs: candidates
    )

    monkeypatch.setattr(
        "app.advanced_retrieval.rerank_documents",
        lambda **kwargs: ranked_results
    )

    results = advanced_retrieve(
        query="How many annual leave days?",
        score_threshold=0
    )

    assert len(results) == 1
    assert results[0]["document"] == "Relevant leave policy"


def test_advanced_retrieval_returns_empty_when_no_candidates(monkeypatch):

    monkeypatch.setattr(
        "app.advanced_retrieval.hybrid_search",
        lambda **kwargs: []
    )

    results = advanced_retrieve("Unknown question")

    assert results == []


def test_advanced_retrieval_keeps_all_results_without_threshold(monkeypatch):

    candidates = [{"id": "1"}, {"id": "2"}]

    ranked_results = [
        {**candidates[0], "rerank_score": 8.5},
        {**candidates[1], "rerank_score": -7.2}
    ]

    monkeypatch.setattr(
        "app.advanced_retrieval.hybrid_search",
        lambda **kwargs: candidates
    )

    monkeypatch.setattr(
        "app.advanced_retrieval.rerank_documents",
        lambda **kwargs: ranked_results
    )

    results = advanced_retrieve("Test question")

    assert len(results) == 2
