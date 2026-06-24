"""llm_eval: a lean, adaptable LLM-as-judge evaluation harness.

Designed to be read in ~10 minutes and adapted inside a take-home window.
Provider-agnostic, runs offline with a deterministic MockProvider, reports
bootstrap confidence intervals, and ships a CI regression gate so quality drops
fail the build instead of shipping.
"""
from .cache import CachingProvider, MeteredProvider, UsageMeter, UsageRecord
from .dataset import EvalCase, load_jsonl
from .judge import JUDGE_SYSTEM, JudgeResult, LLMJudge
from .metrics import ScoreStats, aggregate_scores, bootstrap_ci
from .providers import Message, MockProvider, Provider, with_retries
from .runner import CaseResult, EvalRunner, RunSummary, check_regression

__all__ = [
    "CachingProvider",
    "MeteredProvider",
    "UsageMeter",
    "UsageRecord",
    "EvalCase",
    "load_jsonl",
    "JUDGE_SYSTEM",
    "JudgeResult",
    "LLMJudge",
    "ScoreStats",
    "aggregate_scores",
    "bootstrap_ci",
    "Message",
    "MockProvider",
    "Provider",
    "with_retries",
    "CaseResult",
    "EvalRunner",
    "RunSummary",
    "check_regression",
]
__version__ = "0.1.0"
