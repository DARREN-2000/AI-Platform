from llm_eval.similarity import (
    cosine_similarity,
    exact_match,
    keyword_recall,
    normalize,
    token_f1,
)


def test_normalize_and_exact_match():
    assert normalize("The  CAT, sat!") == "the cat sat"
    assert exact_match("the cat", "The CAT!") == 1.0
    assert exact_match("dog", "cat") == 0.0


def test_token_f1():
    assert token_f1("a b c", "a b c") == 1.0
    assert abs(token_f1("a b", "a b c d") - 2 / 3) < 1e-9
    assert token_f1("x", "y") == 0.0


def test_cosine_similarity():
    assert abs(cosine_similarity("hello world", "hello world") - 1.0) < 1e-9
    assert 0.0 <= cosine_similarity("alpha beta", "gamma delta") < 1.0
    assert cosine_similarity("", "x") == 0.0


def test_keyword_recall():
    assert keyword_recall("paris is the capital", ["paris", "capital"]) == 1.0
    assert keyword_recall("paris", ["paris", "berlin"]) == 0.5
    assert keyword_recall("anything", []) == 1.0
