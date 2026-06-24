"""Command-line entry point.

Examples:
    python -m llm_eval.cli --provider mock --json
    python -m llm_eval.cli --provider openai --samples 3 --cache
    python -m llm_eval.cli --update-baseline   # snapshot current scores

Exit code is non-zero on a regression, so CI fails the build automatically.
Pass --cache to cache + meter provider calls (saves API budget on reruns).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .cache import CachingProvider, MeteredProvider, UsageMeter
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
    if name == "openrouter":
        from .providers import OpenAIProvider

        # OpenRouter is OpenAI-compatible; many free models lack json mode.
        return OpenAIProvider(
            model=os.getenv("OPENROUTER_MODEL") or "meta-llama/llama-3.1-8b-instruct:free",
            name="openrouter",
            base_url=os.getenv("OPENAI_BASE_URL") or "https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
            json_mode=False,
        )
    raise SystemExit(f"Unknown provider: {name}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="llm-eval", description="Run LLM-as-judge evals.")
    parser.add_argument("--dataset", default="data/golden.jsonl")
    parser.add_argument(
        "--provider", default="mock", choices=["mock", "openai", "anthropic", "openrouter"]
    )
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--pass-threshold", type=float, default=0.6)
    parser.add_argument("--baseline", default="data/baseline.json")
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--cache", action="store_true", help="Cache + meter provider calls.")
    parser.add_argument("--json", action="store_true", help="Emit a JSON summary.")
    args = parser.parse_args(argv)

    cases = load_jsonl(args.dataset)
    provider = _build_provider(args.provider)
    meter = None
    cache = None
    if args.cache:
        meter = UsageMeter()
        cache = CachingProvider(MeteredProvider(provider, meter))
        provider = cache

    judge = LLMJudge(provider=provider, samples=args.samples)
    runner = EvalRunner(judge=judge, pass_threshold=args.pass_threshold)
    summary = runner.run(cases)

    out = summary.as_dict()
    if args.cache:
        out["usage"] = meter.summary()
        out["cache"] = cache.stats()

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        s = summary.stats
        print(
            f"cases={s.n} mean={s.mean:.3f} stdev={s.stdev:.3f} "
            f"pass_rate={s.pass_rate:.1%} ci=[{s.ci_low:.3f}, {s.ci_high:.3f}]"
        )
        for r in summary.results:
            print(f"  [{r.score}/5] {r.case_id}: {r.reasoning}")
        if args.cache:
            print(f"usage: {json.dumps(meter.summary())}")
            print(f"cache: {json.dumps(cache.stats())}")

    if args.update_baseline:
        Path(args.baseline).write_text(
            json.dumps(summary.stats.as_dict(), indent=2), encoding="utf-8"
        )
        print(f"Baseline updated -> {args.baseline}")
        return 0

    ok, msg = check_regression(summary, args.baseline)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
