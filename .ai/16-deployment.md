# 16 — Deployment

## Pipeline
- MUST deploy only artifacts that passed CI (lint, types, tests, security, eval gate).
- MUST build once and promote the same immutable artifact across environments.
- MUST NOT deploy manually from a developer machine to production.

## Strategies
- **Rolling:** SHOULD be the default for stateless services with backward-compatible changes.
- **Blue/Green:** SHOULD use when you need instant cutover and instant rollback.
- **Canary:** SHOULD use for high-risk changes; route a small % first, watch metrics, then ramp.
- MUST keep changes backward-compatible during rollout (expand/contract for schema and APIs).

## Rollback
- MUST have an automated, tested rollback path before deploying.
- MUST trigger rollback automatically on health/SLO breach.
- MUST make migrations reversible or forward-fixable without data loss.

## Health & readiness
- MUST gate traffic on readiness; MUST NOT send traffic before dependencies are ready.
- MUST verify liveness/readiness in staging before production.

## Environment management
- MUST keep environments isolated (config, data, credentials).
- MUST manage secrets per environment via a secret manager.
- MUST make deployments idempotent and reproducible from version control (IaC).
- SHOULD verify post-deploy with smoke checks and monitor before declaring success.
