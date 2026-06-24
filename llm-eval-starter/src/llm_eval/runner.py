"""Eval orchestration + the CI regression gate.

``check_regression`` is the piece that turns evals from a notebook curiosity
into a quality gate: a prompt/model change that drops the mean fails the build.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .dataset import EvalCase
from .judge import LLMJudge
from .metrics import ScoreStats, aggregate_scores


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    score: int
    normalized: float
    reasoning: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class RunSummary:
    results: list[CaseResult]
    stats: ScoreStats

    def as_dict(self) -> dict:
        return {"stats": self.stats.as_dict(), "results": [r.__dict__ for r in self.results]}


@dataclass
class EvalRunner:
    judge: LLMJudge
    pass_threshold: float = 0.6

    def run(self, cases: Sequence[EvalCase]) -> RunSummary:
        results: list[CaseResult] = []
        for case in cases:
            jr = self.judge.score_robust(
                case.question, case.answer, case.rubric, list(case.expected_keywords)
            )
            results.append(
                CaseResult(
                    case_id=case.id,
                    score=jr.score,
                    normalized=jr.normalized,
                    reasoning=jr.reasoning,
                    tags=case.tags,
                )
            )
        stats = aggregate_scores(
            [r.normalized for r in results], pass_threshold=self.pass_threshold
        )
        return RunSummary(results=results, stats=stats)


def check_regression(
    summary: RunSummary, baseline_path: str | Path, *, tolerance: float = 0.02
) -> tuple[bool, str]:
    """Compare current mean against a stored baseline. Returns (ok, message)."""
    path = Path(baseline_path)
    if not path.exists():
        return True, f"No baseline at {path}; treating current run as the new baseline."
    baseline = json.loads(path.read_text(encoding="utf-8"))
    base_mean = float(baseline.get("mean", 0.0))
    cur_mean = summary.stats.mean
    if cur_mean + tolerance < base_mean:
        return False, (
            f"REGRESSION: mean {cur_mean:.3f} < baseline {base_mean:.3f} (tol {tolerance})."
        )
    return True, f"OK: mean {cur_mean:.3f} >= baseline {base_mean:.3f} - {tolerance}."
