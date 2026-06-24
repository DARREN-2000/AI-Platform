"""Scheduler tool — wraps APScheduler for cron-based agent triggers."""
import logging
from typing import Callable, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class SchedulerTool:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def add_interval_job(
        self,
        func: Callable,
        hours: int = 24,
        job_id: str = "",
        kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Schedule an async function to run every `hours` hours."""
        self.scheduler.add_job(
            func,
            trigger=IntervalTrigger(hours=hours),
            id=job_id or func.__name__,
            replace_existing=True,
            kwargs=kwargs or {},
        )
        logger.info(f"Scheduled job '{job_id or func.__name__}' every {hours}h")

    def start(self) -> None:
        self.scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self) -> None:
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
