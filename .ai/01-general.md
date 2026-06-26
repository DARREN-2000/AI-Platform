# 01 — General

## Naming & structure
- MUST use intention-revealing names; no abbreviations except well-known ones.
- MUST keep functions small and single-purpose; extract when a function does two things.
- SHOULD keep files focused; split when a file mixes unrelated responsibilities.
- MUST NOT exceed reasonable size for a unit (function, class, module) without justification.

## Errors
- MUST fail fast on programmer errors; handle and recover from expected runtime errors.
- MUST NOT catch broad exceptions silently; catch specific errors and add context.
- MUST never swallow an error without logging or re-raising.
- SHOULD return typed errors/results at boundaries, not booleans or magic values.

## Configuration
- MUST load all config from environment/secret stores; never hardcode secrets, hosts, or model names.
- MUST validate config at startup and fail loudly on missing/invalid values.
- MUST provide a documented `.env.example` with every variable.

## Dependencies
- MUST pin dependency versions and use a lockfile.
- MUST NOT add a dependency for trivial functionality.
- SHOULD remove unused dependencies in the same change that orphans them.

## State & side effects
- MUST NOT use global mutable state; pass state explicitly or inject it.
- MUST keep functions pure where practical; isolate I/O at the edges.
- MUST make all magic numbers/strings named constants.

## Comments
- SHOULD comment *why*, not *what*.
- MUST NOT leave commented-out code in commits.
