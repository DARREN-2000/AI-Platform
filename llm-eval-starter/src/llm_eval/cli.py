"""Command-line entry point.

Examples:
    python -m llm_eval.cli --provider mock --json
    python -m llm_eval.cli --provider openai --samples 3
    python -m llm_eval.cli --update-baseline   # snapshot current scores

Exit code is non-zero on a regression, so CI fails the build automatically.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .dataset import load_jsonl
from .judge import LLMJudge
from .providers import MockProvider
from .runner import EvalRunner, check_regression


def _build_provider(name: str):
    if name == "mock":
        return MockProvider()
    if name == "openai":
        from .providers import OpenAIProvider

        return OpenAIProvider()
    if name == "anthropic":
        from .providers import AnthropicProvider

        return AnthropicProvider()
    raise SystemExit(f"Unknown provider: {name}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="llm-eval", description="Run LLM-as-judge evals.")
    parser.add_argument("--dataset", default="data/golden.jsonl")
    parser.add_argument("--provider", default="mock", choices=["mock", "openai", "anthropic"])
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--pass-threshold", type=float, default=0.6)
    parser.add_argument("--baseline", default="data/baseline.json")
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit a JSON summary.")
    args = parser.parse_args(argv)

    cases = load_jsonl(args.dataset)
    judge = LLMJudge(provider=_build_provider(args.provider), samples=args.samples)
    runner = EvalRunner(judge=judge, pass_threshold=args.pass_threshold)
    summary = runner.run(cases)

    if args.json:
        print(json.dumps(summary.as_dict(), indent=2))
    else:
        s = summary.stats
        print(f"cases={s.n} mean={s.mean:.3f} stdev={s.stdev:.3f} pass_rate={s.pass_rate:.1%}")
        for r in summary.results:
            print(f"  [{r.score}/5] {r.case_id}: {r.reasoning}")

    if args.update_baseline:
        Path(args.baseline).write_text(json.dumps(summary.stats.as_dict(), indent=2), encoding="utf-8")
        print(f"Baseline updated -> {args.baseline}")
        return 0

    ok, msg = check_regression(summary, args.baseline)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
