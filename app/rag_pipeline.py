
from app.retrieval_router import decide_retrieval_strategy
from app.advanced_retrieval import advanced_retrieve
from app.multi_query_retrieval import multi_query_retrieve
from app.generation import generate_answer
from app.intent_router import classify_intent
from app.scope_guard import is_in_scope

def ask_question(question: str):

    # Step 1: Classify user intent
    intent = classify_intent(question)

    # Step 2: Handle invalid input
    if intent == "invalid":
        return {
            "answer": "Please enter a valid question.",
            "sources": []
        }

    # Step 3: Handle greetings without retrieval
    if intent == "greeting":
        return {
            "answer": "Hello! I'm your Enterprise Knowledge Assistant. How can I help you with company policies and information?",
            "sources": []
        }

    # Step 4: Continue with your existing Agentic RAG logic
    decision = decide_retrieval_strategy(question)
    strategy = decision["strategy"]

    print(f"Selected strategy: {strategy}")
    print(f"Reason: {decision['reason']}")

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

    if not results:
        return {
            "answer": "I couldn't find relevant information.",
            "sources": []
        }
    if not is_in_scope(question):
        return {
        "answer": (
            "I'm your Enterprise Knowledge Assistant. "
            "I can help with company policies, leave, "
            "remote work, expenses, benefits and security."
        ),
        "sources": []
    }

    documents = [result["document"] for result in results]
    context = "\n\n".join(documents)

    answer = generate_answer(question, context)

    sources = list(dict.fromkeys(
        result["metadata"]["source"] for result in results
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
