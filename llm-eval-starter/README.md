# llm-eval-starter

A lean, **adaptable** LLM-as-judge evaluation harness you can stand up fast and
bend to almost any take-home prompt. Runs **offline** with a deterministic mock
provider, swaps to OpenAI/Anthropic with one flag, and ships a **CI regression
gate** so quality drops fail the build instead of shipping.

## Why it exists

Most "evaluation" is a notebook with a few scores. Production evaluation is a
*gate*: golden datasets, an LLM-as-judge you can trust, variance you report, and
a regression check wired into CI. This repo is the smallest honest version of
that loop.

## Quickstart

```bash
make install            # pip install -e ".[dev]"
make test               # run the unit tests
make eval               # run evals with the offline mock provider
make baseline           # snapshot current scores to data/baseline.json
```

No API key needed for `mock`. For real judges:

```bash
pip install -e ".[openai]"
export OPENAI_API_KEY=...
python -m llm_eval.cli --provider openai --samples 3 --json
```

## How it works

```
data/golden.jsonl  ->  EvalRunner  ->  LLMJudge(provider)  ->  ScoreStats  ->  regression gate
```

- **`dataset.py`** loads versioned JSONL cases (`question`, `answer`, `rubric`, `expected_keywords`).
- **`judge.py`** prompts the judge for a structured `{score, reasoning}`; `score_robust` medians N samples; `pairwise` does a position-swap to fight position bias.
- **`metrics.py`** reports mean, **stdev**, a **bootstrap confidence interval** on the mean, and pass-rate.
- **`runner.py`** runs the set and `check_regression` compares the mean to a stored baseline.
- **`cli.py`** returns a non-zero exit code on regression, so CI gates on it; `--cache` adds response caching + token/cost/latency metering to conserve API budget.

## Adapt it in an interview

- **New task?** Replace `data/golden.jsonl` and the rubric; the rest is unchanged.
- **Agent / trajectory eval?** Add a `trajectory` field to `EvalCase` and a judge
  method that scores tool-selection and argument-correctness per step.
- **Real tracing?** Wrap `provider.complete` to emit Langfuse spans and attach
  the eval score to the trace.

See `ARCHITECTURE.md` for the design rationale and the obvious extension points.
