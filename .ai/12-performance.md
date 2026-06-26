# 12 — Performance

## Discipline
- MUST measure before optimizing; MUST NOT optimize on speculation.
- MUST optimize the proven bottleneck, not the easy-to-change code.
- SHOULD prefer a clearer algorithm/data structure over micro-optimization.

## I/O & concurrency
- MUST batch or parallelize independent I/O; MUST NOT issue N+1 queries or calls.
- MUST set timeouts on all external calls; MUST bound concurrency (pools, semaphores).
- MUST stream or paginate large datasets; MUST NOT load unbounded data into memory.

## Caching & resources
- MUST add caching only per the decision framework (measured hot path, defined TTL + invalidation).
- MUST release resources deterministically (context managers / defer).
- SHOULD precompute or memoize pure, repeated, expensive work.

## AI-specific
- MUST minimize tokens: trim context, avoid redundant calls, cache deterministic prompts.
- SHOULD pick the smallest model that meets the quality bar; escalate only when needed.
- MUST track per-request token/cost and set budget limits.
