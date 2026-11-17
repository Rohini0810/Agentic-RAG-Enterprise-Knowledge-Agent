
import json
from openai import OpenAI

from app.config import OLLAMA_BASE_URL, LLM_MODEL


client = OpenAI(
    base_url=f"{OLLAMA_BASE_URL}/v1",
    api_key="ollama"
)


VALID_STRATEGIES = {"single_query", "multi_query"}


def decide_retrieval_strategy(question: str) -> dict:

    # Step 1: Validate user input
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    prompt = f"""
You are an intelligent retrieval routing assistant.

Analyze the user's question and select the appropriate
retrieval strategy.

Available strategies:

1. single_query:
Use when the question asks for one clear information
requirement that can be searched using one query.

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

    try:

        # Step 2: Ask the LLM to classify the question
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content or ""

        # Step 3: Parse the JSON response
        decision = json.loads(content)

        # Step 4: Validate the selected strategy
        strategy = decision.get("strategy")

        if strategy not in VALID_STRATEGIES:
            raise ValueError("Unsupported retrieval strategy.")

        reason = decision.get("reason")

        if not isinstance(reason, str) or not reason.strip():
            reason = "Strategy selected by the retrieval router."

        return {
            "strategy": strategy,
            "reason": reason.strip()
        }

    except (json.JSONDecodeError, ValueError, TypeError, AttributeError):

        # Step 5: Safe fallback for invalid LLM responses
        return {
            "strategy": "multi_query",
            "reason": "Invalid routing response. Falling back to multi-query retrieval."
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
