"""Tests for the SQLite store (idempotency + audit log)."""
import pytest

from store import Store


@pytest.fixture
async def store(tmp_path):
    s = Store(str(tmp_path / "test.db"))
    await s.init()
    return s


async def test_idempotency(store):
    assert await store.is_processed("d1") is False
    await store.mark_processed("d1", "issues")
    assert await store.is_processed("d1") is True


async def test_record_and_recent_runs(store):
    await store.record_run("TriageAgent", "GitHub", "did a thing", iterations=3)
    runs = await store.recent_runs()
    assert len(runs) == 1
    assert runs[0]["agent"] == "TriageAgent"
    assert runs[0]["iterations"] == 3


async def test_stats(store):
    await store.record_run("TriageAgent", "GitHub", "a")
    await store.record_run("ReminderAgent", "Schedule", "b", success=False)
    stats = await store.stats()
    assert stats["total_runs"] == 2
    assert len(stats["by_agent"]) == 2
