# 11 — Testing

## Baseline
- MUST add tests for every new behavior and every bug fix (regression test first).
- MUST keep unit tests fast and deterministic; MUST mock all network/LLM/DB calls in unit tests.
- MUST NOT leave untested logic in `src/`.
- MUST make the suite runnable from a clean clone with one command.

## Structure
- MUST mirror source layout in `tests/`; one clear reason per test.
- MUST test behavior and contracts, not private implementation details.
- SHOULD cover edge cases, error paths, and boundaries — not just the happy path.
- MUST mark live/external tests `@pytest.mark.integration` and skip them without credentials.

## Quality
- MUST make assertions specific; MUST NOT assert only "no exception".
- MUST NOT depend on test execution order or shared mutable fixtures.
- SHOULD use factories/builders over large inline fixtures.
- MUST keep tests green in CI; a flaky test MUST be fixed or quarantined immediately.

## AI / eval testing
- MUST keep eval regression tests in `tests/eval/` running against a small fixed set in CI.
- MUST separate deterministic checks from judge-based scoring.
- MUST set thresholds with margin to distinguish real regressions from noise.
