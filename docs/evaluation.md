# Retrieval Evaluation and Experiments

## Objective and scope

The current evaluation asks whether retrieval returns chunks whose source files are labelled relevant. It does not measure generated-answer correctness, faithfulness, completeness, or user satisfaction.

## Dataset

`data/evaluation_dataset.json` contains five questions and expected source filenames.

| Topic | Expected sources |
|---|---|
| Annual leave entitlement | `leave_policy.txt`, `employee_benefits.txt` |
| Remote-work security | `remote_work_policy.txt`, `security_policy.txt` |
| Expense deadline and approval | `expense_policy.txt` |
| Employee benefits | `employee_benefits.txt` |
| Security practices | `security_policy.txt` |

The data is synthetic and manually labelled. It is a development smoke/evaluation set, not a representative enterprise benchmark.

## Evaluation workflow

```mermaid
flowchart TD
  A[Load evaluation dataset] --> B[For each question]
  B --> C[Run multi-query retrieval]
  C --> D[Ranked chunks]
  D --> E[Convert chunks to unique source names]
  E --> F[Compare with relevant source labels]
  F --> P[Precision@3]
  F --> R[Recall@3]
  F --> M[Reciprocal Rank]
  P --> AGG[Aggregate]
  R --> AGG
  M --> AGG
  AGG --> OUT[Print summary]
```

The runner is `app/evaluate_retrieval.py`; metric functions are in `app/evaluation.py`.

## Metrics

### Precision@K

`relevant retrieved items in top K / K`

Measures how much of the returned top-K list is relevant. The current implementation uses K as the denominator even when fewer than K unique sources are returned.

### Recall@K

`relevant retrieved items in top K / total relevant items`

Measures how much of the known relevant source set was recovered.

### Reciprocal Rank

`1 / rank of first relevant result`, or zero if none appears.

### Mean Reciprocal Rank

Average reciprocal rank across all questions.

## Recorded baseline

| Metric | Result |
|---|---:|
| Precision@3 | 0.47 |
| Recall@3 | 1.00 |
| MRR | 0.90 |

On this five-question set, Recall@3 of 1.00 means all labelled relevant source files appeared within the top three source positions. Precision@3 of 0.47 indicates some returned positions were not labelled relevant. MRR of 0.90 indicates the first relevant source generally ranked near the top.

These are recorded development observations, not a guarantee on other corpora.

## Cross-Encoder threshold experiment

Thresholds tested: `-5, -3, -1, 0, 1, 2, 3`.

| Threshold | Precision@3 | Recall@3 | Questions with results |
|---:|---:|---:|---:|
| -5 | 0.47 | 1.00 | 5/5 |
| -3 | 0.40 | 0.90 | 5/5 |
| -1 | 0.40 | 0.90 | 5/5 |
| 0 | 0.33 | 0.80 | 5/5 |
| 1 | 0.33 | 0.80 | 5/5 |
| 2 | 0.27 | 0.70 | 4/5 |
| 3 | 0.27 | 0.70 | 4/5 |

The higher thresholds removed candidates but also removed relevant sources. -5 retained the best observed coverage on this dataset and is the experimental threshold currently passed by the RAG pipeline.

A Cross-Encoder score is not a probability. This threshold is not calibrated for a different corpus, model, or workload.

## Reproduce

Ensure Ollama models are available and the configured ChromaDB collection has been ingested.

```bash
python -m app.evaluate_retrieval
python -m app.threshold_experiment
```

Results can change if model versions, source files, chunking, or dependencies change.

## What is not measured

- Answer factuality and faithfulness.
- Citation entailment at chunk/page level.
- Completeness for multi-part questions.
- Prompt-injection robustness.
- Latency distributions on representative traffic.
- Token usage and cost.
- User satisfaction.
- Performance on a large, diverse, frequently changing corpus.

## Recommended evaluation evolution

1. Expand queries with paraphrases, ambiguous and multi-part questions, and out-of-domain questions.
2. Add documents and source relevance annotations.
3. Compare dense-only, BM25-only, hybrid, and reranked retrieval.
4. Preserve per-query results and dataset/model/config versions.
5. Add human or model-assisted answer correctness and faithfulness review.
6. Build adversarial prompt-injection tests.
7. Measure cold-start and warm latency separately.
8. Use a representative corpus before calibrating relevance thresholds.

A metric on five questions demonstrates behavior on those questions only. It is not evidence of production readiness.
