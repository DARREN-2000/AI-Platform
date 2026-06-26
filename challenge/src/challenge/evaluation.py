"""Evaluation composition for the challenge.

Wires the llm-eval-starter pieces: golden dataset -> LLM-as-judge -> stats with
bootstrap CIs -> regression gate, plus judge calibration against human labels.
Defaults to the offline MockProvider judge so it runs with no keys.
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence

from llm_eval import (
    EvalRunner,
    LLMJudge,
    MockProvider,
    RunSummary,
    check_regression,
    load_jsonl,
)
from llm_eval.calibration import CalibrationReport, calibrate, confusion_at_threshold

from .config import Settings


def get_settings(settings: Optional[Settings] = None) -> Settings:
    return settings or Settings.from_env()


def build_judge(settings: Optional[Settings] = None, samples: int = 1) -> LLMJudge:
    settings = get_settings(settings)
    name = settings.eval_provider.lower()
    if name in ("mock", "rules", "offline"):
        return LLMJudge(provider=MockProvider(), samples=samples)
    # Real providers: llm_eval ships an OpenAIProvider (OpenAI/OpenRouter).
    from llm_eval.providers import OpenAIProvider  # lazy import

    return LLMJudge(provider=OpenAIProvider(model=settings.model or "gpt-4o-mini"), samples=samples)


def run_eval(
    dataset_path: Optional[str] = None,
    *,
    baseline_path: Optional[str] = None,
    settings: Optional[Settings] = None,
) -> RunSummary:
    settings = get_settings(settings)
    cases = load_jsonl(dataset_path or settings.dataset_path)
    summary = EvalRunner(judge=build_judge(settings)).run(cases)
    if baseline_path:
        ok, msg = check_regression(summary, baseline_path)
        summary.stats.as_dict()  # noqa: ensure stats computed
        print(f"[regression] ok={ok}: {msg}")
    return summary


def calibrate_judge(
    dataset_path: Optional[str] = None,
    *,
    human_labels: Dict[str, float],
    settings: Optional[Settings] = None,
) -> CalibrationReport:
    """Run the judge over the dataset and compare to human labels by case id."""
    settings = get_settings(settings)
    cases = load_jsonl(dataset_path or settings.dataset_path)
    summary = EvalRunner(judge=build_judge(settings)).run(cases)
    judge_scores: list = []
    human_scores: list = []
    for r in summary.results:
        if r.case_id in human_labels:
            judge_scores.append(r.score)
            human_scores.append(human_labels[r.case_id])
    return calibrate(judge_scores, human_scores)


def false_positive_report(
    judge_scores: Sequence[float], human_scores: Sequence[float], threshold: float = 3.0
) -> dict:
    return confusion_at_threshold(judge_scores, human_scores, threshold)
