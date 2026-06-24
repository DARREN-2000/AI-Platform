"""Triage Agent — labels and prioritises GitHub issues and PRs."""
from typing import Any

from tools import GitHubTool, NotionTool

from .base_agent import BaseAgent
from .llm import LLMProvider

TRIAGE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_open_issues",
            "description": "List open GitHub issues in the repository.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_labels",
            "description": "Add labels to a GitHub issue or PR.",
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
            "name": "add_comment",
            "description": "Post a comment on a GitHub issue or PR.",
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
            "name": "log_to_notion",
            "description": "Log a triage action to the Notion Automation Hub.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "priority": {"type": "string", "enum": ["Low", "Medium", "High"]},
                    "github_url": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["name", "priority", "github_url"],
            },
        },
    },
]


class TriageAgent(BaseAgent):
    def __init__(self, provider: LLMProvider, github: GitHubTool, notion: NotionTool):
        super().__init__(provider=provider, tools=TRIAGE_TOOLS)
        self.github = github
        self.notion = notion

    def system_prompt(self) -> str:
        return (
            "You are an expert GitHub triage agent. Your job is to:\n"
            "1. List all open issues (or triage the specific issue provided).\n"
            "2. Decide appropriate labels (bug, enhancement, documentation, "
            "good first issue, help wanted, question) and a priority (Low/Medium/High).\n"
            "3. Apply labels using add_labels.\n"
            "4. Post a brief, friendly triage comment.\n"
            "5. Log each triage action to Notion using log_to_notion.\n"
            "Be concise and systematic."
        )

    async def execute_tool(self, name: str, args: dict) -> Any:
        if name == "list_open_issues":
            return await self.github.list_open_issues()
        if name == "add_labels":
            return await self.github.add_labels(**args)
        if name == "add_comment":
            return await self.github.add_comment(**args)
        if name == "log_to_notion":
            return await self.notion.create_automation_entry(
                name=args["name"],
                priority=args.get("priority", "Medium"),
                trigger="GitHub",
                github_url=args.get("github_url", ""),
                notes=args.get("notes", ""),
                status="In progress",
            )
        raise ValueError(f"Unknown tool: {name}")

    async def triage_issue(self, number: int, title: str, body: str, url: str) -> str:
        prompt = (
            f"Triage this GitHub issue:\n#{number}: {title}\n\n{body}\n\n"
            f"URL: {url}\nApply labels, post a triage comment, and log it to Notion."
        )
        return await self.run(prompt)
