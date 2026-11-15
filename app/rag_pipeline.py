
from app.multi_query_retrieval import multi_query_retrieve
from app.generation import generate_answer


def ask_question(question: str):

    # Step 1: Retrieve documents using multi-query retrieval
    results = multi_query_retrieve(
        question=question,
        candidate_count=10,
        top_k=3,
        score_threshold=-5
    )

    if not results:
        return {
            "answer": "I couldn't find relevant information.",
            "sources": []
        }

    # Step 2: Extract document text
    documents = [
        result["document"] for result in results
    ]

    # Step 3: Build context for the LLM
    context = "\n\n".join(documents)

    # Step 4: Generate a grounded answer
    answer = generate_answer(question, context)

    # Step 5: Extract unique source filenames
    sources = list(dict.fromkeys(
        result["metadata"]["source"]
        for result in results
    ))

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    question = "How can employees securely work from home?"

    response = ask_question(question)

    print("\nAnswer:", response["answer"])
    print("Sources:", response["sources"])
