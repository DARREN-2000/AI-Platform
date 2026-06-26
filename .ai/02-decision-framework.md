# 02 — Decision Framework

This is the primary file. For every decision: state **Decision**, **Conditions** (use it when), **Tradeoffs**, **Recommendation**. Default to the simplest option until a condition forces complexity.

## Async vs sync
- **Conditions:** Use async when the workload is I/O-bound and concurrent (network, DB, LLM calls) and the framework is async-native.
- **Tradeoffs:** Async adds complexity and footguns (blocking calls in the loop). Sync is simpler and fine for CPU-bound or low-concurrency code.
- **Recommendation:** SHOULD use async for service I/O paths; MUST NOT mix blocking calls into async paths; MAY stay sync for scripts, CLIs, and CPU-bound work.

## Caching
- **Conditions:** Introduce caching only after a measured hot path with repeated identical reads.
- **Tradeoffs:** Adds invalidation complexity and stale-data risk.
- **Recommendation:** SHOULD start with no cache; add in-process memoization before a network cache; MUST define TTL and invalidation before adding.

## Redis
- **Conditions:** Add when you need shared cache, rate limiting, queues, or pub/sub across instances.
- **Tradeoffs:** New infra to run, monitor, secure.
- **Recommendation:** MUST NOT add Redis for single-instance in-process needs; SHOULD use it when state must be shared across processes/instances.

## Docker
- **Conditions:** Add when the app needs reproducible runtime, has system deps, or will be deployed.
- **Tradeoffs:** Build/maintenance overhead.
- **Recommendation:** SHOULD containerize any deployable service; MAY skip for pure libraries and throwaway scripts.

## LangGraph
- **Conditions:** Use for multi-step agents needing explicit state, branching, loops, retries, checkpointing, or human-in-the-loop.
- **Tradeoffs:** Heavier than a single call or linear chain.
- **Recommendation:** MUST NOT use for a single LLM call or simple linear pipeline; SHOULD use when control flow and observability of steps matter.

## MCP
- **Conditions:** Use to expose tools/data to agents over a standard protocol reused across clients.
- **Tradeoffs:** Protocol/server overhead.
- **Recommendation:** SHOULD use MCP when tools are shared across multiple agents/clients; MAY call functions directly for a single in-process agent.

## Repository pattern
- **Conditions:** Use when persistence may change, or to isolate domain logic from data access for testing.
- **Tradeoffs:** Indirection.
- **Recommendation:** SHOULD apply for non-trivial domains with multiple data sources; MUST NOT wrap a single ORM call in a repository for its own sake.

## Clean architecture / layering
- **Conditions:** Apply layers when the domain is complex and long-lived.
- **Tradeoffs:** Boilerplate, ceremony.
- **Recommendation:** MUST NOT impose full clean architecture on small/medium projects; SHOULD keep a pragmatic 2-3 layer split (api / domain / infra) until size demands more.

## Dependency injection
- **Conditions:** Introduce when components have swappable implementations or need test doubles.
- **Tradeoffs:** Indirection, framework lock-in if using a DI container.
- **Recommendation:** SHOULD inject via constructor/parameters; MUST NOT add a DI framework unless wiring is genuinely complex.

## Interfaces / abstractions
- **Conditions:** Create an interface when there are >=2 real implementations or a clear, imminent second one.
- **Tradeoffs:** Premature abstraction is harder to remove than to add.
- **Recommendation:** MUST NOT create an interface for a single implementation; SHOULD remove an abstraction once it has only one user and adds no value.

## When to keep it simple
- MUST default to a single module/function until duplication or change pressure justifies structure.
- SHOULD prefer composition over inheritance.
- MUST revisit and delete abstractions that no longer earn their cost.
