
from time import perf_counter

from app.retrieval_router import decide_retrieval_strategy
from app.advanced_retrieval import advanced_retrieve
from app.multi_query_retrieval import multi_query_retrieve
from app.generation import generate_answer
from app.intent_router import classify_intent
from app.scope_guard import is_in_scope

from app.observability import (
    generate_request_id,
    log_event,
    track_duration
)


def ask_question(question: str):

    request_id = generate_request_id()
    request_start = perf_counter()

    log_event(
        event="request_started",
        request_id=request_id,
        question_length=len(question) if question else 0
    )

    try:
        response = process_question(question, request_id)

        log_event(
            event="request_completed",
            request_id=request_id,
            status="success",
            total_duration_ms=round(
                (perf_counter() - request_start) * 1000, 2
            ),
            source_count=len(response["sources"])
        )

        return response

    except Exception:
        log_event(
            event="request_failed",
            request_id=request_id,
            level="exception",
            total_duration_ms=round(
                (perf_counter() - request_start) * 1000, 2
            ),
            status="failed"
        )
        raise


def process_question(question: str, request_id: str):

    # Step 1: Classify user intent
    with track_duration("intent_classification", request_id):
        intent = classify_intent(question)

    log_event(
        event="intent_classified",
        request_id=request_id,
        intent=intent
    )

    # Step 2: Handle invalid input
    if intent == "invalid":
        return {
            "answer": "Please enter a valid question.",
            "sources": []
        }

    # Step 3: Handle greetings
    if intent == "greeting":
        return {
            "answer": (
                "Hello! I'm your Enterprise Knowledge Assistant. "
                "How can I help you with company policies and information?"
            ),
            "sources": []
        }

    # Step 4: Validate enterprise scope
    with track_duration("scope_validation", request_id):
        in_scope = is_in_scope(question)

    if not in_scope:
        log_event(
            event="question_rejected",
            request_id=request_id,
            reason="out_of_scope"
        )

        return {
            "answer": (
                "I'm your Enterprise Knowledge Assistant. "
                "I can help with company policies, leave, remote work, "
                "expenses, benefits and security."
            ),
            "sources": []
        }

    # Step 5: Select retrieval strategy
    with track_duration("retrieval_routing", request_id):
        decision = decide_retrieval_strategy(question)

    strategy = decision["strategy"]

    log_event(
        event="retrieval_strategy_selected",
        request_id=request_id,
        strategy=strategy,
        reason=decision["reason"]
    )

    # Step 6: Retrieve documents
    with track_duration(
        "retrieval",
        request_id,
        strategy=strategy
    ):
        if strategy == "single_query":
            results = advanced_retrieve(
                query=question,
                candidate_count=10,
                top_k=3,
                score_threshold=-5
            )
        else:
            results = multi_query_retrieve(
                question=question,
                candidate_count=10,
                top_k=3,
                score_threshold=-5
            )

    log_event(
        event="retrieval_results",
        request_id=request_id,
        document_count=len(results)
    )

    # Step 7: Handle empty retrieval
    if not results:
        return {
            "answer": "I couldn't find relevant information.",
            "sources": []
        }

    # Step 8: Prepare context
    documents = [
        result["document"] for result in results
    ]
    context = "\n\n".join(documents)

    # Step 9: Generate grounded answer
    with track_duration("generation", request_id):
        answer = generate_answer(
            question=question,
            context=context
        )

    # Step 10: Extract unique sources
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
        "Can I work remotely and what security rules apply?",
        "Hi",
        "What's the weather in Bengaluru?"
    ]

    for question in questions:

        print("\n" + "=" * 60)
        print("Question:", question)

        response = ask_question(question)

        print("\nAnswer:", response["answer"])
        print("Sources:", response["sources"])
