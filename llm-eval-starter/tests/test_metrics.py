from llm_eval.metrics import aggregate_scores, bootstrap_ci


def test_aggregate_empty():
    s = aggregate_scores([])
    assert s.n == 0
    assert s.mean == 0.0
    assert s.pass_rate == 0.0


def test_aggregate_basic():
    s = aggregate_scores([1.0, 1.0, 1.0, 0.0], pass_threshold=0.6)
    assert s.n == 4
    assert abs(s.mean - 0.75) < 1e-9
    assert abs(s.pass_rate - 0.75) < 1e-9
    assert s.stdev > 0


def test_aggregate_includes_ci():
    s = aggregate_scores([1.0, 1.0, 1.0, 0.0])
    assert s.ci_low <= s.mean <= s.ci_high
    d = s.as_dict()
    assert "ci_low" in d and "ci_high" in d


def test_bootstrap_ci_deterministic_and_brackets_mean():
    scores = [1.0, 1.0, 1.0, 0.0]
    lo, hi = bootstrap_ci(scores, seed=0)
    lo2, hi2 = bootstrap_ci(scores, seed=0)
    assert (lo, hi) == (lo2, hi2)  # deterministic given the seed
    assert lo <= sum(scores) / len(scores) <= hi


def test_bootstrap_ci_single_value():
    assert bootstrap_ci([0.7]) == (0.7, 0.7)


def test_bootstrap_ci_empty():
    assert bootstrap_ci([]) == (0.0, 0.0)
