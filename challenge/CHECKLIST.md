# Challenge & production readiness checklist

What a strong submission should cover. Each item notes the building block that
already exists so you only build what's challenge-specific. Tick what the prompt
actually asks for - don't gold-plate.

## 0. Challenge intake (do this first)
- [ ] Capture the exact prompt, inputs/outputs, and constraints in `NOTES.md`
- [ ] Write down assumptions + clarifying questions
- [ ] Time-box: decide MVP vs stretch before coding
- [ ] Define "done" = what the reviewer will run

## 1. Agent system
- [ ] Clear control flow (graph / state machine) - `toolkit/agent.py` (`Graph`, `ReActAgent`)
- [ ] Tools with safe execution + a registry - `toolkit/tools.py`
- [ ] Sub-agents / plan-and-execute if multi-step - `toolkit/planner.py`
- [ ] Multi-agent routing if multiple skills - `toolkit/multiagent.py` (`Supervisor`)
- [ ] Prompt iteration is versioned, not inline - `toolkit/prompts.py`
- [ ] Conversation memory if multi-turn - `toolkit/memory.py`
- [ ] Guardrails (PII, injection, limits) - `toolkit/guardrails.py`
- [ ] Streaming if a UX/latency requirement - `toolkit/streaming.py`
- [ ] Grounding / RAG if knowledge-based - `toolkit/rag.py`

## 2. Evaluation (the core competency)
- [ ] Versioned golden dataset (JSONL) - `eval/dataset.py`, `data/golden.jsonl`
- [ ] LLM-as-judge with structured, parseable verdicts - `eval/judge.py`
- [ ] Robustness: median-of-N + pairwise position-swap - `eval/judge.py`
- [ ] **Calibration against human labels** (kappa, correlation, FP/FN) - `eval/calibration.py`
- [ ] Stats: mean, stdev, **bootstrap CIs**, sample-size awareness - `eval/metrics.py`
- [ ] Reference metrics where gold answers exist - `eval/similarity.py`
- [ ] Regression gate wired into CI (non-zero exit on drop) - `eval/runner.py` (`check_regression`)
- [ ] Online/trace mining path (feed prod traces back into datasets) - design note in `NOTES.md`

## 3. Observability
- [ ] Tracing with spans - `toolkit/tracing.py`
- [ ] Export to Langfuse / LangSmith - `to_langfuse` / `to_langsmith`
- [ ] Cost / token / latency metering - `toolkit/instrumentation.py`

## 4. Reliability
- [ ] Retries with backoff - `toolkit/providers.with_retries`, `reliability.py`
- [ ] Timeouts + graceful degradation (offline fallback) - throughout
- [ ] Rate limiting - `reliability.TokenBucket`
- [ ] Idempotency for side-effecting calls - `reliability.IdempotencyStore`
- [ ] Webhook/signature verification if relevant - `reliability.sign/verify_signature`
- [ ] SLO thinking documented (latency/error budgets) - `NOTES.md`

## 5. Serving & API
- [ ] HTTP layer (FastAPI), health check, error handling - `toolkit/serving/app.py`, `challenge/app.py`
- [ ] Request/response schema validation
- [ ] Framework-agnostic core behind the API - `toolkit/service.py`

## 6. Persistence
- [ ] Storage behind an interface (in-memory <-> Postgres) - `toolkit/storage.py`
- [ ] `DATABASE_URL` config, no hardcoding - `challenge/config.py`
- [ ] Migrations / schema note if a real DB is required - `NOTES.md`

## 7. Config & secrets
- [ ] Everything env-driven - `config.py`, `.env.example`
- [ ] No secrets in the repo (keys via env only)
- [ ] Multiple providers selectable (OpenAI/Anthropic/OpenRouter) - `toolkit/config.build_provider`

## 8. Testing
- [ ] Unit tests for new logic
- [ ] Deterministic / offline tests (no network needed) - mock/rule providers
- [ ] Smoke test the full composition - `challenge/tests/test_smoke.py`

## 9. Packaging & deploy
- [ ] Dockerfile - `challenge/Dockerfile`, `toolkit/Dockerfile`
- [ ] docker-compose for local stack (app + db) - `toolkit/docker-compose.yml`
- [ ] k8s manifests if asked - `toolkit/deploy/`
- [ ] CI workflow (tests + eval gate)

## 10. Docs & submission polish
- [ ] README runnable in < 5 minutes
- [ ] ARCHITECTURE / decisions + trade-offs written down
- [ ] A one-command offline demo - `examples/run_offline.py`
- [ ] Clean commit history; remove dead scaffolding you didn't use
- [ ] Interview talking points: why these choices, what you'd do with more time
