"""Minimal nested-span tracer with Langfuse / LangSmith export.

Observability is a first-class requirement for agents. This gives you spans,
nesting, and a JSON tree, plus pure converters to Langfuse and LangSmith shapes
so you can ship traces to your platform without changing any call sites.
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Dict, List, Optional


@dataclass
class Span:
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List["Span"] = field(default_factory=list)
    start: float = 0.0
    end: float = 0.0

    @property
    def duration_ms(self) -> float:
        return (self.end - self.start) * 1000.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "attributes": self.attributes,
            "duration_ms": round(self.duration_ms, 3),
            "children": [c.to_dict() for c in self.children],
        }


class Tracer:
    def __init__(self) -> None:
        self.roots: List[Span] = []
        self._stack: List[Span] = []

    @contextmanager
    def span(self, name: str, attributes: Optional[dict] = None):
        s = Span(name=name, attributes=dict(attributes or {}), start=time.perf_counter())
        if self._stack:
            self._stack[-1].children.append(s)
        else:
            self.roots.append(s)
        self._stack.append(s)
        try:
            yield s
        finally:
            s.end = time.perf_counter()
            self._stack.pop()

    def export(self) -> dict:
        if len(self.roots) == 1:
            return self.roots[0].to_dict()
        return {
            "name": "trace",
            "attributes": {},
            "duration_ms": 0.0,
            "children": [r.to_dict() for r in self.roots],
        }


def traced(tracer: Tracer, name: Optional[str] = None):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **k):
            with tracer.span(name or fn.__name__):
                return fn(*a, **k)

        return wrapper

    return deco


def to_langsmith(trace: dict) -> dict:
    """Convert an exported trace into a LangSmith-style nested run tree.

    Pass the result to ``langsmith.Client().create_run(**...)`` (or post it) in
    production; offline it is a plain, inspectable dict.
    """

    def conv(node: dict) -> dict:
        return {
            "name": node["name"],
            "run_type": "chain",
            "extra": {"metadata": node.get("attributes", {})},
            "latency_ms": node.get("duration_ms", 0.0),
            "child_runs": [conv(c) for c in node.get("children", [])],
        }

    return conv(trace)


def to_langfuse(trace: dict) -> dict:
    """Convert an exported trace into a Langfuse-style payload: one trace with a
    flat list of observations linked by ``parentObservationId``.
    """
    observations: List[dict] = []
    counter = {"n": 0}

    def walk(node: dict, parent_id: Optional[str]) -> None:
        counter["n"] += 1
        obs_id = f"obs-{counter['n']}"
        observations.append(
            {
                "id": obs_id,
                "type": "SPAN",
                "name": node["name"],
                "parentObservationId": parent_id,
                "metadata": node.get("attributes", {}),
                "latencyMs": node.get("duration_ms", 0.0),
            }
        )
        for child in node.get("children", []):
            walk(child, obs_id)

    walk(trace, None)
    return {"name": trace.get("name", "trace"), "observations": observations}
