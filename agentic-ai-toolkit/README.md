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
| `rag.py` | **Retrieval (RAG)** | LangChain / vector DBs | chunk -> embed -> store -> retrieve -> grounded prompt with citations; TF-IDF + hashing embedders |
| `tracing.py` | **Observability** | Langfuse / LangSmith | Nested spans + decorator + JSON trace export |
| `reliability.py` | **Production hardening** | webhooks / queues | Idempotency, token-bucket rate limiting, HMAC signature verify, retries w/ backoff |
| `service.py` + `serving/app.py` | **Serving** | FastAPI | Framework-agnostic `ChatService` behind a thin HTTP layer |
| `evaluate_trajectory` | **Eval bridge** | (pairs with `llm-eval-starter`) | Scores the agent's *path* (tool choice/order), not just the answer |

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
