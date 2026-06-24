# agentic-ai-toolkit

Composable, **offline-runnable** building blocks for agentic-AI take-homes. Each
module is dependency-free (Python stdlib only), deterministic, and fully tested,
so you can demo it without API keys and **adapt it fast** to whatever the prompt
asks for. Every piece maps cleanly to a production framework at its seams.

## The directions covered

| Module | Direction | Maps to | What it demonstrates |
|---|---|---|---|
| `agent.py` | **Agent orchestration** | LangGraph | Explicit state `Graph` (nodes + conditional edges) + a ReAct tool loop with a step budget and a recorded trajectory |
| `tools.py` | **Tool use** | function/tool calling | Registry pattern; a safe (AST-based, no `eval`) calculator + lookup tool |
| `rag.py` | **Retrieval (RAG)** | LangChain / vector DBs | chunk -> embed -> store -> retrieve -> grounded prompt with citations |
| `tracing.py` | **Observability** | Langfuse / LangSmith | Nested spans + decorator + JSON trace export, plus `to_langfuse` / `to_langsmith` converters |
| `reliability.py` | **Production hardening** | webhooks / queues | Idempotency, token-bucket rate limiting, HMAC signature verify, retries w/ backoff |
| `service.py` + `serving/app.py` | **Serving** | FastAPI | Framework-agnostic `ChatService` behind a thin HTTP layer |
| `evaluate_trajectory` | **Eval bridge** | (pairs with `llm-eval-starter`) | Scores the agent's *path* (tool choice/order), not just the answer |
| `instrumentation.py` | **Cost control** | provider middleware | Response caching + token/cost/latency metering to conserve API budget |
| `structured.py` | **Structured output** | function-calling / JSON mode | Extract + validate JSON against a schema with a self-repair retry loop |

> Pairs with the companion **`llm-eval-starter`** repo (LLM-as-judge + CI
> regression gate). Together they cover eval **and** the agent/RAG/serving stack.

## Quickstart

```bash
make install          # pip install -e ".[dev]"
make test             # run the full unit-test suite
make demo             # run the agent + RAG demos (offline, no keys)
```

Offline demos:

```bash
python -m agentic_toolkit.cli agent "what is 21 * 2"      # tool-using agent
python -m agentic_toolkit.cli rag   "capital of France"    # retrieval + grounding
python -m agentic_toolkit.cli chat  "capital of France?"   # full service + trace
```

Serve it over HTTP:

```bash
pip install -e ".[serve]"
uvicorn serving.app:app --reload
# POST /chat {"question": "..."}   GET /health
```

Swap in a real model (no other code changes):

```python
from agentic_toolkit.providers import OpenAIProvider
from agentic_toolkit.agent import ReActAgent
agent = ReActAgent(provider=OpenAIProvider())   # set OPENAI_API_KEY
```

## How the agent works

```
        +-----------+   action    +-----------+
  ----> |   model   | ----------> |   tools   |
        +-----------+             +-----------+
              |  final                  |
              v                         | observation
            (END) <--------------------- (loop back to model)
```

The model node asks the provider for `ACTION: <tool> <json>` or `FINAL: <text>`.
A conditional edge routes to the tools node or to `END`. Every tool call is
appended to `state.trajectory`, which `evaluate_trajectory` can grade.

See `ARCHITECTURE.md` for design rationale, interview talking points, and the
obvious extension points (real vector DB, Langfuse spans, trajectory eval).

## Cost, caching & structured output

When you switch to a real provider, wrap it to cache repeats and track spend
(crucial when an eval re-runs the same prompts):

```python
from agentic_toolkit import CachingProvider, MeteredProvider, UsageMeter, OpenAIProvider
meter = UsageMeter()
provider = CachingProvider(MeteredProvider(OpenAIProvider(), meter))  # use in ReActAgent/ChatService
print(meter.summary())   # {calls, total_tokens, cost_usd, avg_latency_ms, ...}
print(provider.stats())  # {hits, misses, hit_rate, size}
```

Get typed, validated output from any model (with an automatic repair retry):

```python
from agentic_toolkit import generate_structured
schema = {"type": "object", "required": ["score"],
          "properties": {"score": {"type": "integer", "minimum": 1, "maximum": 5}}}
verdict = generate_structured(provider, messages, schema)  # dict guaranteed to match the schema
```

Ship traces to your platform without changing call sites:

```python
from agentic_toolkit import to_langfuse, to_langsmith
to_langfuse(tracer.export())    # Langfuse observations payload
to_langsmith(tracer.export())   # LangSmith run tree
```

## Deploy

The service is configured entirely through environment variables, so adapting it
to a challenge is usually just editing `.env` (Docker) or the ConfigMap (k8s) -
not the code.

| Variable | Default | Purpose |
|---|---|---|
| `AGENTIC_PROVIDER` | `rules` | `rules` (offline, no keys), `openai`, or `anthropic` |
| `AGENTIC_MODEL` | provider default | model name override |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | - | only for real providers |
| `AGENTIC_DOCS_PATH` | built-in demo docs | newline-delimited docs file for RAG |
| `PORT` | `8000` | HTTP port |

Endpoints: `GET /health`, `POST /chat {"question": "...", "k": 3}`.

```bash
make docker-build && cp .env.example .env && make docker-run   # Docker
make compose-up                                                # docker compose
kubectl apply -k deploy/k8s                                    # Kubernetes (kustomize)
```

The Kubernetes bundle ships a Namespace, ConfigMap, optional Secret, Deployment
(2 replicas, liveness/readiness probes on `/health`, resource requests+limits),
Service, Ingress, and an HPA (2-6 replicas at 70% CPU). The offline `rules`
provider needs no Secret. Full instructions: `deploy/README.md`.

## Project layout & tooling

```
src/agentic_toolkit/   core library (stdlib only)
serving/               FastAPI app (create_app, env-driven)
tests/                 offline, deterministic unit tests
examples/quickstart.py runnable API tour: PYTHONPATH=src python examples/quickstart.py
deploy/k8s/            kustomize bundle
Dockerfile, docker-compose.yml, .env.example
```

```bash
make test    # pytest
make lint    # ruff + black --check
make fmt     # auto-fix
```

Pre-commit hooks (`.pre-commit-config.yaml`), a devcontainer
(`.devcontainer/`), and CI workflows for both tests and Docker
(`.github/workflows/`) are included.
