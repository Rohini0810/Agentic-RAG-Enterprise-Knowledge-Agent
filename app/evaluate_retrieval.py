
import json
from pathlib import Path

from app.multi_query_retrieval import multi_query_retrieve
from app.evaluation import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def load_evaluation_dataset():
    dataset_path = Path("data/evaluation_dataset.json")

    with dataset_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_retrieval():
    dataset = load_evaluation_dataset()

    precision_scores = []
    recall_scores = []
    reciprocal_rank_scores = []

    for item in dataset:
        question = item["question"]
        relevant_sources = set(item["relevant_sources"])

        print("\n" + "=" * 60)
        print("Question:", question)

        results = multi_query_retrieve(
            question=question,
            candidate_count=10,
            top_k=10
        )

        print("\nReranking score distribution:")

        for rank, result in enumerate(results, start=1):
            print(
        f"Rank: {rank} | "
        f"Source: {result['metadata']['source']} | "
        f"Score: {result['rerank_score']:.4f}"
    )
    
        # Extract unique source filenames, preserving their rank.
        retrieved_sources = list(dict.fromkeys(
            result["metadata"]["source"]
            for result in results
        ))

        precision = precision_at_k(
            retrieved_sources, relevant_sources, k=3
        )
        recall = recall_at_k(
            retrieved_sources, relevant_sources, k=3
        )
        rr = reciprocal_rank(
            retrieved_sources, relevant_sources
        )

        precision_scores.append(precision)
        recall_scores.append(recall)
        reciprocal_rank_scores.append(rr)

        print("Retrieved:", retrieved_sources)
        print("Expected:", sorted(relevant_sources))
        print(f"Precision@3: {precision:.2f}")
        print(f"Recall@3: {recall:.2f}")
        print(f"Reciprocal Rank: {rr:.2f}")

    total = len(dataset)

    print("\n" + "=" * 60)
    print("FINAL EVALUATION RESULTS")
    print("=" * 60)
    print(f"Questions evaluated: {total}")
    print(f"Average Precision@3: {sum(precision_scores) / total:.2f}")
    print(f"Average Recall@3: {sum(recall_scores) / total:.2f}")
    print(f"Mean Reciprocal Rank: {sum(reciprocal_rank_scores) / total:.2f}")


if __name__ == "__main__":
    evaluate_retrieval()
