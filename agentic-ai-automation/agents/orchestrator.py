"""Orchestrator — coordinates agents, persistence, and scheduling."""
import logging

from config import settings
from models import WebhookEvent
from store import Store
from tools import GitHubTool, NotionTool, SchedulerTool

from .llm import build_provider
from .reminder_agent import ReminderAgent
from .triage_agent import TriageAgent

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self):
        self.github = GitHubTool(
            token=settings.github_token,
            repo=settings.github_repo,
            webhook_secret=settings.github_webhook_secret,
        )
        self.notion = NotionTool(
            token=settings.notion_token,
            database_id=settings.notion_database_id,
        )
        self.store = Store(settings.db_path)
        self.scheduler = SchedulerTool()

        provider = build_provider(
            settings.llm_provider, settings.active_api_key, settings.llm_model
        )
        self.triage_agent = TriageAgent(provider, self.github, self.notion)
        self.reminder_agent = ReminderAgent(
            provider, self.github, self.notion, stale_days=settings.stale_pr_threshold_days
        )

    async def startup(self) -> None:
        await self.store.init()
        self.scheduler.add_interval_job(
            self._scheduled_reminders,
            hours=settings.reminder_interval_hours,
            job_id="reminder_agent",
        )
        self.scheduler.start()
        logger.info("orchestrator started")

    def shutdown(self) -> None:
        self.scheduler.shutdown()

    # ---- scheduled + manual triggers -------------------------------- #

    async def _scheduled_reminders(self) -> str:
        summary = await self.reminder_agent.run_scheduled()
        await self.store.record_run(
            "ReminderAgent", "Schedule", summary,
            iterations=self.reminder_agent.last_iterations,
        )
        return summary

    async def run_full_triage(self) -> str:
        summary = await self.triage_agent.run(
            "Triage all open issues: label them, comment, and log to Notion."
        )
        await self.store.record_run(
            "TriageAgent", "Manual", summary, iterations=self.triage_agent.last_iterations
        )
        return summary

    async def run_reminders(self) -> str:
        return await self._scheduled_reminders()

    # ---- webhook routing with idempotency --------------------------- #

    async def handle_webhook(self, event: WebhookEvent) -> str:
        if await self.store.is_processed(event.delivery_id):
            logger.info("duplicate delivery skipped: %s", event.delivery_id)
            return "duplicate_skipped"

        result = "ignored"
        if event.event_type in ("issues", "pull_request") and event.action == "opened":
            target = event.target
            if target:
                result = await self.triage_agent.triage_issue(
                    number=target.number,
                    title=target.title,
                    body=target.body or "",
                    url=target.html_url,
                )
                await self.store.record_run(
                    "TriageAgent", "GitHub", result,
                    iterations=self.triage_agent.last_iterations,
                )

        await self.store.mark_processed(event.delivery_id, event.event_type)
        return result
