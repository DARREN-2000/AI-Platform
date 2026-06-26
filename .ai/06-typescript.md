# 06 — TypeScript

## Baseline
- MUST enable `strict` in `tsconfig`; MUST NOT use `any` (use `unknown` + narrowing).
- MUST lint with ESLint and format with Prettier/Biome; CI MUST fail on violations.
- MUST use ESM modules and a pinned package manager with a lockfile.

## Types
- MUST type all public functions and module boundaries explicitly.
- MUST validate external/runtime data with a schema validator (e.g. `zod`); MUST NOT trust `JSON.parse` shapes.
- SHOULD prefer `type`/discriminated unions over enums for closed sets.
- MUST NOT use non-null assertions (`!`) to bypass the type system.

## Async & errors
- MUST `await` or explicitly handle every promise; MUST NOT leave floating promises.
- MUST handle rejected promises; MUST NOT swallow errors.
- SHOULD use `Result`-style returns or typed errors at boundaries.

## Style
- MUST prefer `const`; MUST NOT use `var`.
- MUST keep modules side-effect-free on import.
- SHOULD keep functions pure and small; isolate I/O.
- MUST NOT introduce default exports for shared modules (prefer named).
