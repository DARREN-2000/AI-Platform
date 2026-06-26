# 14 — Docker

## Images
- MUST use multi-stage builds; final image contains only runtime artifacts.
- MUST pin a specific minimal base image (e.g. `python:3.11-slim`); MUST NOT use `latest`.
- MUST run as a non-root user.
- MUST add a `.dockerignore` excluding `.git`, `.env`, caches, and tests.

## Build
- MUST order layers for cache efficiency (dependencies before source).
- MUST install pinned dependencies from a lockfile.
- MUST NOT bake secrets into images or layers; use build args/secrets mounts only for non-persistent needs.
- SHOULD keep images small and single-purpose (one process per container).

## Runtime
- MUST define a `HEALTHCHECK` or rely on orchestrator probes.
- MUST make the container handle SIGTERM and shut down gracefully.
- MUST set `PYTHONUNBUFFERED=1` (or equivalent) for immediate logs.
- SHOULD expose config via environment variables only.

## Compose (local/dev)
- SHOULD use Docker Compose for local multi-service dev with healthchecks and `depends_on: condition: service_healthy`.
- MUST NOT use dev compose files as the production deployment unit.
