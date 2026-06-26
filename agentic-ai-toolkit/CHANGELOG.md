# Changelog

## 0.1.0

- Initial release.
- Core (stdlib-only, offline): LangGraph-style agent `Graph` + ReAct loop, tool
  registry with a safe calculator, TF-IDF / hashing RAG, span tracer,
  reliability primitives (idempotency, token bucket, HMAC, retries), and a
  composable `ChatService`.
- Provider middleware (`instrumentation.py`): `CachingProvider` (response cache)
  plus `MeteredProvider` / `UsageMeter` for token, cost, and latency tracking -
  wrap a real provider to conserve API budget and report spend.
- Structured output (`structured.py`): JSON extraction (handles fences/prose),
  a JSON-Schema-subset validator, and `generate_structured` with a self-repair
  retry loop.
- Tracing exporters: `to_langfuse` and `to_langsmith` convert a trace into
  Langfuse / LangSmith shapes without changing call sites.
- Env-driven FastAPI serving layer (`serving/app.py`, `create_app()`).
- Deployment: production `Dockerfile`, `docker-compose.yml`, and a Kubernetes +
  kustomize bundle (namespace, configmap, optional secret, deployment with
  probes, service, ingress, HPA).
- Tooling/CI: unit tests + offline demos, Docker build & container smoke test,
  ruff/black/mypy config, pre-commit hooks, devcontainer, and a runnable
  `examples/quickstart.py`.

## [Unreleased]

### Added
- `memory.py`: conversation memories (buffer, window, token-window, summarizing).
- `guardrails.py`: PII redaction, prompt-injection heuristics, length/blocklist checks, composable `Guardrail` pipeline.
- `planner.py`: `PlanAndExecuteAgent` (plan-first, then execute via ReAct sub-agent).
- `multiagent.py`: `Supervisor` with keyword/LLM routing across named agents.
- `prompts.py`: versioned `PromptTemplate` + `PromptLibrary`.
- `streaming.py`: `StreamingProvider` + offline `word_stream`.
- OpenRouter provider support (OpenAI-compatible base URL).
- `examples/extensions_demo.py` composing the new building blocks offline.
