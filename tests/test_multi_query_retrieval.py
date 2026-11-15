from app.multi_query_retrieval import multi_query_retrieve


def test_threshold_filters_irrelevant_documents(monkeypatch):
    candidates = [
        {
            "id": "1",
            "document": "Expense claims need manager approval.",
            "metadata": {"source": "expense_policy.txt"},
            "rerank_score": 4.9
        },
        {
            "id": "2",
            "document": "Employees receive health insurance.",
            "metadata": {"source": "employee_benefits.txt"},
            "rerank_score": -10.0
        }
    ]

    monkeypatch.setattr(
        "app.multi_query_retrieval.generate_multiple_queries",
        lambda question: []
    )

    monkeypatch.setattr(
        "app.multi_query_retrieval.hybrid_search",
        lambda **kwargs: candidates
    )

    monkeypatch.setattr(
        "app.multi_query_retrieval.rerank_documents",
        lambda **kwargs: candidates
    )

    monkeypatch.setattr(
        "app.multi_query_retrieval.create_reranking_query",
        lambda question: question
    )

    results = multi_query_retrieve(
        question="What is the expense approval process?",
        top_k=3,
        score_threshold=-5
    )

    assert len(results) == 1
    assert results[0]["metadata"]["source"] == "expense_policy.txt"


def test_none_threshold_disables_filtering(monkeypatch):
    candidates = [
        {
            "id": "1",
            "document": "Relevant document.",
            "metadata": {"source": "expense_policy.txt"},
            "rerank_score": 4.9
        },
        {
            "id": "2",
            "document": "Less relevant document.",
            "metadata": {"source": "employee_benefits.txt"},
            "rerank_score": -10.0
        }
    ]

    monkeypatch.setattr(
        "app.multi_query_retrieval.generate_multiple_queries",
        lambda question: []
    )
    monkeypatch.setattr(
        "app.multi_query_retrieval.hybrid_search",
        lambda **kwargs: candidates
    )
    monkeypatch.setattr(
        "app.multi_query_retrieval.rerank_documents",
        lambda **kwargs: candidates
    )
    monkeypatch.setattr(
        "app.multi_query_retrieval.create_reranking_query",
        lambda question: question
    )

    results = multi_query_retrieve(
        question="Test question",
        top_k=3,
        score_threshold=None
    )

    assert len(results) == 2


def test_empty_candidates_return_empty_list(monkeypatch):
    monkeypatch.setattr(
        "app.multi_query_retrieval.generate_multiple_queries",
        lambda question: []
    )
    monkeypatch.setattr(
        "app.multi_query_retrieval.hybrid_search",
        lambda **kwargs: []
    )

    results = multi_query_retrieve(
        question="Unknown question",
        score_threshold=-5
    )

    assert results == []