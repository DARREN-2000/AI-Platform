# 20 — Checklists

## Before coding
- [ ] MUST restate the task and list assumptions.
- [ ] MUST identify which `.ai/` files apply and read them.
- [ ] MUST choose the simplest viable approach (apply 02-decision-framework).
- [ ] MUST confirm scope: smallest change that fully solves the task.

## Before commit
- [ ] MUST run format, lint, type-check, and tests — all green.
- [ ] MUST remove debug code, dead code, and commented-out blocks.
- [ ] MUST verify no secrets are staged.
- [ ] MUST write a focused, conventional commit message.

## Before PR
- [ ] MUST keep the diff small and single-purpose.
- [ ] MUST update README/docs and `.env.example` for any change.
- [ ] MUST add/extend tests for new logic and bug fixes.
- [ ] MUST self-review against 19-review.md.

## Before merge
- [ ] MUST have all CI checks green (lint, types, tests, security, eval gate).
- [ ] MUST resolve all review threads.
- [ ] MUST confirm migrations are backward-compatible.

## Before release
- [ ] MUST tag a versioned, immutable artifact.
- [ ] MUST verify changelog/release notes.
- [ ] MUST confirm rollback path exists.

## Before deployment
- [ ] MUST deploy to staging and verify health/readiness.
- [ ] MUST confirm config and secrets are present per environment.
- [ ] MUST choose a rollout strategy (rolling/blue-green/canary) per risk.

## Before production
- [ ] MUST verify observability (logs, metrics, traces, alerts) is live.
- [ ] MUST confirm SLOs and error budgets are monitored.
- [ ] MUST confirm automated rollback and on-call awareness.
- [ ] For AI: MUST confirm eval baselines, guardrails, and cost/token limits are active.
