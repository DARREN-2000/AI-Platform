# 18 — Documentation

## README (every project)
- MUST state what the project does, how to install, run, test, and configure.
- MUST document every environment variable and provide `.env.example`.
- MUST keep run instructions reproducible from a clean clone.
- SHOULD include architecture overview and key design decisions with rationale.

## Code
- MUST document public APIs (params, returns, raised errors).
- SHOULD comment *why*, not *what*; MUST NOT leave stale or misleading comments.
- MUST update docs in the same change that alters behavior or interfaces.

## Decisions
- SHOULD record significant/irreversible decisions (short ADR or README note) with the rejected alternative.
- MUST document operational runbooks for production services (deploy, rollback, on-call).

## AI specifics
- MUST document prompts' purpose/version, eval methodology, metrics, and known limitations.
- MUST document model/provider configuration and fallback behavior.
