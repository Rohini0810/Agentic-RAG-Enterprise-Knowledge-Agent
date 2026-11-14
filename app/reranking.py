
from sentence_transformers import CrossEncoder

# Load the pretrained reranking model
MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(MODEL_NAME)


def rerank_documents(
    query: str,
    documents: list[dict],
    top_k: int = 3
) -> list[dict]:

    if not documents:
        return []

    # Create query-document pairs
    pairs = [
        (query, document["document"])
        for document in documents
    ]

    # Calculate relevance scores
    scores = reranker.predict(pairs)

    # Attach scores to documents
    for document, score in zip(documents, scores):
        document["rerank_score"] = float(score)

    # Sort by relevance score, highest first
    ranked_documents = sorted(
        documents,
        key=lambda item: item["rerank_score"],
        reverse=True
    )

    return ranked_documents[:top_k]


if __name__ == "__main__":

    query = "How many annual leave days do employees receive?"

    sample_documents = [
        {
            "document": "Employees receive 20 days of annual paid leave.",
            "metadata": {"source": "leave_policy.txt"}
        },
        {
            "document": "Employees can work remotely up to three days per week.",
            "metadata": {"source": "remote_work_policy.txt"}
        },
        {
            "document": "Employees must submit expense claims within 30 days.",
            "metadata": {"source": "expense_policy.txt"}
        }
    ]

    results = rerank_documents(
        query,
        sample_documents,
        top_k=3
    )

    for result in results:
        print("\nDocument:", result["document"])
        print("Source:", result["metadata"]["source"])
        print("Rerank score:", result["rerank_score"])
