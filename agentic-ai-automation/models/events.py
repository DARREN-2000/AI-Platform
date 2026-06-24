"""Typed models for GitHub webhook events and agent results."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class GitHubUser(BaseModel):
    login: str
    html_url: Optional[str] = None


class GitHubIssue(BaseModel):
    number: int
    title: str
    body: Optional[str] = ""
    html_url: str
    state: str = "open"
    user: Optional[GitHubUser] = None
    labels: list[dict] = Field(default_factory=list)
    updated_at: Optional[datetime] = None


class WebhookEvent(BaseModel):
    """Normalised representation of an incoming GitHub webhook."""

    event_type: str
    action: Optional[str] = None
    delivery_id: str
    issue: Optional[GitHubIssue] = None
    pull_request: Optional[GitHubIssue] = None
    repository_full_name: Optional[str] = None

    @property
    def target(self) -> Optional[GitHubIssue]:
        return self.issue or self.pull_request


class AgentRun(BaseModel):
    """Result of an agent run, persisted to the audit log."""

    agent: str
    trigger: str
    summary: str
    success: bool = True
    iterations: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
