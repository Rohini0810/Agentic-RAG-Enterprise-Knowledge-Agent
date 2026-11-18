
import pytest

from app.intent_router import classify_intent


@pytest.mark.parametrize(
    "question",
    [
        "Hi",
        "hello",
        "Hey!",
        "Good morning",
        "Good afternoon."
    ]
)
def test_greeting_detection(question):
    assert classify_intent(question) == "greeting"


@pytest.mark.parametrize(
    "question",
    [
        "How many annual leave days do employees receive?",
        "What is the remote work policy?",
        "Explain the expense approval process."
    ]
)
def test_knowledge_query_detection(question):
    assert classify_intent(question) == "knowledge_query"


@pytest.mark.parametrize("question", ["", "   "])
def test_empty_question_detection(question):
    assert classify_intent(question) == "invalid"
