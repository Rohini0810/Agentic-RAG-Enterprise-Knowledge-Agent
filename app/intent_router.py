
import re

GREETINGS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "howdy"
}


def classify_intent(question: str) -> str:
    """
    Classify a user message into a supported intent.
    """

    if not question or not question.strip():
        return "invalid"

    normalized_question = question.lower().strip()

    # Remove common punctuation
    normalized_question = re.sub(
        r"[.!?,]+$",
        "",
        normalized_question
    )

    if normalized_question in GREETINGS:
        return "greeting"

    return "knowledge_query"
