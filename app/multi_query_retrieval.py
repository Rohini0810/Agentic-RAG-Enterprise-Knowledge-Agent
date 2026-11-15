
import re
from openai import OpenAI

from app.config import OLLAMA_BASE_URL, LLM_MODEL
from app.hybrid_retrieval import (
    hybrid_search,
    reciprocal_rank_fusion
)
from app.reranking import rerank_documents


# Connect to Ollama using its OpenAI-compatible API
client = OpenAI(
    base_url=f"{OLLAMA_BASE_URL}/v1",
    api_key="ollama"
)


def create_reranking_query(question: str) -> str:

    
    prompt = f"""
You are an enterprise search query rewriting assistant.

Rewrite the user's question into a clearer search query.

STRICT RULES:
1. Preserve the exact meaning of the original question.
2. Preserve every distinct information requirement.
3. Preserve numbers, dates, conditions and constraints.
4. Do not add technical terminology.
5. Do not mention AI, LLMs, Cross-Encoders,
   retrieval systems or document management systems.
6. Do not introduce new topics or assumptions.
7. Do not answer the question.
8. Return only the rewritten query.

Original question:
{question}

Rewritten query:
"""


    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    rewritten_query = response.choices[0].message.content or ""

    return rewritten_query.strip() or question

    

def generate_multiple_queries(
    question: str,
    num_queries: int = 3
) -> list[str]:

    prompt = f"""
You are an enterprise knowledge-base search assistant.

Your task is to break the user's question into distinct
information requirements and generate search queries.

STRICT RULES:

1. Identify only information requirements explicitly
   mentioned or clearly implied by the user's question.
2. Each query must cover a different requirement.
3. Do not introduce unrelated topics or assumptions.
4. Do not force a fixed number of queries if fewer
   distinct requirements exist.
5. Generate at most {num_queries} queries.
6. Use terminology likely to appear in enterprise documents.
7. Preserve the user's original intent.
8. Do not answer the question.
9. Return one query per line.
10. Do not number the queries.

Examples:

Question: Can I WFH three days and what security rules apply?

Queries:
Remote work eligibility and weekly work-from-home limits
Security requirements for employees working remotely

Question: What is the expense claim deadline and approval process?

Queries:
Expense claim submission deadline
Expense claim approval and reimbursement process

Question: How many annual leave days do employees receive?

Queries:
Annual paid leave entitlement for employees

User question:
{question}

Search queries:
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content or ""

    queries = [
        re.sub(r"^\s*[-*\d.)]+\s*", "", line).strip()
        for line in content.splitlines()
        if line.strip()
    ]

    queries = [
        query
        for query in queries
        if query and query.lower() != question.lower()
    ]

    return list(dict.fromkeys(queries))[:num_queries]


def multi_query_retrieve(
    question: str,
    candidate_count: int = 10,
    top_k: int = 3,
    score_threshold: float | None = None
) -> list[dict]:

    # Step 1: Generate alternative search queries
    queries = generate_multiple_queries(question)

    print("\nGenerated queries:")

    for query in queries:
        print("-", query)

    # Step 2: Include the original question
    all_queries = list(dict.fromkeys([question] + queries))

    rankings = []
    document_lookup = {}

    # Step 3: Retrieve candidates for every query
    for query in all_queries:

        results = hybrid_search(
            query=query,
            top_k=candidate_count
        )

        ranking = []

        for result in results:
            document_id = result["id"]

            ranking.append(document_id)

            document_lookup[document_id] = result

        rankings.append(ranking)

    # Step 4: Combine rankings using Reciprocal Rank Fusion
    fused_scores = reciprocal_rank_fusion(rankings)

    ranked_ids = sorted(
        fused_scores,
        key=fused_scores.get,
        reverse=True
    )[:candidate_count]

    # Step 5: Build the combined candidate list
    candidates = []

    for document_id in ranked_ids:

        result = document_lookup[document_id].copy()

        result["multi_query_rrf_score"] = fused_scores[document_id]

        candidates.append(result)

    # Step 6: Inspect candidates before reranking
    print("\nCandidates before reranking:")

    for item in candidates:
        print(f"Source: {item['metadata']['source']}")
        print(f"RRF Score: {item['multi_query_rrf_score']}")
        print(f"Document: {item['document'][:150]}")
        print("-" * 50)

    # Step 7: Rerank candidates against the reranked query
    reranking_query = create_reranking_query(question)

    print("\nReranking query:")
    print(reranking_query)
    
    ranked_results = rerank_documents(
        query=reranking_query,
        documents=candidates,
        top_k=len(candidates)
)

    if score_threshold is not None:
        ranked_results = [
        result for result in ranked_results
        if result["rerank_score"] >= score_threshold
    ]

    return ranked_results[:top_k]


if __name__ == "__main__":

    question = "What is the expense claim deadline and approval process?"

    results = multi_query_retrieve(
        question=question,
        candidate_count=10,
        top_k=3,
        score_threshold=-5
    )

    print("\nFinal retrieved documents:")

    for result in results:
        print("\nDocument:", result["document"])
        print("Source:", result["metadata"]["source"])
        print("Multi-query RRF score:", result["multi_query_rrf_score"])
        print("Rerank score:", result["rerank_score"])
