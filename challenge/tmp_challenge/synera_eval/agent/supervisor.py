"""A supervisor / worker FlowAgent — the multi-agent sibling of ``graph.py``.

Where ``graph.py`` is a single worker looping ``supervisor -> tools -> supervisor``,
this module models the *real* MAS shape: an orchestrating **supervisor** that routes
sub-tasks to specialised **worker** sub-agents, each owning a slice of the tool
surface, then synthesises their results into a final answer. It is the surface the
multi-agent take-home traces are generated from.

Like the single-agent graph, it runs fully offline and deterministically: every agent
(the supervisor and each worker) talks to the LLM only through the ``ModelClient``
protocol, and the scripted ``MockModelClient`` replays a fixed sequence of decisions.
Nothing here imports a real provider, uses the wall clock, or draws randomness.

Two things make the coordination and synthesis behaviour *evaluable* on the resulting
traces:

* **Routing is checkable.** Tool ownership (``OWNED`` / ``OWNER``) is disjoint and
  total — every tool belongs to exactly one worker — so the "right" worker for a
  sub-task is simply ``OWNER[required_tool]``.
* **Handoffs are explicit.** Each delegation emits a ``{"type": "handoff"}`` record
  carrying the ``context`` the supervisor forwarded (on dispatch) and the structured
  ``findings`` the worker produced (on return). A handoff-accuracy or synthesis
  -faithfulness check reads these directly.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .model import Decision, MockModelClient
from .tools import TOOLS, ToolError

# Worker roster and tool ownership. Disjoint + total over the six tools in TOOLS, so
# ``OWNER[tool]`` is the single correct worker for any tool — the basis of a
# deterministic routing-correctness check.
WORKERS: tuple[str, ...] = ("material_worker", "simulation_worker", "report_worker")

OWNED: dict[str, tuple[str, ...]] = {
    "material_worker": ("lookup_material", "unit_convert"),
    "simulation_worker": ("run_simulation", "compute_mass", "compute_safety_factor"),
    "report_worker": ("write_report",),
}

# Reverse index: tool name -> the worker that owns it.
OWNER: dict[str, str] = {tool: worker for worker, tools in OWNED.items() for tool in tools}


class SupervisorState(TypedDict, total=False):
    query: str
    # Full trajectory: an ordered list of {"type": "model"|"tool"|"handoff", ...} records,
    # each tagged with the ``agent`` that produced it ("supervisor" or a worker name).
    steps: Annotated[list[dict[str, Any]], operator.add]
    final_answer: str | None
    # Internal scratch: the dispatch the supervisor just requested.
    pending_dispatch: dict[str, Any] | None
    # Structured worker returns, in order — the material the supervisor synthesises over.
    worker_results: Annotated[list[dict[str, Any]], operator.add]


def _make_worker(name: str, owned: tuple[str, ...], model: MockModelClient):
    """Build a worker node bound to its own scripted model and owned tool set.

    A worker drains its own decisions to a ``final_answer`` within a single node visit:
    it requests tools (executing only those it owns), then hands a structured result
    back to the supervisor. Calling a tool it does not own is recorded as an ``error``
    step — the multi-agent analogue of a routing fault.
    """

    def worker(state: SupervisorState) -> dict[str, Any]:
        out: list[dict[str, Any]] = []
        while True:
            decision: Decision = model.decide(state["query"], state.get("steps", []))
            record: dict[str, Any] = {"type": "model", "agent": name, "reasoning": decision.reasoning}
            if decision.final_answer is None and decision.tool_call is not None:
                call = {"name": decision.tool_call.name, "args": dict(decision.tool_call.args)}
                record["tool_call"] = call
                out.append(record)
                tool_step: dict[str, Any] = {"type": "tool", "agent": name, "name": call["name"], "args": call["args"]}
                fn = TOOLS.get(call["name"])
                if call["name"] not in owned:
                    tool_step["error"] = f"{name} is not authorised to call {call['name']}"
                elif fn is None:
                    tool_step["error"] = f"no such tool: {call['name']}"
                else:
                    try:
                        tool_step["output"] = fn(**call["args"])
                    except ToolError as exc:
                        tool_step["error"] = str(exc)
                    except TypeError as exc:
                        tool_step["error"] = f"bad arguments for {call['name']}: {exc}"
                out.append(tool_step)
                continue
            # No tool call -> the worker is reporting back.
            record["final_answer"] = decision.final_answer
            out.append(record)
            findings = [{"tool": s["name"], "output": s["output"]} for s in out if s["type"] == "tool" and "output" in s]
            out.append({
                "type": "handoff", "direction": "return", "from": name, "to": "supervisor",
                "result": decision.final_answer, "findings": findings,
            })
            return {
                "steps": out,
                "worker_results": [{"worker": name, "result": decision.final_answer, "findings": findings}],
                "pending_dispatch": None,
            }

    return worker


def build_supervisor_agent(scripts: dict[str, list[Decision]], max_turns: int = 8):
    """Compile a supervisor/worker FlowAgent bound to per-agent scripted models.

    ``scripts`` maps each agent name ("supervisor" and each worker) to the ordered list
    of decisions it emits. Each agent gets its own ``MockModelClient`` so their scripts
    advance independently — the interleaving of nodes cannot perturb any single agent's
    sequence, which keeps the whole run deterministic.

    The supervisor delegates by emitting a ``ToolCall("dispatch", {"worker", "subtask",
    "context"})`` (``dispatch`` is not a real tool, so it never reaches ``tools.py``); a
    plain ``final_answer`` ends the run. ``max_turns`` caps the number of dispatches.
    """

    sup_model = MockModelClient(scripts.get("supervisor", []))
    worker_models = {w: MockModelClient(scripts.get(w, [])) for w in WORKERS}

    def supervisor(state: SupervisorState) -> dict[str, Any]:
        decision: Decision = sup_model.decide(state["query"], state.get("steps", []))
        record: dict[str, Any] = {"type": "model", "agent": "supervisor", "reasoning": decision.reasoning}
        call = decision.tool_call
        if call is not None and call.name == "dispatch" and decision.final_answer is None:
            worker = call.args.get("worker")
            subtask = call.args.get("subtask", "")
            context = dict(call.args.get("context", {}))
            record["dispatch"] = {"worker": worker, "subtask": subtask}
            handoff = {
                "type": "handoff", "direction": "dispatch", "from": "supervisor",
                "to": worker, "subtask": subtask, "context": context,
            }
            return {"steps": [record, handoff], "pending_dispatch": {"worker": worker, "subtask": subtask, "context": context}}
        record["final_answer"] = decision.final_answer
        return {"steps": [record], "final_answer": decision.final_answer, "pending_dispatch": None}

    def route(state: SupervisorState) -> str:
        if state.get("final_answer") is not None:
            return END
        pending = state.get("pending_dispatch")
        if not pending:
            return END
        dispatches = sum(
            1 for s in state.get("steps", [])
            if s.get("type") == "handoff" and s.get("direction") == "dispatch"
        )
        if dispatches > max_turns:
            return END
        worker = pending["worker"]
        return worker if worker in WORKERS else END

    graph = StateGraph(SupervisorState)
    graph.add_node("supervisor", supervisor)
    for w in WORKERS:
        graph.add_node(w, _make_worker(w, OWNED[w], worker_models[w]))
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", route, {**{w: w for w in WORKERS}, END: END})
    for w in WORKERS:
        graph.add_edge(w, "supervisor")
    return graph.compile()
