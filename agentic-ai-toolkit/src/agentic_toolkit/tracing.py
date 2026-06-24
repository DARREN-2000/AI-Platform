"""Minimal nested-span tracer with a Langfuse-shaped export.

Observability is a first-class requirement for agents. This gives you spans,
nesting, and a JSON tree you can ship to Langfuse/LangSmith by swapping
`export()` - without changing any call sites.
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
