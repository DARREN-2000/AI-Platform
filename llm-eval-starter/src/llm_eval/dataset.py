"""Golden dataset loading.

JSONL keeps cases diff-friendly and easy to version. Blank lines and lines
starting with '#' are ignored so you can annotate the file.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvalCase:
    id: str
    question: str
    answer: str = ""
    rubric: str = ""
    expected_keywords: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, d: dict) -> "EvalCase":
        return cls(
            id=str(d["id"]),
            question=d["question"],
            answer=d.get("answer", ""),
            rubric=d.get("rubric", ""),
            expected_keywords=tuple(d.get("expected_keywords", [])),
            tags=tuple(d.get("tags", [])),
        )


def load_jsonl(path: str | Path) -> list[EvalCase]:
    cases: list[EvalCase] = []
    for i, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            cases.append(EvalCase.from_dict(json.loads(line)))
        except (json.JSONDecodeError, KeyError) as exc:
            raise ValueError(f"Bad eval case on line {i}: {exc}") from exc
    return cases
