"""Versioned prompt templates.

Treat prompts as managed artifacts (named + versioned) instead of inline
strings, so you can A/B them and record which version produced a result - the
seam where a prompt registry (Langfuse, PromptLayer) plugs in. Pure-Python and
offline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

_VAR_RE = re.compile(r"{(\w+)}")


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    template: str
    version: int = 1

    def variables(self) -> List[str]:
        return sorted(set(_VAR_RE.findall(self.template)))

    def render(self, **values: object) -> str:
        missing = [v for v in self.variables() if v not in values]
        if missing:
            raise KeyError(f"missing template variables: {missing}")
        out = self.template
        for key, value in values.items():
            out = out.replace("{" + key + "}", str(value))
        return out


class PromptLibrary:
    """An in-memory registry of named, versioned templates."""

    def __init__(self) -> None:
        self._templates: Dict[Tuple[str, int], PromptTemplate] = {}
        self._latest: Dict[str, int] = {}

    def register(self, template: PromptTemplate) -> "PromptLibrary":
        self._templates[(template.name, template.version)] = template
        self._latest[template.name] = max(
            self._latest.get(template.name, 0), template.version
        )
        return self

    def get(self, name: str, version: Optional[int] = None) -> PromptTemplate:
        if name not in self._latest:
            raise KeyError(f"unknown prompt: {name}")
        v = version if version is not None else self._latest[name]
        return self._templates[(name, v)]

    def render(self, name: str, version: Optional[int] = None, **values: object) -> str:
        return self.get(name, version).render(**values)

    def versions(self, name: str) -> List[int]:
        return sorted(v for (n, v) in self._templates if n == name)
