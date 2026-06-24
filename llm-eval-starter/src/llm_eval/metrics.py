"""Aggregation metrics.

Reporting stdev AND a bootstrap confidence interval alongside the mean matters:
a single mean hides how much it would move on a different sample. ``pass_rate``
is the headline number CI gates on.
"""
from __future__ import annotations

import random
import statistics
from dataclasses import dataclass
from typing import Sequence, Tuple


@dataclass(frozen=True)
class ScoreStats:
    n: int
    mean: float
    stdev: float
    pass_rate: float  # fraction at or above the pass threshold
    ci_low: float = 0.0
    ci_high: float = 0.0

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "mean": round(self.mean, 4),
            "stdev": round(self.stdev, 4),
            "pass_rate": round(self.pass_rate, 4),
            "ci_low": round(self.ci_low, 4),
            "ci_high": round(self.ci_high, 4),
        }


def bootstrap_ci(
    scores: Sequence[float],
    *,
    confidence: float = 0.95,
    n_resamples: int = 1000,
    seed: int = 0,
) -> Tuple[float, float]:
    """Percentile bootstrap CI for the mean. Deterministic given ``seed``.

    Resamples the scores with replacement ``n_resamples`` times and returns the
    (alpha/2, 1-alpha/2) percentiles of the resample means. A small dataset
    yields a wide interval - which is exactly the signal you want to report.
    """
    values = list(scores)
    if not values:
        return (0.0, 0.0)
    if len(values) == 1:
        return (float(values[0]), float(values[0]))
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(n_resamples):
        total = 0.0
        for _ in range(n):
            total += values[rng.randrange(n)]
        means.append(total / n)
    means.sort()
    alpha = (1.0 - confidence) / 2.0
    lo_idx = int(alpha * n_resamples)
    hi_idx = min(n_resamples - 1, int((1.0 - alpha) * n_resamples))
    return (means[lo_idx], means[hi_idx])


def aggregate_scores(
    scores: Sequence[float],
    *,
    pass_threshold: float = 0.6,
    n_resamples: int = 1000,
    ci_seed: int = 0,
) -> ScoreStats:
    if not scores:
        return ScoreStats(0, 0.0, 0.0, 0.0, 0.0, 0.0)
    mean = statistics.fmean(scores)
    stdev = statistics.pstdev(scores) if len(scores) > 1 else 0.0
    pass_rate = sum(1 for s in scores if s >= pass_threshold) / len(scores)
    ci_low, ci_high = bootstrap_ci(scores, n_resamples=n_resamples, seed=ci_seed)
    return ScoreStats(len(scores), mean, stdev, pass_rate, ci_low, ci_high)
