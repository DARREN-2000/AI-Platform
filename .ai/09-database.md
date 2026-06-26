# 09 — Database

## Access
- MUST access the DB through a typed layer (ORM/query builder); MUST NOT build SQL via string concatenation.
- MUST use parameterized queries always.
- MUST use connection pooling with bounded size and timeouts.
- SHOULD keep transactions short; MUST make multi-step writes atomic.

## Schema & migrations
- MUST manage schema with versioned migrations (e.g. Alembic); MUST NOT mutate schema manually.
- MUST make migrations reversible or document why not.
- MUST add indexes for all frequent query predicates and foreign keys.
- SHOULD design migrations to be backward-compatible for zero-downtime deploys.

## Data integrity
- MUST enforce constraints (NOT NULL, unique, FK) in the schema, not only in app code.
- MUST handle N+1 queries (eager-load or batch); MUST NOT load unbounded result sets.
- MUST paginate large reads.

## Safety
- MUST NOT log raw query parameters containing secrets/PII.
- MUST set statement timeouts.
- SHOULD separate read/write concerns only when a measured need exists.
- MAY add Redis/cache only per the decision framework, never by default.
