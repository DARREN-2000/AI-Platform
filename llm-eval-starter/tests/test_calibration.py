import pytest

from llm_eval.calibration import (
    calibrate,
    cohens_kappa,
    confusion_at_threshold,
    mean_absolute_error,
    pearson,
    spearman,
    weighted_kappa,
)


def test_perfect_agreement():
    j = [1, 2, 3, 4, 5]
    rep = calibrate(j, j)
    assert rep.n == 5
    assert rep.agreement == 1.0
    assert rep.cohen_kappa == 1.0
    assert rep.quadratic_weighted_kappa == 1.0
    assert abs(rep.pearson - 1.0) < 1e-9
    assert rep.mae == 0.0


def test_partial_agreement_metrics_in_range():
    judge = [5, 4, 3, 2, 1]
    human = [5, 5, 3, 1, 1]
    rep = calibrate(judge, human)
    assert 0.0 < rep.agreement < 1.0
    assert -1.0 <= rep.cohen_kappa <= 1.0
    assert rep.pearson > 0.5  # strongly correlated but not perfect
    assert rep.mae > 0.0


def test_weighted_kappa_penalizes_far_misses_less_than_unweighted():
    # judge is off by one everywhere: ordinal kappa should stay high
    judge = [1, 2, 3, 4, 5]
    human = [2, 3, 4, 5, 5]
    qwk = weighted_kappa(judge, human, "quadratic")
    ck = cohens_kappa(judge, human)
    assert qwk > ck


def test_confusion_at_threshold_false_positives():
    # judge passes (>=0.6) case the human fails -> one false positive
    judge = [0.9, 0.8, 0.7, 0.2]
    human = [1.0, 1.0, 0.0, 0.0]
    cm = confusion_at_threshold(judge, human, threshold=0.6)
    assert cm["tp"] == 2 and cm["fp"] == 1 and cm["tn"] == 1 and cm["fn"] == 0
    assert cm["false_positive_rate"] == 0.5
    assert cm["false_negative_rate"] == 0.0


def test_length_mismatch_raises():
    with pytest.raises(ValueError):
        calibrate([1, 2], [1])


def test_correlation_edge_cases():
    assert pearson([1, 1, 1], [1, 2, 3]) == 0.0  # zero variance -> 0
    assert spearman([], []) == 0.0
    assert mean_absolute_error([], []) == 0.0
