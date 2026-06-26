# 00 — Philosophy

## Core beliefs
- MUST optimize for correctness, readability, and maintainability over cleverness.
- MUST choose the simplest solution that fully satisfies the task.
- MUST treat generated code as production code by default.
- MUST prefer deleting code over adding code when both solve the problem.
- SHOULD make the change small and the diff reviewable.

## Judgment over dogma
- MUST adapt patterns to the task; rules guide decisions, they do not force technologies.
- MUST NOT apply a pattern, abstraction, or tool that the current task does not need.
- MUST justify any non-obvious decision in a comment or the PR/README, including the rejected alternative.
- SHOULD bias toward boring, well-understood technology.

## Definition of "done"
- MUST be: builds, types pass, lints clean, tests pass, runs from a clean clone.
- MUST update docs and config when behavior or interfaces change.
- MUST leave no secrets, dead code, or unexplained TODOs.

## When uncertain
- MUST state assumptions explicitly and pick a sensible default rather than stall.
- SHOULD prefer reversible decisions; defer irreversible ones until evidence exists.
- MUST NOT invent requirements, APIs, or data that were not given.
