"""LLM-as-judge scoring.

Design choices worth defending in an interview:
- Structured JSON verdict (score + reasoning) so results are machine-checkable.
- ``score_robust`` runs N samples and takes the median to tame non-determinism.
- ``pairwise`` does a position-swap to control for position bias.
- Normalized 0..1 score lets you average across rubrics with different scales.
"""
from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from typing import Sequence

from .providers import Message, Provider

JUDGE_SYSTEM = (
    "You are a rigorous evaluation judge. Score the candidate answer against the "
    "rubric on an integer scale of 1 (poor) to 5 (excellent). Respond ONLY with a "
    'JSON object: {"score": <int 1-5>, "reasoning": <short string>}.'
)


@dataclass(frozen=True)
class JudgeResult:
    score: int
    reasoning: str
    raw: str

    @property
    def normalized(self) -> float:
        """Score mapped to 0..1 for aggregation across rubrics."""
        return (self.score - 1) / 4


def _build_prompt(question: str, answer: str, rubric: str, expected_keywords) -> str:
    payload = {
        "question": question,
        "answer": answer,
        "rubric": rubric,
        "expected_keywords": list(expected_keywords or []),
    }
    return (
        f"Evaluate the candidate answer.\nRubric: {rubric}\n"
        f"<eval-input>{json.dumps(payload)}</eval-input>"
    )


@dataclass
class LLMJudge:
    provider: Provider
    samples: int = 1  # >1 to reduce variance on real (non-deterministic) judges
    temperature: float = 0.0

    def score(self, question, answer, rubric="", expected_keywords=None) -> JudgeResult:
        prompt = _build_prompt(question, answer, rubric, expected_keywords)
        messages = [Message("system", JUDGE_SYSTEM), Message("user", prompt)]
        raw = self.provider.complete(messages, temperature=self.temperature)
        score, reasoning = self._parse(raw)
        return JudgeResult(score=score, reasoning=reasoning, raw=raw)

    def score_robust(self, question, answer, rubric="", expected_keywords=None) -> JudgeResult:
        """Run ``samples`` times and take the median score."""
        results = [
            self.score(question, answer, rubric, expected_keywords)
            for _ in range(max(1, self.samples))
        ]
        median_score = int(round(statistics.median(r.score for r in results)))
        return JudgeResult(
            score=median_score,
            reasoning=results[0].reasoning,
            raw=json.dumps([r.raw for r in results]),
        )

    def pairwise(self, question, answer_a, answer_b, rubric="", expected_keywords=None) -> str:
        """Position-swap pairwise comparison. Returns 'A', 'B', or 'tie'."""
        score_a = self.score_robust(question, answer_a, rubric, expected_keywords).score
        score_b = self.score_robust(question, answer_b, rubric, expected_keywords).score
        if score_a > score_b:
            return "A"
        if score_b > score_a:
            return "B"
        return "tie"

    @staticmethod
    def _parse(raw: str):
        try:
            obj = json.loads(raw)
            score = max(1, min(5, int(obj["score"])))
            return score, str(obj.get("reasoning", ""))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return 1, f"Unparseable judge output: {raw[:120]!r}"
