"""The FlowAgent graph — a minimal supervisor / tool-execution loop in LangGraph.

This is intentionally small and representative rather than complete. It is the
surface the take-home traces were generated from, and the same code is used in
the live code-dive. The supervisor delegates the *decision* to a ``ModelClient``
so the graph runs fully offline with the scripted ``MockModelClient``.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .model import Decision, ModelClient
from .tools import TOOLS, ToolError


class AgentState(TypedDict, total=False):
    query: str
    # Full trajectory: an ordered list of {"type": "model"|"tool", ...} records.
    steps: Annotated[list[dict[str, Any]], operator.add]
    final_answer: str | None
    # Internal scratch: the tool call the supervisor just requested.
    pending_tool: dict[str, Any] | None


def build_agent(model: ModelClient, max_model_steps: int = 12):
    """Compile a FlowAgent graph bound to a given model client."""

    def supervisor(state: AgentState) -> dict[str, Any]:
        decision: Decision = model.decide(state["query"], state.get("steps", []))
        record: dict[str, Any] = {"type": "model", "reasoning": decision.reasoning}
        if decision.tool_call is not None:
            call = {"name": decision.tool_call.name, "args": dict(decision.tool_call.args)}
            record["tool_call"] = call
            return {"steps": [record], "pending_tool": call}
        record["final_answer"] = decision.final_answer
        return {"steps": [record], "final_answer": decision.final_answer, "pending_tool": None}

    def tools(state: AgentState) -> dict[str, Any]:
        call = state.get("pending_tool") or {}
        name, args = call.get("name"), call.get("args", {})
        record: dict[str, Any] = {"type": "tool", "name": name, "args": args}
        fn = TOOLS.get(name)
        if fn is None:
            record["error"] = f"no such tool: {name}"
        else:
            try:
                record["output"] = fn(**args)
            except ToolError as exc:
                record["error"] = str(exc)
            except TypeError as exc:
                record["error"] = f"bad arguments for {name}: {exc}"
        return {"steps": [record], "pending_tool": None}

    def route(state: AgentState) -> str:
        if state.get("final_answer") is not None:
            return END
        model_steps = sum(1 for s in state.get("steps", []) if s.get("type") == "model")
        if model_steps >= max_model_steps:
            return END
        return "tools"

    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("tools", tools)
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", route, {"tools": "tools", END: END})
    graph.add_edge("tools", "supervisor")
    return graph.compile()
