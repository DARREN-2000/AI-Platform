"""Aggregation metrics.

Reporting stdev alongside the mean matters: an eval score without variance is
half a result. pass_rate is the headline number CI gates on.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ScoreStats:
    n: int
    mean: float
    stdev: float
    pass_rate: float  # fraction at or above the pass threshold

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "mean": round(self.mean, 4),
            "stdev": round(self.stdev, 4),
            "pass_rate": round(self.pass_rate, 4),
        }


def aggregate_scores(scores: Sequence[float], *, pass_threshold: float = 0.6) -> ScoreStats:
    if not scores:
        return ScoreStats(0, 0.0, 0.0, 0.0)
    mean = statistics.fmean(scores)
    stdev = statistics.pstdev(scores) if len(scores) > 1 else 0.0
    pass_rate = sum(1 for s in scores if s >= pass_threshold) / len(scores)
    return ScoreStats(len(scores), mean, stdev, pass_rate)
