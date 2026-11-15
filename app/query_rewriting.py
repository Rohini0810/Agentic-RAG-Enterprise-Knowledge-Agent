
from openai import OpenAI

from app.config import OLLAMA_BASE_URL, LLM_MODEL


client = OpenAI(
    base_url=f"{OLLAMA_BASE_URL}/v1",
    api_key="ollama"
)


def rewrite_query(question: str) -> str:

    prompt = f"""
    You are a query rewriting assistant for an
    enterprise knowledge retrieval system.

    Rewrite the user's question to improve document retrieval.

    Rules:
    1. Preserve the original meaning and intent.
    2. Use clear, specific search terminology.
    3. Do not answer the question.
    4. Do not introduce assumptions or new facts.
    5. Return only the rewritten question.

    Original question:
    {question}

    Rewritten question:
    """

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    rewritten_query = response.choices[0].message.content

    if not rewritten_query or not rewritten_query.strip():
        return question

    return rewritten_query.strip()


if __name__ == "__main__":

    question = "Can I WFH three days and what security rules apply?"

    rewritten = rewrite_query(question)

    print("Original query:", question)
    print("\nRewritten query:", rewritten)
