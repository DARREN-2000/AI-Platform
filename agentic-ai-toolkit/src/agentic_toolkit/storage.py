"""Pluggable persistence: an in-memory default plus a PostgreSQL adapter.

The point is the *seam*: storage sits behind a small ``KeyValueStore`` protocol,
so moving from in-memory (tests / offline) to PostgreSQL (production) is a config
change, not a rewrite. The Postgres adapter lazy-imports ``psycopg`` so the
package stays import-safe and offline-testable without the driver installed, and
accepts an injectable ``connect`` callable so the SQL paths are unit-testable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class KeyValueStore(Protocol):
    def get(self, key: str) -> Optional[str]: ...
    def set(self, key: str, value: str) -> None: ...
    def delete(self, key: str) -> None: ...
    def exists(self, key: str) -> bool: ...


@dataclass
class InMemoryStore:
    """Process-local store. Great for tests, demos, and single-process runs."""

    _data: Dict[str, str] = field(default_factory=dict)

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def exists(self, key: str) -> bool:
        return key in self._data

    def keys(self) -> List[str]:
        return list(self._data)


class PostgresStore:
    """PostgreSQL-backed key/value store.

    Requires ``psycopg`` in production (``pip install 'psycopg[binary]'``). For
    tests, pass a ``connect`` callable returning a DB-API-ish connection so no
    real database is needed.
    """

    def __init__(
        self,
        dsn: str,
        *,
        table: str = "kv_store",
        connect: Optional[Callable[[str], object]] = None,
    ) -> None:
        self.dsn = dsn
        self.table = table
        self._connect = connect
        self._conn: object = None

    # -- connection management -------------------------------------------------
    def _new_connection(self) -> object:
        if self._connect is not None:
            return self._connect(self.dsn)
        try:
            import psycopg  # type: ignore
        except ImportError as exc:  # pragma: no cover - exercised only w/o driver
            raise RuntimeError(
                "PostgresStore requires psycopg: pip install 'psycopg[binary]'"
            ) from exc
        return psycopg.connect(self.dsn)

    def _connection(self) -> object:
        if self._conn is None:
            self._conn = self._new_connection()
            self._execute(
                f"CREATE TABLE IF NOT EXISTS {self.table} "
                "(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
        return self._conn

    def _execute(self, sql: str, params: tuple = ()):
        conn = self._conn if self._conn is not None else self._new_connection()
        if self._conn is None:
            self._conn = conn
        with conn.cursor() as cur:  # type: ignore[attr-defined]
            cur.execute(sql, params)
            row = None
            if sql.lstrip().upper().startswith("SELECT"):
                row = cur.fetchone()
        conn.commit()  # type: ignore[attr-defined]
        return row

    # -- KeyValueStore protocol ------------------------------------------------
    def set(self, key: str, value: str) -> None:
        self._connection()
        self._execute(
            f"INSERT INTO {self.table} (key, value) VALUES (%s, %s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            (key, value),
        )

    def get(self, key: str) -> Optional[str]:
        self._connection()
        row = self._execute(
            f"SELECT value FROM {self.table} WHERE key = %s", (key,)
        )
        return row[0] if row else None

    def exists(self, key: str) -> bool:
        self._connection()
        row = self._execute(
            f"SELECT 1 FROM {self.table} WHERE key = %s", (key,)
        )
        return row is not None

    def delete(self, key: str) -> None:
        self._connection()
        self._execute(f"DELETE FROM {self.table} WHERE key = %s", (key,))

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()  # type: ignore[attr-defined]
            self._conn = None


def make_store(dsn: Optional[str] = None) -> KeyValueStore:
    """Return a PostgresStore when a DSN is given, else an InMemoryStore.

    Lets call sites do ``make_store(os.getenv("DATABASE_URL"))`` and get the
    right backend with zero conditional logic.
    """
    if dsn:
        return PostgresStore(dsn)
    return InMemoryStore()
