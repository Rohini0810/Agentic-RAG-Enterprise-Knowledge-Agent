from app.retrieval import retrieve_documents
from app.generation import generate_answer


def ask_question(question: str):

    # Step 1: Retrieve relevant document chunks
    results = retrieve_documents(question, top_k=3)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        return "I couldn't find relevant information."

    # Step 2: Combine retrieved chunks into context
    context = "\n\n".join(documents)

    # Step 3: Generate an answer using the retrieved context
    answer = generate_answer(question, context)

    # Step 4: Return answer and source information
    sources = list(set(metadata["source"] for metadata in metadatas))

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    question = "How many annual leave days do employees receive?"

    response = ask_question(question)

    print("\nAnswer:", response["answer"])
    print("Sources:", response["sources"])