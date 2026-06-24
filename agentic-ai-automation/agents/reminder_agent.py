"""Reminder Agent — pings contributors on stale PRs and overdue tasks."""
from typing import Any

from tools import GitHubTool, NotionTool

from .base_agent import BaseAgent
from .llm import LLMProvider

REMINDER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_stale_prs",
            "description": "Get pull requests with no activity beyond the stale threshold.",
            "parameters": {
                "type": "object",
                "properties": {"threshold_days": {"type": "integer"}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_comment",
            "description": "Post a reminder comment on a GitHub PR.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_number": {"type": "integer"},
                    "body": {"type": "string"},
                },
                "required": ["issue_number", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_labels",
            "description": "Add labels to a PR (e.g. 'stale').",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_number": {"type": "integer"},
                    "labels": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["issue_number", "labels"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_to_notion",
            "description": "Log a reminder action to the Notion Automation Hub.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "github_url": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["name", "github_url"],
            },
        },
    },
]


class ReminderAgent(BaseAgent):
    def __init__(
        self,
        provider: LLMProvider,
        github: GitHubTool,
        notion: NotionTool,
        stale_days: int = 7,
    ):
        super().__init__(provider=provider, tools=REMINDER_TOOLS)
        self.github = github
        self.notion = notion
        self.stale_days = stale_days

    def system_prompt(self) -> str:
        return (
            "You are a friendly reminder agent for a software team. Your job is to:\n"
            f"1. Find all PRs stale for {self.stale_days}+ days using get_stale_prs.\n"
            "2. For each stale PR: add the 'stale' label and post a kind reminder comment "
            "asking for an update or review.\n"
            "3. Log each reminder to Notion.\n"
            "Keep comments short, friendly, and actionable."
        )

    async def execute_tool(self, name: str, args: dict) -> Any:
        if name == "get_stale_prs":
            return await self.github.get_stale_prs(
                threshold_days=args.get("threshold_days", self.stale_days)
            )
        if name == "add_comment":
            return await self.github.add_comment(**args)
        if name == "add_labels":
            return await self.github.add_labels(**args)
        if name == "log_to_notion":
            return await self.notion.create_automation_entry(
                name=args["name"],
                priority="Low",
                trigger="Schedule",
                github_url=args.get("github_url", ""),
                notes=args.get("notes", ""),
                status="Done",
            )
        raise ValueError(f"Unknown tool: {name}")

    async def run_scheduled(self) -> str:
        return await self.run(
            f"Check for stale PRs (>{self.stale_days} days) and send reminders."
        )
