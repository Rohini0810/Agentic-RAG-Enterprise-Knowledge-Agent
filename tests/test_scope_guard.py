
import pytest

from app.scope_guard import is_in_scope


@pytest.mark.parametrize(
    "question",
    [
        "How many annual leave days do I get?",
        "What is the remote work policy?",
        "How do I submit an expense claim?",
        "What employee benefits are available?",
        "What are the security requirements?"
    ]
)
def test_enterprise_questions_are_in_scope(question):
    assert is_in_scope(question)


@pytest.mark.parametrize(
    "question",
    [
        "What's the weather in Bengaluru?",
        "Who won the World Cup?",
        "Tell me a joke",
        "What is the capital of France?"
    ]
)
def test_unrelated_questions_are_out_of_scope(question):
    assert not is_in_scope(question)


def test_empty_question_is_out_of_scope():
    assert not is_in_scope("")


def test_whitespace_question_is_out_of_scope():
    assert not is_in_scope("   ")
