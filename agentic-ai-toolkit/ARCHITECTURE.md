# Architecture & decisions

## Design goals

1. **Readable in ~15 minutes**, so it can be adapted under interview pressure.
2. **Runs with zero dependencies and zero API keys** (stdlib only) - tests are
   fast and deterministic.
3. **Extensible at the seams** real take-homes poke at: provider, tool, graph,
   retriever, tracer, transport.

## Module map

| Module | Responsibility | Key decision |
|---|---|---|
| `providers.py` | Talk to an LLM | Tiny `Provider` Protocol; `ScriptedLLM`/`RuleBasedLLM` for offline determinism; real providers lazy-import their SDKs and retry with backoff. |
| `tools.py` | The agent's hands | Registry of data-defined tools; calculator uses an AST walk (no `eval`) so it is injection-safe. |
| `agent.py` | Orchestration | Control flow is an explicit `Graph` (LangGraph-shaped) not a hidden loop; ReAct model/tools nodes; step budget; recorded trajectory. |
| `rag.py` | Retrieval | chunk->embed->store->retrieve->ground; TF-IDF (corpus-fitted) and hashing embedders behind one `Embedder` Protocol. |
| `tracing.py` | Observability | Nested spans -> JSON tree shaped like Langfuse; swap `export()` for a real client without touching call sites. |
| `reliability.py` | Production hardening | Idempotency, token bucket (injectable clock), constant-time HMAC verify, retries. |
| `service.py` | Composition | Framework-agnostic `ChatService` ties retrieval+agent+tracing; HTTP layer is a thin wrapper. |

## Interview talking points (defend these)

- **Why a graph, not a while-loop?** Explicit nodes/edges make agent control
  flow inspectable, testable, and resumable - the LangGraph thesis. Adding a
  "reflect" or "human-approval" node is a new node + edge, not a rewrite.
- **Agent eval = outcome + trajectory.** `evaluate_trajectory` scores tool
  choice and order; combine with an LLM-as-judge on the final answer. Report
  both, plus cost/steps.
- **RAG quality knobs:** chunk size/overlap, embedder choice (TF-IDF vs dense),
  k, and whether to rerank. The grounded prompt forces citations so answers are
  auditable.
- **Determinism & testing:** scripted providers + injectable clocks mean the
  whole agent is unit-tested without network or flakiness.
- **Reliability:** at-least-once delivery (webhooks/queues) demands idempotency;
  signature verification must be constant-time; external calls must retry.
- **Observability:** spans turn an opaque agent run into a debuggable trace, and
  production traces become new eval cases.

## Obvious extensions (mention even if unbuilt)

- **Real vector DB**: implement the `Embedder` Protocol with a hosted model and
  back `VectorStore` with pgvector/FAISS/Qdrant.
- **Langfuse tracing**: wrap `Provider.complete` and the agent nodes to emit
  spans; attach eval scores back to traces.
- **Streaming + async**: make `ChatService.chat` async and stream tokens through
  the FastAPI layer (SSE/websockets).
- **Persistence/checkpointing**: serialize `AgentState` between graph steps to
  support pause/resume and human-in-the-loop approvals.
- **Trajectory eval at scale**: feed recorded trajectories into the companion
  `llm-eval-starter` regression gate so agent-quality drops fail CI.
