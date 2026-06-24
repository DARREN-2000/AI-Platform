from llm_eval.dataset import EvalCase
from llm_eval.judge import LLMJudge
from llm_eval.providers import MockProvider
from llm_eval.runner import EvalRunner, check_regression


def _runner():
    return EvalRunner(judge=LLMJudge(provider=MockProvider(), samples=1))


def test_run_produces_summary():
    cases = [
        EvalCase("a", "Q", "Paris", "", ("paris",)),
        EvalCase("b", "Q", "nope", "", ("duplicate",)),
    ]
    summary = _runner().run(cases)
    assert summary.stats.n == 2
    by_id = {r.case_id: r for r in summary.results}
    assert by_id["a"].score == 5
    assert by_id["b"].score == 1


def test_regression_no_baseline(tmp_path):
    summary = _runner().run([EvalCase("a", "Q", "Paris", "", ("paris",))])
    ok, _ = check_regression(summary, tmp_path / "missing.json")
    assert ok


def test_regression_detects_drop(tmp_path):
    baseline = tmp_path / "baseline.json"
    baseline.write_text('{"mean": 0.9}', encoding="utf-8")
    summary = _runner().run([EvalCase("a", "Q", "nope", "", ("duplicate",))])
    ok, _ = check_regression(summary, baseline)
    assert not ok
