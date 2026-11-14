
from app.advanced_retrieval import advanced_retrieve
from app.generation import generate_answer


def ask_question(question: str):

    # Step 1: Retrieve and rerank relevant chunks
    results = advanced_retrieve(
        query=question,
        candidate_count=10,
        top_k=3
    )

    if not results:
        return {
            "answer": "I couldn't find relevant information.",
            "sources": []
        }

    # Step 2: Extract document text from retrieved results
    documents = [
        result["document"] for result in results
    ]

    # Step 3: Combine documents into LLM context
    context = "\n\n".join(documents)

    # Step 4: Generate an answer
    answer = generate_answer(question, context)

    # Step 5: Extract unique source filenames
    sources = list(set(
        result["metadata"]["source"]
        for result in results
    ))

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    #question = "How many annual leave days do employees receive?"
    question = "How can employees securely work from home?"
    
    response = ask_question(question)

    print("\nAnswer:", response["answer"])
    print("Sources:", response["sources"])
