"""GitHub API tool with retry/backoff and webhook signature validation."""
import hashlib
import hmac
from datetime import datetime, timezone

import httpx

from .resilience import with_retry


class GitHubTool:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, repo: str, webhook_secret: str = "", timeout: float = 20.0):
        self.repo = repo
        self.webhook_secret = webhook_secret
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self.headers, timeout=self.timeout)

    # ---- webhook validation ----------------------------------------- #

    def verify_signature(self, payload: bytes, signature_header: str) -> bool:
        if not self.webhook_secret:
            return True
        expected = "sha256=" + hmac.new(
            self.webhook_secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature_header or "")

    # ---- issues ------------------------------------------------------ #

    @with_retry()
    async def list_open_issues(self) -> list[dict]:
        async with self._client() as client:
            resp = await client.get(
                f"{self.BASE_URL}/repos/{self.repo}/issues",
                params={"state": "open", "per_page": 100},
            )
            resp.raise_for_status()
            return [i for i in resp.json() if "pull_request" not in i]

    @with_retry()
    async def add_labels(self, issue_number: int, labels: list[str]) -> dict:
        async with self._client() as client:
            resp = await client.post(
                f"{self.BASE_URL}/repos/{self.repo}/issues/{issue_number}/labels",
                json={"labels": labels},
            )
            resp.raise_for_status()
            return resp.json()

    @with_retry()
    async def add_comment(self, issue_number: int, body: str) -> dict:
        async with self._client() as client:
            resp = await client.post(
                f"{self.BASE_URL}/repos/{self.repo}/issues/{issue_number}/comments",
                json={"body": body},
            )
            resp.raise_for_status()
            return resp.json()

    # ---- pull requests ---------------------------------------------- #

    @with_retry()
    async def list_open_prs(self) -> list[dict]:
        async with self._client() as client:
            resp = await client.get(
                f"{self.BASE_URL}/repos/{self.repo}/pulls",
                params={"state": "open", "per_page": 100},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_stale_prs(self, threshold_days: int = 7) -> list[dict]:
        prs = await self.list_open_prs()
        now = datetime.now(timezone.utc)
        stale = []
        for pr in prs:
            updated = datetime.fromisoformat(pr["updated_at"].replace("Z", "+00:00"))
            age = (now - updated).days
            if age >= threshold_days:
                pr["stale_days"] = age
                stale.append(pr)
        return stale

    @with_retry()
    async def request_review(self, pr_number: int, reviewers: list[str]) -> dict:
        async with self._client() as client:
            resp = await client.post(
                f"{self.BASE_URL}/repos/{self.repo}/pulls/{pr_number}/requested_reviewers",
                json={"reviewers": reviewers},
            )
            resp.raise_for_status()
            return resp.json()
