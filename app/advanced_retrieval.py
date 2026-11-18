
from app.hybrid_retrieval import hybrid_search
from app.reranking import rerank_documents


def advanced_retrieve(
    query: str,
    candidate_count: int = 10,
    top_k: int = 3,
    score_threshold: float | None = None
):
    # Stage 1: Retrieve candidates
    candidates = hybrid_search(
        query=query,
        top_k=candidate_count
    )

    if not candidates:
        return []

    # Stage 2: Rerank candidates
    ranked_results = rerank_documents(
        query=query,
        documents=candidates,
        top_k=len(candidates)
    )

    # Stage 3: Filter by relevance when a calibrated
    # threshold has been supplied
    if score_threshold is not None:
        ranked_results = [
            result
            for result in ranked_results
            if result["rerank_score"] >= score_threshold
        ]

    return ranked_results[:top_k]



if __name__ == "__main__":

    question = "How many annual leave days do employees receive?"

    results = advanced_retrieve(question)

    for rank, result in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print("Document:", result["document"])
        print("Source:", result["metadata"]["source"])
        print("RRF Score:", result["rrf_score"])
        print("Rerank Score:", result["rerank_score"])
