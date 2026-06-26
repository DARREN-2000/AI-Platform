# 05 — FastAPI

## Structure
- MUST keep route handlers thin: validate, call a service, map the result. No business logic in handlers.
- MUST define request/response models with `pydantic`; MUST NOT return raw dicts or ORM objects.
- MUST use `APIRouter` per resource and a single app factory.
- MUST use dependency injection (`Depends`) for db sessions, auth, and clients.

## Async & lifecycle
- MUST use async handlers and async clients for I/O; MUST NOT block the event loop.
- MUST manage startup/shutdown with the lifespan context; MUST close pools/clients on shutdown.

## Contracts & errors
- MUST version the public API (e.g. `/v1`).
- MUST return a consistent error envelope; MUST map domain errors to correct status codes.
- MUST NOT leak stack traces or internal messages to clients.
- SHOULD set explicit response models and status codes per route.

## Validation & security
- MUST validate and constrain all inputs (types, lengths, ranges).
- MUST enforce auth/authorization in dependencies, not inside handlers.
- MUST set request size limits and timeouts.
- SHOULD add CORS explicitly; MUST NOT use a wildcard origin with credentials.

## Ops
- MUST expose `/health` (liveness) and `/ready` (readiness) endpoints.
- MUST emit structured logs with a request id middleware.
- SHOULD paginate list endpoints by default.
