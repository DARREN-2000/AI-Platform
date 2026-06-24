# Architecture & decisions

## Goals

1. **Readable in ~10 minutes** so it can be adapted under time pressure.
2. **Runs with zero external dependencies** (stdlib only) and zero API keys.
3. **Extensible at the seams** that real take-homes poke at: provider, judge,
   dataset, metrics, gate.

## Components

| Module | Responsibility | Key decision |
|---|---|---|
| `providers.py` | Talk to an LLM | Tiny `Provider` Protocol; `MockProvider` for offline determinism; real providers lazy-import their SDKs and retry with backoff. |
| `judge.py` | Score an answer | Structured JSON verdict; median-of-N to tame non-determinism; position-swap pairwise for bias control; normalized 0..1 score. |
| `dataset.py` | Load golden cases | JSONL (diff-friendly, versionable); tolerant of comments/blanks. |
| `metrics.py` | Aggregate | Report mean **and** stdev; pass-rate is the CI headline. |
| `runner.py` | Orchestrate + gate | `check_regression` compares mean to a baseline with a tolerance band. |
| `cli.py` | Operate | Non-zero exit on regression so CI fails the build. |

## Why these choices defend well in an interview

- **LLM-as-judge trust**: rubric + structured output + reasoning, calibrate vs
  human labels (hook: feed a human-labeled slice and measure judge agreement),
  control position/verbosity bias, prefer pairwise/reference-based grading.
- **Non-determinism**: fix temperature, sample multiple times, aggregate, report
  variance, set a tolerance band so noise is not flagged as regression.
- **Agent vs single-call eval**: evaluate the final outcome *and* the trajectory
  (tool selection, argument correctness, steps/cost) - see extension below.

## Obvious extensions (call these out, even if unbuilt)

- **Trajectory eval**: add `trajectory: list[Step]` to `EvalCase`; score tool
  choice + arguments per step alongside the final answer.
- **Tracing**: wrap `Provider.complete` to emit Langfuse/LangSmith spans and
  attach scores back to traces -> production traces become new eval cases.
- **Statistical rigor**: bootstrap confidence intervals on the mean; pick sample
  size from a target margin of error before calling a delta a regression.
- **Storage**: swap the JSON baseline for PostgreSQL (runs, cases, results) and
  expose an async FastAPI surface for long eval jobs.
