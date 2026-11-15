
from app.retrieval_router import decide_retrieval_strategy
from app.advanced_retrieval import advanced_retrieve
from app.multi_query_retrieval import multi_query_retrieve
from app.generation import generate_answer


def ask_question(question: str):

    # Step 1: Decide which retrieval strategy to use
    decision = decide_retrieval_strategy(question)

    strategy = decision["strategy"]

    print("\nRetrieval strategy:", strategy)
    print("Reason:", decision["reason"])

    # Step 2: Execute the selected retrieval strategy
    if strategy == "single_query":

        results = advanced_retrieve(
            query=question,
            candidate_count=10,
            top_k=3
        )

    else:

        results = multi_query_retrieve(
            question=question,
            candidate_count=10,
            top_k=3,
            score_threshold=-5
        )

    # Step 3: Handle empty retrieval results
    if not results:
        return {
            "answer": "I couldn't find relevant information.",
            "sources": []
        }

    # Step 4: Extract document text
    documents = [
        result["document"] for result in results
    ]

    # Step 5: Build context for the LLM
    context = "\n\n".join(documents)

    # Step 6: Generate a grounded answer
    answer = generate_answer(question, context)

    # Step 7: Extract unique source filenames
    sources = list(dict.fromkeys(
        result["metadata"]["source"]
        for result in results
    ))

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    questions = [
        "How many annual leave days do employees receive?",
        "Can I work remotely and what security rules apply?"
    ]

    for question in questions:

        print("\n" + "=" * 60)
        print("Question:", question)

        response = ask_question(question)

        print("\nAnswer:", response["answer"])
        print("Sources:", response["sources"])
