# 19 — Self-Review (run before declaring done)

Review every change against each dimension. Fix or explicitly justify each finding.

## Correctness
- [ ] Does it do exactly what the task asked, including edge cases and error paths?
- [ ] Are assumptions stated and reasonable?

## Architecture
- [ ] Is the structure as simple as the task allows? Any abstraction without >=2 users?
- [ ] Is I/O separated from logic? Dependency direction correct?

## Naming & readability
- [ ] Are names intention-revealing? Would a new reader understand it quickly?
- [ ] Any dead code, commented-out blocks, or unexplained TODOs? (remove)

## Complexity
- [ ] Any function/file doing too much? Any needless pattern or premature optimization?

## Testing
- [ ] New behavior and bug fixes covered? Network/LLM mocked in unit tests? Suite green?

## Security
- [ ] No secrets committed. Inputs validated. Output/LLM results treated as untrusted.

## Logging & observability
- [ ] Structured logs with trace id? Errors logged with context? Spans for LLM/tool/node calls? No secrets logged?

## Performance
- [ ] No N+1. Timeouts and bounded concurrency on I/O. No unbounded memory.

## Configuration
- [ ] All config env-driven and validated at startup. `.env.example` updated.

## Error handling
- [ ] Specific exceptions, no catch-all swallow. Graceful degradation with retries/fallbacks.

## Deployment readiness
- [ ] Health/readiness present. Migrations backward-compatible. Rollback path exists.

## Documentation
- [ ] README updated: what/why/how-to-run + results/metrics where relevant.
