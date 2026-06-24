"""Tests for TriageAgent."""
import pytest
from unittest.mock import AsyncMock, patch

from agents.llm import LLMResponse, ToolCall
from agents.triage_agent import TriageAgent
from tests.conftest import FakeProvider


@pytest.fixture
def agent(fake_provider, mock_github, mock_notion):
    return TriageAgent(provider=fake_provider, github=mock_github, notion=mock_notion)


async def test_execute_tool_list_issues(agent, mock_github):
    result = await agent.execute_tool("list_open_issues", {})
    assert len(result) == 1
    mock_github.list_open_issues.assert_called_once()


async def test_execute_tool_add_labels(agent, mock_github):
    await agent.execute_tool("add_labels", {"issue_number": 1, "labels": ["bug"]})
    mock_github.add_labels.assert_called_once_with(issue_number=1, labels=["bug"])


async def test_execute_tool_log_to_notion(agent, mock_notion):
    await agent.execute_tool("log_to_notion", {
        "name": "Triage #1", "priority": "High",
        "github_url": "https://github.com/org/repo/issues/1", "notes": "Crash",
    })
    mock_notion.create_automation_entry.assert_called_once()


async def test_execute_tool_unknown_raises(agent):
    with pytest.raises(ValueError, match="Unknown tool"):
        await agent.execute_tool("nope", {})


async def test_run_loop_executes_tool_then_finishes(mock_github, mock_notion):
    """Provider asks for a tool call, then returns a final answer."""
    provider = FakeProvider([
        LLMResponse(tool_calls=[ToolCall(id="t1", name="list_open_issues", arguments={})]),
        LLMResponse(content="Triaged 1 issue."),
    ])
    agent = TriageAgent(provider=provider, github=mock_github, notion=mock_notion)
    result = await agent.run("triage everything")
    assert result == "Triaged 1 issue."
    assert agent.last_iterations == 2
    mock_github.list_open_issues.assert_called_once()


async def test_triage_issue_calls_run(agent):
    with patch.object(agent, "run", new=AsyncMock(return_value="ok")) as mock_run:
        result = await agent.triage_issue(3, "Bug", "broke", "https://x/3")
        assert result == "ok"
        mock_run.assert_called_once()
