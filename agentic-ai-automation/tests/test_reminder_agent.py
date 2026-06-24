"""Tests for ReminderAgent."""
import pytest
from unittest.mock import AsyncMock, patch

from agents.reminder_agent import ReminderAgent


@pytest.fixture
def agent(fake_provider, mock_github, mock_notion):
    return ReminderAgent(
        provider=fake_provider, github=mock_github, notion=mock_notion, stale_days=7
    )


async def test_get_stale_prs(agent, mock_github):
    result = await agent.execute_tool("get_stale_prs", {"threshold_days": 7})
    assert result[0]["stale_days"] == 9
    mock_github.get_stale_prs.assert_called_once_with(threshold_days=7)


async def test_add_stale_label(agent, mock_github):
    await agent.execute_tool("add_labels", {"issue_number": 10, "labels": ["stale"]})
    mock_github.add_labels.assert_called_once_with(issue_number=10, labels=["stale"])


async def test_run_scheduled_calls_run(agent):
    with patch.object(agent, "run", new=AsyncMock(return_value="Reminded!")) as mock_run:
        result = await agent.run_scheduled()
        assert result == "Reminded!"
        mock_run.assert_called_once()


async def test_execute_tool_unknown_raises(agent):
    with pytest.raises(ValueError):
        await agent.execute_tool("bad", {})
