from llm_eval.judge import LLMJudge
from llm_eval.providers import MockProvider


def test_judge_high_score_on_keyword_match():
    judge = LLMJudge(provider=MockProvider(), samples=1)
    r = judge.score("Q", "The capital is Paris.", "Names Paris", ["paris"])
    assert r.score == 5
    assert r.normalized == 1.0


def test_judge_low_score_no_match():
    judge = LLMJudge(provider=MockProvider(), samples=1)
    r = judge.score("Q", "It is fast.", "Explains duplicates", ["duplicate", "repeat"])
    assert r.score == 1


def test_judge_handles_garbage_output():
    judge = LLMJudge(provider=MockProvider(scripted={"<eval-input>": "not json at all"}), samples=1)
    r = judge.score("Q", "x", "", [])
    assert r.score == 1
    assert "Unparseable" in r.reasoning


def test_pairwise_prefers_better_answer():
    judge = LLMJudge(provider=MockProvider(), samples=1)
    winner = judge.pairwise("Q", "Paris is the capital.", "I do not know.", "Names Paris", ["paris"])
    assert winner == "A"
