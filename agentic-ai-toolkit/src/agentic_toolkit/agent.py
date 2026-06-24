"""A minimal LangGraph-style agent: an explicit state graph + a ReAct loop.

Control flow lives in a `Graph` of nodes and (conditional) edges instead of a
hidden while-loop, which is exactly how LangGraph models agents - and it makes
the agent unit-testable. The agent records a trajectory so you can evaluate the
*path* (tool choice/order), not just the final answer.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .providers import Message, Provider
from .tools import ToolRegistry, default_registry
from .tracing import Tracer

END = "__end__"


class Graph:
    """Tiny state machine: nodes mutate state; static or conditional edges pick
    the next node. Return `END` from a router to stop."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Callable[[Any], Any]] = {}
        self.edges: Dict[str, str] = {}
        self.cond: Dict[str, Callable[[Any], str]] = {}
        self.entry: Optional[str] = None

    def add_node(self, name: str, fn: Callable[[Any], Any]) -> "Graph":
        self.nodes[name] = fn
        return self

    def set_entry(self, name: str) -> "Graph":
        self.entry = name
        return self

    def add_edge(self, src: str, dst: str) -> "Graph":
        self.edges[src] = dst
        return self

    def add_conditional_edges(self, src: str, router: Callable[[Any], str]) -> "Graph":
        self.cond[src] = router
        return self

    def run(self, state: Any, *, max_steps: int = 50) -> Any:
        if self.entry is None:
            raise ValueError("no entry node set")
        node = self.entry
        n = 0
        while node != END and n < max_steps:
            state = self.nodes[node](state)
            router = self.cond.get(node)
            if router is not None:
                node = router(state)
            elif node in self.edges:
                node = self.edges[node]
            else:
                node = END
            n += 1
        return state


@dataclass
class TrajectoryStep:
    tool: str
    args: Dict[str, Any]
    observation: str


@dataclass
class AgentState:
    messages: List[Message]
    trajectory: List[TrajectoryStep] = field(default_factory=list)
    pending: Optional[Tuple[str, dict]] = None
    answer: Optional[str] = None
    finished: bool = False
    steps: int = 0
    max_steps: int = 6


def parse_action(text: str) -> Tuple[str, str, Optional[dict]]:
    """Parse 'ACTION: <tool> <json-args>' or 'FINAL: <text>'.
    Unrecognized output is treated as a final answer (graceful degradation)."""
    t = text.strip()
    if t.startswith("FINAL:"):
        return ("final", t[len("FINAL:"):].strip(), None)
    if t.startswith("ACTION:"):
        body = t[len("ACTION:"):].strip()
        tool, _, rest = body.partition(" ")
        try:
            args = json.loads(rest) if rest.strip() else {}
        except json.JSONDecodeError:
            args = {"_raw": rest}
        return ("action", tool, args)
    return ("final", t, None)


@dataclass
class ReActAgent:
    provider: Provider
    registry: ToolRegistry = field(default_factory=default_registry)
    tracer: Optional[Tracer] = None
    max_steps: int = 6

    def _model(self, state: AgentState) -> AgentState:
        if state.steps >= state.max_steps:
            state.finished = True
            state.answer = state.answer or "Stopped: step budget exhausted."
            return state
        state.steps += 1
        out = self.provider.complete(state.messages)
        state.messages = state.messages + [Message("assistant", out)]
        kind, a, b = parse_action(out)
        if kind == "final":
            state.answer = a
            state.finished = True
            state.pending = None
        else:
            state.pending = (a, b or {})
        return state

    def _tools(self, state: AgentState) -> AgentState:
        assert state.pending is not None
        tool, args = state.pending
        try:
            obs = self.registry.run(tool, args)
        except Exception as exc:  # tool errors become observations, not crashes
            obs = f"ERROR: {exc}"
        state.trajectory.append(TrajectoryStep(tool=tool, args=args, observation=obs))
        state.messages = state.messages + [Message("tool", obs)]
        state.pending = None
        return state

    def build_graph(self) -> Graph:
        g = Graph()
        g.add_node("model", self._model)
        g.add_node("tools", self._tools)
        g.set_entry("model")
        g.add_conditional_edges("model", lambda s: END if s.finished else "tools")
        g.add_edge("tools", "model")
        return g

    def run(self, question: str, *, system: str = "") -> AgentState:
        msgs: List[Message] = []
        if system:
            msgs.append(Message("system", system))
        msgs.append(Message("user", question))
        state = AgentState(messages=msgs, max_steps=self.max_steps)
        graph = self.build_graph()
        guard = self.max_steps * 2 + 2
        if self.tracer is not None:
            with self.tracer.span("agent.run", {"question": question}):
                return graph.run(state, max_steps=guard)
        return graph.run(state, max_steps=guard)


def evaluate_trajectory(trajectory: List[TrajectoryStep], expected_tools: List[str]) -> dict:
    """Bridge to the eval kit: score the path, not just the answer. Reports the
    tools used, set-coverage of expected tools, and exact-order match."""
    used = [s.tool for s in trajectory]
    expected_set = set(expected_tools)
    coverage = (
        sum(1 for t in expected_set if t in used) / len(expected_set)
        if expected_set
        else 1.0
    )
    ordered_match = used[: len(expected_tools)] == list(expected_tools)
    return {"tools_used": used, "coverage": coverage, "ordered_match": ordered_match}
