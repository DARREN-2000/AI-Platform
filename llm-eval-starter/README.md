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

Or judge with any OpenAI-compatible endpoint - e.g. **OpenRouter** (free models
work; the key stays in your env):

```bash
pip install -e ".[openai]"
export OPENROUTER_API_KEY=sk-or-...
export OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
python -m llm_eval.cli --provider openrouter --cache --json
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

## Metrics beyond the judge

`similarity.py` adds deterministic, reference-based metrics for when you have gold answers: `exact_match`, `token_f1`, `cosine_similarity` (hashed bag-of-words), and `keyword_recall`. Use them standalone or to cross-check the LLM judge — they are fast, free, and fully reproducible.

## Judge calibration against human labels

An uncalibrated judge is just a vibe. `calibration.py` quantifies how well the
LLM judge agrees with human gold labels: exact agreement, Cohen's kappa and
ordinal (quadratic-weighted) kappa, Pearson/Spearman correlation, MAE, and a
`confusion_at_threshold` that reports **false-positive / false-negative rates**
at your pass threshold - the asymmetric errors that matter when an eval gates
shipping. Use `calibrate(judge_scores, human_scores)` for a one-call report.
