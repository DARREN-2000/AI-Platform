# Engineering Constitution — Agent Instructions

> This file is an exact mirror of `CLAUDE.md`. Different agents read different filenames; both resolve the same `.ai/` standards. Keep the two in sync.

You are an AI coding agent working in this repository. Before writing or changing code you MUST follow this protocol. The detailed standards live in `.ai/`. This file is a thin router — keep it that way.

## Protocol
1. READ the relevant standards. Always read `.ai/00-philosophy.md`, `.ai/01-general.md`, and `.ai/02-decision-framework.md`. Then read the files matching the task:
   - Language: `.ai/04-python.md` / `.ai/06-typescript.md` / `.ai/07-go.md`
   - Surface: `.ai/05-fastapi.md`, `.ai/08-ai.md`, `.ai/09-database.md`
   - Cross-cutting: `.ai/10-security.md`, `.ai/11-testing.md`, `.ai/12-performance.md`, `.ai/13-observability.md`, `.ai/17-github.md`, `.ai/18-documentation.md`
   - Delivery: `.ai/14-docker.md`, `.ai/15-kubernetes.md`, `.ai/16-deployment.md`
   - New repo/module: `.ai/03-architecture.md`, `.ai/22-repository-templates.md`
   - Prompt work: `.ai/23-prompts.md`
2. DETERMINE which rules apply to this specific task.
3. IGNORE irrelevant files. Do not apply rules or patterns the task does not need.
4. ADAPT to the task. Choose the simplest solution that fully satisfies it. Standards guide decisions; they do not force technologies.
5. PRODUCE production-quality code: correct, readable, tested, secure, observable, documented. Honor every MUST in the relevant files; justify any deviation.
6. SELF-REVIEW before finishing using `.ai/19-review.md` and `.ai/20-checklists.md`. Avoid everything in `.ai/21-anti-patterns.md`. Re-run lint, types, and tests.

## Hard rules (always)
- MUST NOT hardcode or commit secrets.
- MUST validate all external and LLM output before use.
- MUST add tests for new logic and keep CI green.
- MUST prefer the simplest solution; MUST NOT overengineer.
- MUST state assumptions instead of inventing requirements.

Reference scaffolding lives in `.ai/templates/`.
