# Synera — AI / LLM Engineer take-home

This exercise is about **how you think about evaluating an AI agent**, not how much
code you can produce. We give you a small agent and recordings of it running. You
analyse the problem, design an evaluation approach — the design doc is the main
deliverable — and prove a thin slice of it in code. You'll go deep on code with us
live afterwards, so the take-home leans on your judgement, not your typing speed.

## Time

Budget about **4 focused hours** (hard ceiling: 6).

If you run out of time, stop and write up what you'd do next. Knowing what to cut is
part of the signal — we'd rather see sharp thinking than a half-built framework.

**AI tools are encouraged** — it's how we work. Own every line, and add a short
`AI_USAGE.md` noting what you used and how. We'll dig into the code together in the
follow-up, so be ready to defend it.

## What we give you

```
candidate-take-home/
  synera_eval/
    agent/        small synthetic LangGraph agents (FlowAgent) — context + reference
    data/
      traces.json       125 raw recorded runs of the agents, to analyse
      seed_labels.json  a small hand-labelled sample to start from
    loader.py     a minimal helper to load traces + seed labels
  tests/          one passing data sanity check; add your own
  pyproject.toml
```

We deliberately do **not** hand you an eval framework, full label taxonomy, or
evaluator interfaces. Designing and defending those choices is the point. The
seed labels are a small scaffold to bootstrap your thinking, not a complete
specification to copy.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Python 3.12+
pip install -e ".[dev]"
pytest -q          # data sanity checks should pass
```

Load the data with `from synera_eval.loader import load_traces, load_seed_labels`.
If you want to run a real LLM-as-judge, we provide an Anthropic API key by email.
Working fully offline with a deterministic stand-in is equally fine.

## The task

Hand back two things — a design doc and a thin proof-of-concept. How you spend your
time across them is your call.

**`SOLUTION.md` — how you'd evaluate this agent.** Dig into the agent and its traces,
then write a short design doc setting out the approach you'd take and why. We're
interested in your judgement: what actually matters here, what you'd measure, what
you'd build, what you'd skip, and where the provided data can and can't be trusted.
There's no template — decide what's worth saying.

**A proof-of-concept.** Pick the most important part of your design and make it **run**
on the real data — one evaluator producing a result is plenty. One thing working
end-to-end beats five half-built; we look at the seam (could the rest plug in?) more
than at coverage. Keep this intentionally thin: a small, clear running slice is
stronger than broad implementation.

## What to hand back

- `SOLUTION.md` — your design doc (primary)
- the POC — runnable, with a one-line "how to run"
- `AI_USAGE.md`

Hand it back as a **private git repository** (GitHub) with
**@bertolt**, **@Ahmed-dhouib99** and **@dspeckmann** added as a collaborators for the review

Make your **first commit the take-home exactly as we gave it to you**, unchanged, then
build your solution in the commits after it. We branch a short live coding exercise
from that initial commit in the follow-up, so please keep it clean.

## How we assess this

Primarily the **design doc** — the quality of your thinking and the judgement in what
you choose to measure, build, and leave out. The **POC** shows you can turn a design
into running code. We are **not** grading lines of code or coverage.

Afterwards we run a ~30-minute live session: a short walk-through of your work and a
small change to the agent together. That's where we go deep on code and agent
architecture — come ready to explain *why*, and to disagree with us where you think
we're wrong. We like that.

Good luck, and thank you. — The Agentic Ants team
