
from app.hybrid_retrieval import hybrid_search
from app.reranking import rerank_documents


def advanced_retrieve(
    query: str,
    candidate_count: int = 10,
    top_k: int = 3
):
    # Stage 1: Retrieve candidate documents using hybrid search
    candidates = hybrid_search(
        query=query,
        top_k=candidate_count
    )

    # Stage 2: Rerank candidates using Cross-Encoder
    ranked_results = rerank_documents(
        query=query,
        documents=candidates,
        top_k=top_k
    )

    return ranked_results


if __name__ == "__main__":

    question = "How many annual leave days do employees receive?"

    results = advanced_retrieve(question)

    for rank, result in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print("Document:", result["document"])
        print("Source:", result["metadata"]["source"])
        print("RRF Score:", result["rrf_score"])
        print("Rerank Score:", result["rerank_score"])
