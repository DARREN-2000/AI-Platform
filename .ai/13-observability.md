# 13 — Observability

## Logging
- MUST emit structured (JSON) logs with level, timestamp, and a request/trace id.
- MUST propagate the trace id across all calls (HTTP, DB, LLM, tools).
- MUST NOT log secrets, full PII, or full sensitive payloads.
- MUST log errors with context and a stack/cause; MUST NOT log-and-swallow.

## Metrics
- MUST expose key metrics: request rate, latency (p50/p95/p99), error rate, saturation.
- SHOULD track domain metrics (e.g. tokens, cost, eval scores) where relevant.
- MUST define SLOs for user-facing services and alert on error-budget burn.

## Tracing
- MUST emit spans for every LLM call, tool call, and agent node with inputs, outputs, tokens, cost, and latency.
- MUST make tracing a no-op when the backend (e.g. Langfuse/LangSmith) env vars are absent, so the app always runs.
- SHOULD link traces to the request id and (for AI) the eval/prompt version.

## Health
- MUST expose liveness and readiness endpoints.
- MUST make alerts actionable and tied to user impact; MUST NOT alert on noise.
