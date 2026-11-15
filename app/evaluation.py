
def precision_at_k(
    retrieved_documents: list[str],
    relevant_documents: set[str],
    k: int
) -> float:

    if k <= 0:
        raise ValueError("k must be greater than zero")

    if not relevant_documents:
        return 0.0

    top_k_documents = retrieved_documents[:k]

    if not top_k_documents:
        return 0.0

    relevant_retrieved = sum(
        1
        for document in top_k_documents
        if document in relevant_documents
    )

    return relevant_retrieved / k


def recall_at_k(
    retrieved_documents: list[str],
    relevant_documents: set[str],
    k: int
) -> float:

    if k <= 0:
        raise ValueError("k must be greater than zero")

    if not relevant_documents:
        return 0.0

    top_k_documents = retrieved_documents[:k]

    relevant_retrieved = sum(
        1
        for document in top_k_documents
        if document in relevant_documents
    )

    return relevant_retrieved / len(relevant_documents)


def reciprocal_rank(
    retrieved_documents: list[str],
    relevant_documents: set[str]
) -> float:

    for rank, document in enumerate(retrieved_documents, start=1):

        if document in relevant_documents:
            return 1 / rank

    return 0.0


def mean_reciprocal_rank(
    search_results: list[list[str]],
    relevant_results: list[set[str]]
) -> float:

    if len(search_results) != len(relevant_results):
        raise ValueError(
            "Search results and relevant results must have equal length"
        )

    if not search_results:
        return 0.0

    reciprocal_ranks = [
        reciprocal_rank(retrieved, relevant)
        for retrieved, relevant in zip(search_results, relevant_results)
    ]

    return sum(reciprocal_ranks) / len(reciprocal_ranks)


if __name__ == "__main__":

    retrieved = [
        "expense_policy.txt",
        "leave_policy.txt",
        "employee_benefits.txt"
    ]

    relevant = {
        "leave_policy.txt",
        "employee_benefits.txt"
    }

    precision = precision_at_k(retrieved, relevant, k=3)
    recall = recall_at_k(retrieved, relevant, k=3)

    search_results = [
        ["expense_policy.txt", "leave_policy.txt"],
        ["employee_benefits.txt", "security_policy.txt"]
    ]

    relevant_results = [
        {"leave_policy.txt"},
        {"employee_benefits.txt"}
    ]

    mrr = mean_reciprocal_rank(
        search_results,
        relevant_results
    )

    print("Precision@3:", precision)
    print("Recall@3:", recall)
    print("MRR:", mrr)
