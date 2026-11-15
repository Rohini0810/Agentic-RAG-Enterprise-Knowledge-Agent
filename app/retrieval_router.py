#Its responsibility will be to analyze a question and choose:
#- single_query — for straightforward questions.
#- multi_query — for questions involving multiple information requirements.

# We'll call this component the Retrieval Router. 
# Its job is to decide which retrieval strategy is appropriate for each question.

# Example 1: Simple question
#"How many annual leave days do employees receive?"
#single_query
#One search query is sufficient.

#Example 2: Complex question
#"Can I work remotely, and what security rules apply?"
#multi_query
#Two distinct information requirements need to be searched.


import json
from openai import OpenAI

from app.config import OLLAMA_BASE_URL, LLM_MODEL


# Connect to Ollama through its OpenAI-compatible API
client = OpenAI(
    base_url=f"{OLLAMA_BASE_URL}/v1",
    api_key="ollama"
)


def decide_retrieval_strategy(question: str) -> dict:

    prompt = f"""
You are an intelligent retrieval routing assistant.

Analyze the user's question and decide which retrieval
strategy should be used.

Available strategies:

1. single_query:
Use when the question asks for one clear piece of
information that can be retrieved using one search query.

2. multi_query:
Use when the question contains multiple distinct
information requirements that may need separate searches.

Rules:
- Preserve the user's intent.
- Do not answer the question.
- Do not invent additional requirements.
- Return valid JSON only.

Expected JSON format:

{{
    "strategy": "single_query or multi_query",
    "reason": "Brief explanation"
}}

User question:
{question}
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content or ""

    try:
        decision = json.loads(content)

        if decision.get("strategy") not in [
            "single_query",
            "multi_query"
        ]:
            raise ValueError("Invalid retrieval strategy")

        return decision

    except (json.JSONDecodeError, ValueError):
        return {
            "strategy": "multi_query",
            "reason": "Could not confidently classify the question. Using multi-query retrieval as a fallback."
        }


if __name__ == "__main__":

    questions = [
        "How many annual leave days do employees receive?",
        "Can I work remotely and what security rules apply?"
    ]

    for question in questions:

        decision = decide_retrieval_strategy(question)

        print("\nQuestion:", question)
        print("Strategy:", decision["strategy"])
        print("Reason:", decision["reason"])
