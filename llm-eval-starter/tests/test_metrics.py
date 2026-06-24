from llm_eval.metrics import aggregate_scores


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
