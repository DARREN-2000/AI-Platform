"""Reference eval gate.

Fails CI when the aggregate score drops below the threshold. Adapt scoring to the
task: run cheap deterministic checks first, then LLM-as-judge for open-ended
quality. Keep it deterministic enough to separate real regressions from noise.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_cases(dataset_dir: Path) -> list[dict]:
    cases: list[dict] = []
    for f in sorted(dataset_dir.glob("*.jsonl")):
        for line in f.read_text().splitlines():
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def score_case(case: dict) -> float:
    """Replace with real scoring (deterministic checks + judge)."""
    expected = case.get("expected")
    actual = case.get("actual", expected)
    return 1.0 if actual == expected else 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--threshold", type=float, default=0.8)
    args = parser.parse_args()

    cases = load_cases(Path(args.dataset))
    if not cases:
        print("No eval cases found; failing closed.")
        return 1

    scores = [score_case(c) for c in cases]
    aggregate = sum(scores) / len(scores)
    print(f"eval cases={len(cases)} score={aggregate:.3f} threshold={args.threshold:.3f}")
    return 0 if aggregate >= args.threshold else 1


if __name__ == "__main__":
    sys.exit(main())
