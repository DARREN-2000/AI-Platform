"""Model client abstraction for the FlowAgent.

The agent talks to an LLM only through the ``ModelClient`` protocol. This keeps
the graph runnable fully offline: the supplied ``MockModelClient`` replays a
scripted sequence of decisions (used to generate the frozen traces and to run
the graph during the live code-dive), while a real implementation would call an
LLM provider and parse a tool call out of the response.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass(frozen=True)
class Decision:
    """One step of the supervisor's reasoning.

    Exactly one of ``tool_call`` / ``final_answer`` is expected to be set:
    a tool call continues the loop, a final answer ends it.
    """

    reasoning: str
    tool_call: ToolCall | None = None
    final_answer: str | None = None


class ModelClient(Protocol):
    def decide(self, query: str, trajectory: list[dict[str, Any]]) -> Decision:
        """Return the next decision given the query and the steps so far."""
        ...


class MockModelClient:
    """Deterministic, scripted model client.

    ``script`` is the ordered list of decisions the "model" emits. This lets us
    reproduce healthy *and* faulty agent behaviours with zero API calls and full
    reproducibility. If the script runs out, the agent finishes defensively.
    """

    def __init__(self, script: list[Decision]) -> None:
        self._script = script
        self._i = 0

    def decide(self, query: str, trajectory: list[dict[str, Any]]) -> Decision:
        if self._i >= len(self._script):
            return Decision(reasoning="(script exhausted)", final_answer="(no answer)")
        decision = self._script[self._i]
        self._i += 1
        return decision
