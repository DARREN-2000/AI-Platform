# challenge

A ready-to-fill workspace for the take-home. The structure and prod-readiness
checklist are in place **now**; once the actual challenge lands you drop its spec
into `NOTES.md` and wire in the existing, already-tested building blocks from the
sibling packages instead of starting from scratch.

## What this reuses

- **`agentic-ai-toolkit`** - agent graphs, tools, RAG, memory, guardrails,
  prompts, multi-agent routing, streaming, tracing, reliability, cost/caching,
  storage (Postgres adapter), and a FastAPI service.
- **`llm-eval-starter`** - LLM-as-judge, golden-dataset versioning, bootstrap
  CIs, CI regression gate, reference-based similarity metrics, and judge
  **calibration against human labels**.

Nothing here re-implements those; it composes them.

## Layout

```
challenge/
  README.md            this file
  CHECKLIST.md         what a complete challenge + prod submission needs
  NOTES.md             paste the real challenge spec / decisions here
  pyproject.toml       package metadata (+ how to install siblings)
  .env.example         configuration surface
  Makefile             install / test / eval / demo / serve
  Dockerfile           container entrypoint
  src/challenge/
    config.py          env-driven settings (provider, model, DATABASE_URL)
    agent.py           builds the agent / service from the toolkit
    evaluation.py      builds the eval runner + calibration from llm-eval
    app.py             FastAPI app (lazy import; reuses ChatService)
  data/
    golden.jsonl       placeholder golden dataset
    human_labels.jsonl placeholder human labels (for calibration)
  examples/run_offline.py   end-to-end offline demo (no API keys)
  tests/test_smoke.py       smoke test the composition stays wired
```

## Quick start (offline, no keys)

```bash
# from the repo root, make the sibling packages importable
export PYTHONPATH="$PWD/agentic-ai-toolkit/src:$PWD/llm-eval-starter/src:$PWD/challenge/src"
python challenge/examples/run_offline.py
```

or with the Makefile (handles PYTHONPATH for you):

```bash
cd challenge
make demo      # run the offline end-to-end demo
make test      # smoke test
make eval      # run the eval over data/golden.jsonl
```

## When the challenge arrives

1. Paste the prompt + constraints into `NOTES.md`; list clarifying questions.
2. Walk `CHECKLIST.md` and tick what the prompt actually asks for (don't gold-plate).
3. Point `config.py` / `.env` at the right provider and `DATABASE_URL`.
4. Fill `data/golden.jsonl` with real cases and `data/human_labels.jsonl` with
   a few human scores, then run `make eval` and calibrate.
5. Implement task-specific logic in `agent.py` / `evaluation.py`, leaning on the
   toolkit + eval packages. Add tests as you go.
