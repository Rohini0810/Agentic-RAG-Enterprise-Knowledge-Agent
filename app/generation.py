#We'll connect Qwen 2.5 3B through Ollama's OpenAI-compatible API.
from openai import OpenAI

from app.config import OLLAMA_BASE_URL, LLM_MODEL

client = OpenAI(
    base_url=f"{OLLAMA_BASE_URL}/v1",
    api_key="ollama"
)


def generate_answer(question: str, context: str):

    prompt = f"""
    You are an enterprise knowledge assistant.

    Answer the question using ONLY the provided context.
    If the answer is not present in the context, say you don't know.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    question = "How many annual leave days do employees receive?"

    context = """
    Employees receive 20 days of annual paid leave.
    """

    answer = generate_answer(question, context)

    print("\nAnswer:", answer)