
import json
from pathlib import Path

from app.multi_query_retrieval import multi_query_retrieve
from app.evaluation import precision_at_k, recall_at_k

THRESHOLDS = [-5, -3, -1, 0, 1, 2, 3]


def load_dataset():
    path = Path("data/evaluation_dataset.json")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_experiment():
    dataset = load_dataset()
    results_by_question = []

    # Retrieve and rerank once per question.
    for item in dataset:
        results = multi_query_retrieve(
            question=item["question"],
            candidate_count=10,
            top_k=10
        )

        results_by_question.append({
            "relevant": set(item["relevant_sources"]),
            "results": results
        })

    print("\nTHRESHOLD COMPARISON")
    print("-" * 65)
    print(
        f"{'Threshold':<12}"
        f"{'Precision@3':<16}"
        f"{'Recall@3':<14}"
        f"{'Questions with results':<22}"
    )

    for threshold in THRESHOLDS:
        precision_scores = []
        recall_scores = []
        questions_with_results = 0

        for item in results_by_question:
            relevant = item["relevant"]

            # Keep candidates whose Cross-Encoder score meets threshold.
            filtered = [
                result for result in item["results"]
                if result["rerank_score"] >= threshold
            ]

            # Convert chunks to unique source filenames.
            sources = list(dict.fromkeys(
                result["metadata"]["source"]
                for result in filtered
            ))

            if sources:
                questions_with_results += 1

            precision_scores.append(
                precision_at_k(sources, relevant, k=3)
            )
            recall_scores.append(
                recall_at_k(sources, relevant, k=3)
            )

        total = len(dataset)

        print(
            f"{threshold:<12}"
            f"{sum(precision_scores) / total:<16.2f}"
            f"{sum(recall_scores) / total:<14.2f}"
            f"{questions_with_results}/{total:<22}"
        )


if __name__ == "__main__":
    run_experiment()
