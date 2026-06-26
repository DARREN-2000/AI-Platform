# `.ai/` — AI Engineering Standards

A permanent engineering constitution for AI coding agents (Claude Code, Codex CLI, Cursor, Gemini CLI, Cline, Roo Code, Windsurf, Aider). Agents load these rule files **before writing code**.

This is not docs, a tutorial, or a handbook — only actionable rules (MUST / MUST NOT / SHOULD / SHOULD NOT / MAY). The root `CLAUDE.md` / `AGENTS.md` are thin routers; the detailed standards live here and are loaded on demand.

## How agents use it
1. Read `CLAUDE.md` / `AGENTS.md` (root) → routing table.
2. Always read `00-philosophy.md`, `01-general.md`, `02-decision-framework.md`.
3. Read the files matching the task (language, surface, delivery); ignore the rest.
4. Implement the simplest solution that fully satisfies the task.
5. Self-review against `19-review.md` + `20-checklists.md`; avoid `21-anti-patterns.md`.

## Files
| File | Scope |
| --- | --- |
| 00-philosophy.md | Core beliefs |
| 01-general.md | Cross-cutting engineering rules |
| 02-decision-framework.md | How to decide (the key file) |
| 03-architecture.md | Architecture per project type |
| 04-python.md | Python |
| 05-fastapi.md | FastAPI services |
| 06-typescript.md | TypeScript |
| 07-go.md | Go |
| 08-ai.md | LLMs / agents / RAG / eval |
| 09-database.md | Data & persistence |
| 10-security.md | Security |
| 11-testing.md | Testing |
| 12-performance.md | Performance |
| 13-observability.md | Logging / metrics / tracing |
| 14-docker.md | Containers |
| 15-kubernetes.md | Kubernetes |
| 16-deployment.md | CD strategies |
| 17-github.md | Git / PR / Actions |
| 18-documentation.md | Docs |
| 19-review.md | Self-review gates |
| 20-checklists.md | Stage checklists |
| 21-anti-patterns.md | What to avoid |
| 22-repository-templates.md | Folder templates |
| 23-prompts.md | Prompt/context standards |

## Templates
`templates/` holds reference scaffolding (pyproject, Dockerfile, docker-compose, GitHub Actions CI, eval gate, `.env.example`). Copy and adapt per project; do not wire CI from here directly.
