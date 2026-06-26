# 21 — Anti-Patterns

MUST NOT introduce any of the following. If one already exists in touched code, SHOULD fix or flag it.

## Design
- **Overengineering:** abstractions, layers, or patterns the task does not need.
- **Premature optimization:** tuning before profiling.
- **Needless design patterns:** patterns applied for their own sake.
- **Leaky abstractions:** wrappers that expose the thing they wrap.
- **Framework abuse:** bending a framework against its grain.
- **Speculative generality:** building for imagined future requirements.

## Code
- **God classes / massive files:** units doing too many things.
- **Hidden state:** implicit globals, singletons, module-level mutable state.
- **Global variables:** shared mutable globals.
- **Magic numbers/strings:** unexplained literals.
- **Duplicate code:** copy-paste instead of extraction.
- **Poor naming:** vague, abbreviated, or misleading names.
- **Catch-all exceptions:** `except Exception` / empty catch that hides failures.
- **Blocking async code:** synchronous I/O inside async paths.
- **Unused dependencies/imports:** dead weight.

## Security / ops
- **Hardcoded secrets:** credentials in code or images.
- **Unvalidated input:** trusting external or LLM data.
- **Silent failures:** swallowed errors with no log/metric.
- **Unbounded work:** missing timeouts, pagination, retries, or step/cost limits.

## AI-specific
- **Trusting model output blindly:** executing or persisting unvalidated output.
- **Prompt injection by concatenation:** user text mixed into instructions.
- **Agent where a function suffices:** needless agent/LLM for deterministic work.
- **Untracked LLM calls:** no tracing, cost, or eval coverage.
