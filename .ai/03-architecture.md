# 03 — Architecture

## General
- MUST match architecture to project size and lifespan; do not pre-build for imagined scale.
- MUST separate I/O (network, DB, LLM, filesystem) from pure business logic.
- SHOULD keep a clear dependency direction: outer layers depend on inner, never the reverse.
- MUST make the entry point thin; push logic into testable units.

## By project type
- **Small project / script:** MUST stay single-module or a flat package; MUST NOT add layers or DI.
- **Medium project:** SHOULD use a pragmatic split: `api`/`domain`/`infra` (or equivalent). MAY add a service layer.
- **Large project:** SHOULD use modular boundaries by domain; MUST enforce boundaries (no cross-domain imports of internals).
- **Library:** MUST expose a minimal, stable public API; MUST hide internals; MUST NOT depend on app frameworks.
- **CLI:** MUST separate argument parsing from logic; logic MUST be importable and testable.
- **Microservice:** MUST own its data; MUST expose health/readiness; MUST be independently deployable.
- **AI agent:** MUST separate orchestration (graph/state) from tools, prompts, and providers; MUST make each tool independently testable.
- **REST API:** MUST validate at the edge, keep handlers thin, push logic to services; MUST version the public contract.
- **Data pipeline:** MUST make stages idempotent and re-runnable; MUST checkpoint; MUST separate extract/transform/load.
- **ML project:** MUST separate data, training, eval, and serving; MUST version data, configs, and models; MUST make runs reproducible.

## Boundaries
- MUST define module boundaries by responsibility, not by technical layer alone.
- MUST NOT leak framework or ORM types across domain boundaries.
- SHOULD keep configuration and wiring in one composition root.
