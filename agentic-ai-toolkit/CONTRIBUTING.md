# Contributing

Thanks for taking a look! This repo favors small, dependency-free, well-tested
building blocks.

## Setup

```bash
make install        # editable install with dev extras
make test           # run the unit-test suite
make lint           # ruff + black --check
make fmt            # auto-fix imports/formatting
```

## Conventions

- **Standard library only** in the core package; heavier deps live behind
  optional extras (`serve`, `openai`, `anthropic`).
- Every public behavior gets a unit test, and tests must run **offline and
  deterministically** (no network, no API keys).
- Keep modules readable end-to-end; prefer clarity over cleverness.
- Run `make lint` and `make test` before opening a PR (pre-commit will too).
