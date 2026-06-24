"""Shared pytest fixtures."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.llm import LLMProvider, LLMResponse


class FakeProvider(LLMProvider):
    """A scripted LLM provider that returns queued responses in order."""

    def __init__(self, responses: list[LLMResponse]):
        self._responses = list(responses)

    async def complete(self, messages, tools) -> LLMResponse:
        return self._responses.pop(0) if self._responses else LLMResponse(content="done")


@pytest.fixture
def fake_provider():
    return FakeProvider([LLMResponse(content="All triaged.")])


@pytest.fixture
def mock_github():
    gh = MagicMock()
    gh.list_open_issues = AsyncMock(return_value=[
        {"number": 1, "title": "Crash on login", "body": "It crashes.",
         "html_url": "https://github.com/org/repo/issues/1"},
    ])
    gh.add_labels = AsyncMock(return_value={"labels": ["bug"]})
    gh.add_comment = AsyncMock(return_value={"id": 1})
    gh.get_stale_prs = AsyncMock(return_value=[
        {"number": 10, "title": "Refactor", "html_url": "https://github.com/org/repo/pull/10",
         "stale_days": 9},
    ])
    return gh


@pytest.fixture
def mock_notion():
    notion = MagicMock()
    notion.create_automation_entry = AsyncMock(return_value={"id": "abc"})
    return notion
