import pytest

from app.evaluation import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    mean_reciprocal_rank,
)


def test_precision_at_k():
    retrieved = ["leave.txt", "expense.txt", "benefits.txt"]
    relevant = {"leave.txt", "benefits.txt"}

    assert precision_at_k(retrieved, relevant, 3) == pytest.approx(2 / 3)


def test_recall_at_k():
    retrieved = ["leave.txt", "expense.txt", "benefits.txt"]
    relevant = {"leave.txt", "benefits.txt"}

    assert recall_at_k(retrieved, relevant, 3) == 1.0


def test_reciprocal_rank():
    retrieved = ["expense.txt", "leave.txt", "benefits.txt"]
    relevant = {"leave.txt"}

    assert reciprocal_rank(retrieved, relevant) == 0.5


def test_mean_reciprocal_rank():
    results = [
        ["expense.txt", "leave.txt"],
        ["benefits.txt", "security.txt"],
    ]
    relevant = [
        {"leave.txt"},
        {"benefits.txt"},
    ]

    assert mean_reciprocal_rank(results, relevant) == 0.75


def test_invalid_k():
    with pytest.raises(ValueError):
        precision_at_k(["leave.txt"], {"leave.txt"}, 0)

    with pytest.raises(ValueError):
        recall_at_k(["leave.txt"], {"leave.txt"}, 0)