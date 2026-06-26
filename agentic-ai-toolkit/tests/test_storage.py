import pytest

from agentic_toolkit.storage import (
    InMemoryStore,
    KeyValueStore,
    PostgresStore,
    make_store,
)


class _FakeCursor:
    def __init__(self, table: dict):
        self._table = table
        self._result = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql: str, params=()):
        head = sql.strip().upper()
        self._result = None
        if head.startswith("CREATE TABLE"):
            return
        if head.startswith("INSERT"):
            key, value = params
            self._table[key] = value
        elif head.startswith("SELECT VALUE"):
            (key,) = params
            self._result = (self._table[key],) if key in self._table else None
        elif head.startswith("SELECT 1"):
            (key,) = params
            self._result = (1,) if key in self._table else None
        elif head.startswith("DELETE"):
            (key,) = params
            self._table.pop(key, None)

    def fetchone(self):
        return self._result


class _FakeConn:
    def __init__(self):
        self.table: dict = {}
        self.commits = 0

    def cursor(self):
        return _FakeCursor(self.table)

    def commit(self):
        self.commits += 1

    def close(self):
        pass


def test_in_memory_roundtrip():
    s = InMemoryStore()
    assert isinstance(s, KeyValueStore)
    assert s.get("a") is None
    s.set("a", "1")
    assert s.get("a") == "1" and s.exists("a")
    s.set("a", "2")  # upsert
    assert s.get("a") == "2"
    s.delete("a")
    assert not s.exists("a")


def test_make_store_selects_backend():
    assert isinstance(make_store(None), InMemoryStore)
    assert isinstance(make_store("postgresql://x"), PostgresStore)


def test_postgres_store_with_injected_connection():
    conn = _FakeConn()
    store = PostgresStore("postgresql://fake", connect=lambda dsn: conn)
    assert store.get("missing") is None
    store.set("k", "v")
    assert store.get("k") == "v"
    assert store.exists("k") is True
    store.set("k", "v2")  # upsert path
    assert store.get("k") == "v2"
    store.delete("k")
    assert store.exists("k") is False
    assert conn.commits > 0


def test_postgres_store_without_driver_raises():
    # No injected connection and psycopg is not installed in this env.
    store = PostgresStore("postgresql://nope")
    with pytest.raises(Exception):
        store.set("a", "b")
