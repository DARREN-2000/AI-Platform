"""Judge-vs-human calibration: does the LLM judge agree with human labels?

An uncalibrated judge is just a vibe. These metrics quantify agreement between
judge scores and human gold labels, which is exactly the "calibration against
human labels" + "false positives" rigor the eval loop needs:

  * agreement                - exact-match rate
  * cohens_kappa             - chance-corrected agreement (categorical)
  * weighted_kappa           - ordinal agreement (linear/quadratic) for 1..5
  * pearson / spearman       - linear / rank correlation
  * mean_absolute_error      - average score gap
  * confusion_at_threshold   - TP/FP/TN/FN + false-positive / false-negative
                               rates at a pass threshold

All stdlib, deterministic, offline.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Sequence


def _check_pair(a: Sequence[float], b: Sequence[float]) -> None:
    if len(a) != len(b):
        raise ValueError("score sequences must have the same length")


def agreement(a: Sequence[float], b: Sequence[float]) -> float:
    """Exact-match rate after rounding to the nearest integer label."""
    _check_pair(a, b)
    if not a:
        return 0.0
    return sum(1 for x, y in zip(a, b) if round(x) == round(y)) / len(a)


def _confusion_counts(a: Sequence[int], b: Sequence[int]):
    cats = sorted(set(a) | set(b))
    idx = {c: i for i, c in enumerate(cats)}
    k = len(cats)
    matrix = [[0] * k for _ in range(k)]
    for x, y in zip(a, b):
        matrix[idx[x]][idx[y]] += 1
    return cats, matrix


def cohens_kappa(a: Sequence[float], b: Sequence[float]) -> float:
    """Unweighted Cohen's kappa on integer-rounded labels."""
    _check_pair(a, b)
    if not a:
        return 0.0
    ai = [round(x) for x in a]
    bi = [round(y) for y in b]
    cats, matrix = _confusion_counts(ai, bi)
    k = len(cats)
    n = len(ai)
    po = sum(matrix[i][i] for i in range(k)) / n
    row = [sum(matrix[i]) for i in range(k)]
    col = [sum(matrix[i][j] for i in range(k)) for j in range(k)]
    pe = sum((row[i] / n) * (col[i] / n) for i in range(k))
    if pe >= 1.0:
        return 1.0 if po >= 1.0 else 0.0
    return (po - pe) / (1.0 - pe)


def weighted_kappa(
    a: Sequence[float], b: Sequence[float], weights: str = "quadratic"
) -> float:
    """Weighted kappa for ordinal labels (``quadratic`` or ``linear``)."""
    _check_pair(a, b)
    if not a:
        return 0.0
    ai = [round(x) for x in a]
    bi = [round(y) for y in b]
    cats, matrix = _confusion_counts(ai, bi)
    k = len(cats)
    n = len(ai)
    if k == 1:
        return 1.0
    row = [sum(matrix[i]) for i in range(k)]
    col = [sum(matrix[i][j] for i in range(k)) for j in range(k)]
    expected = [[row[i] * col[j] / n for j in range(k)] for i in range(k)]

    def w(i: int, j: int) -> float:
        if weights == "linear":
            return abs(i - j) / (k - 1)
        return ((i - j) ** 2) / ((k - 1) ** 2)

    num = sum(w(i, j) * matrix[i][j] for i in range(k) for j in range(k))
    den = sum(w(i, j) * expected[i][j] for i in range(k) for j in range(k))
    if den == 0:
        return 1.0
    return 1.0 - num / den


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    _check_pair(x, y)
    n = len(x)
    if n == 0:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


def _ranks(values: Sequence[float]) -> List[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for m in range(i, j + 1):
            ranks[order[m]] = avg_rank
        i = j + 1
    return ranks


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    _check_pair(x, y)
    if not x:
        return 0.0
    return pearson(_ranks(x), _ranks(y))


def mean_absolute_error(x: Sequence[float], y: Sequence[float]) -> float:
    _check_pair(x, y)
    if not x:
        return 0.0
    return sum(abs(a - b) for a, b in zip(x, y)) / len(x)


def confusion_at_threshold(
    judge: Sequence[float], human: Sequence[float], threshold: float
) -> Dict[str, float]:
    """Treat score >= threshold as a 'pass'. Human labels are ground truth.

    Reports false-positive rate (judge passes what humans fail) and
    false-negative rate (judge fails what humans pass) - the asymmetric errors
    that matter when an eval gates shipping.
    """
    _check_pair(judge, human)
    tp = fp = tn = fn = 0
    for j, h in zip(judge, human):
        jp = j >= threshold
        hp = h >= threshold
        if jp and hp:
            tp += 1
        elif jp and not hp:
            fp += 1
        elif (not jp) and hp:
            fn += 1
        else:
            tn += 1
    total = tp + fp + tn + fn
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "false_positive_rate": fp / (fp + tn) if (fp + tn) else 0.0,
        "false_negative_rate": fn / (fn + tp) if (fn + tp) else 0.0,
        "precision": tp / (tp + fp) if (tp + fp) else 0.0,
        "recall": tp / (tp + fn) if (tp + fn) else 0.0,
        "accuracy": (tp + tn) / total if total else 0.0,
    }


@dataclass(frozen=True)
class CalibrationReport:
    n: int
    agreement: float
    cohen_kappa: float
    quadratic_weighted_kappa: float
    pearson: float
    spearman: float
    mae: float

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "agreement": round(self.agreement, 4),
            "cohen_kappa": round(self.cohen_kappa, 4),
            "quadratic_weighted_kappa": round(self.quadratic_weighted_kappa, 4),
            "pearson": round(self.pearson, 4),
            "spearman": round(self.spearman, 4),
            "mae": round(self.mae, 4),
        }


def calibrate(
    judge_scores: Sequence[float], human_scores: Sequence[float]
) -> CalibrationReport:
    """Full calibration report comparing judge scores to human gold labels."""
    _check_pair(judge_scores, human_scores)
    n = len(judge_scores)
    return CalibrationReport(
        n=n,
        agreement=agreement(judge_scores, human_scores),
        cohen_kappa=cohens_kappa(judge_scores, human_scores),
        quadratic_weighted_kappa=weighted_kappa(judge_scores, human_scores, "quadratic"),
        pearson=pearson(judge_scores, human_scores),
        spearman=spearman(judge_scores, human_scores),
        mae=mean_absolute_error(judge_scores, human_scores),
    )
