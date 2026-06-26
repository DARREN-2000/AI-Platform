# 04 — Python

## Baseline
- MUST target Python 3.11+ and use full type hints on all public functions.
- MUST pass `mypy` (or `pyright`) with no ignored errors except justified, commented `# type: ignore[code]`.
- MUST format and lint with `ruff`; CI MUST fail on violations.
- MUST manage deps with `uv` or `poetry` and commit a lockfile.

## Types & data
- MUST use `pydantic` v2 models (or dataclasses) at all I/O boundaries.
- MUST NOT use `Any` except at true dynamic edges, and MUST narrow it immediately.
- SHOULD prefer `Enum`/`Literal` over bare strings for closed sets.
- MUST use `pathlib`, not string path manipulation.

## Functions & errors
- MUST raise specific exceptions; MUST NOT `except Exception:` without re-raise or structured handling.
- MUST NOT use mutable default arguments.
- SHOULD return explicit result/error types at boundaries.

## Async
- MUST NOT call blocking I/O inside `async` functions; offload to a thread/executor if unavoidable.
- MUST set timeouts on all awaited I/O.
- SHOULD use structured concurrency (`asyncio.TaskGroup`) over loose tasks.

## Style
- MUST keep imports at module top; no unused imports.
- MUST use logging, not `print`, in library/service code.
- SHOULD use context managers for all resources.
- MUST make modules import-safe (no side effects at import time).
