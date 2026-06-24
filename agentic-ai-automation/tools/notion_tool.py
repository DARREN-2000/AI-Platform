"""Notion API tool with retry/backoff for syncing automation state."""
from typing import Any

import httpx

from .resilience import with_retry


class NotionTool:
    BASE_URL = "https://api.notion.com/v1"

    def __init__(self, token: str, database_id: str, timeout: float = 20.0):
        self.database_id = database_id
        self.enabled = bool(token and database_id)
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self.headers, timeout=self.timeout)

    @with_retry()
    async def create_automation_entry(
        self,
        name: str,
        status: str = "Inbox",
        priority: str = "Medium",
        trigger: str = "GitHub",
        github_url: str = "",
        notes: str = "",
    ) -> dict:
        """Create a new row in the Automation Hub database (no-op if Notion disabled)."""
        if not self.enabled:
            return {"skipped": "notion_disabled"}

        payload: dict[str, Any] = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Automation": {"title": [{"text": {"content": name}}]},
                "Status": {"status": {"name": status}},
                "Priority": {"select": {"name": priority}},
                "Trigger": {"select": {"name": trigger}},
                "Notes": {"rich_text": [{"text": {"content": notes}}]},
            },
        }
        if github_url:
            payload["properties"]["GitHub URL"] = {"url": github_url}

        async with self._client() as client:
            resp = await client.post(f"{self.BASE_URL}/pages", json=payload)
            resp.raise_for_status()
            return resp.json()

    @with_retry()
    async def update_status(self, page_id: str, status: str) -> dict:
        if not self.enabled:
            return {"skipped": "notion_disabled"}
        async with self._client() as client:
            resp = await client.patch(
                f"{self.BASE_URL}/pages/{page_id}",
                json={"properties": {"Status": {"status": {"name": status}}}},
            )
            resp.raise_for_status()
            return resp.json()

    @with_retry()
    async def query_by_status(self, status: str) -> list[dict]:
        if not self.enabled:
            return []
        async with self._client() as client:
            resp = await client.post(
                f"{self.BASE_URL}/databases/{self.database_id}/query",
                json={"filter": {"property": "Status", "status": {"equals": status}}},
            )
            resp.raise_for_status()
            return resp.json().get("results", [])
