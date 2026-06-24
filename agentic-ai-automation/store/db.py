"""Async SQLite persistence: webhook idempotency + agent audit log."""
import logging
from datetime import datetime, timezone
from typing import Optional

import aiosqlite

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS processed_deliveries (
    delivery_id TEXT PRIMARY KEY,
    event_type  TEXT NOT NULL,
    processed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    agent      TEXT NOT NULL,
    trigger    TEXT NOT NULL,
    summary    TEXT NOT NULL,
    success    INTEGER NOT NULL DEFAULT 1,
    iterations INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
"""


class Store:
    def __init__(self, path: str = "automation.db"):
        self.path = path

    async def init(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.executescript(_SCHEMA)
            await db.commit()
        logger.info("store initialised at %s", self.path)

    # ---- idempotency ------------------------------------------------- #

    async def is_processed(self, delivery_id: str) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT 1 FROM processed_deliveries WHERE delivery_id = ?",
                (delivery_id,),
            )
            return await cur.fetchone() is not None

    async def mark_processed(self, delivery_id: str, event_type: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO processed_deliveries VALUES (?, ?, ?)",
                (delivery_id, event_type, datetime.now(timezone.utc).isoformat()),
            )
            await db.commit()

    # ---- audit log --------------------------------------------------- #

    async def record_run(
        self,
        agent: str,
        trigger: str,
        summary: str,
        success: bool = True,
        iterations: int = 0,
    ) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO agent_runs (agent, trigger, summary, success, iterations, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (agent, trigger, summary, int(success), iterations,
                 datetime.now(timezone.utc).isoformat()),
            )
            await db.commit()

    async def recent_runs(self, limit: int = 50) -> list[dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM agent_runs ORDER BY id DESC LIMIT ?", (limit,)
            )
            return [dict(r) for r in await cur.fetchall()]

    async def stats(self) -> dict:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT agent, COUNT(*) AS runs, SUM(success) AS ok FROM agent_runs GROUP BY agent"
            )
            by_agent = [dict(r) for r in await cur.fetchall()]
            cur = await db.execute("SELECT COUNT(*) AS total FROM agent_runs")
            total = (await cur.fetchone())["total"]
        return {"total_runs": total, "by_agent": by_agent}
