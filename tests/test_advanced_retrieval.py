from app.advanced_retrieval import advanced_retrieve


def test_advanced_retrieve_returns_top_results(monkeypatch):

    candidates = [
        {
            "document": "Annual leave is 20 days.",
            "metadata": {"source": "leave_policy.txt"},
            "rrf_score": 0.03
        }
    ]

    monkeypatch.setattr(
        "app.advanced_retrieval.hybrid_search",
        lambda **kwargs: candidates
    )

    monkeypatch.setattr(
        "app.advanced_retrieval.rerank_documents",
        lambda query, documents, top_k: documents[:top_k]
    )

    results = advanced_retrieve(
        "How many leave days?",
        candidate_count=10,
        top_k=3
    )

    assert len(results) == 1
    assert results[0]["metadata"]["source"] == "leave_policy.txt"


def test_advanced_retrieve_handles_no_candidates(monkeypatch):

    monkeypatch.setattr(
        "app.advanced_retrieval.hybrid_search",
        lambda **kwargs: []
    )

    monkeypatch.setattr(
        "app.advanced_retrieval.rerank_documents",
        lambda **kwargs: []
    )

    results = advanced_retrieve("Unknown question")

    assert results == []