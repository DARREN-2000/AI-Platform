"""Tool abstraction + a safe calculator and a tiny lookup tool.

Tools are the agent's hands. The registry pattern keeps tool definitions data,
not code branches, so adding a tool is a one-liner and the agent prompt can be
generated from `specs()`.
"""
from __future__ import annotations

import ast
import operator
from dataclasses import dataclass
from typing import Callable, Dict, List

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_arith(expr: str) -> float:
    """Evaluate arithmetic without `eval`: walk a parsed AST allowing only
    numbers and the operators in `_OPS`. No names, calls, or attributes."""

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.operand))
        raise ValueError(f"unsupported expression node: {type(node).__name__}")

    return _eval(ast.parse(expr, mode="eval"))


@dataclass
class Tool:
    name: str
    description: str
    func: Callable[[dict], str]

    def run(self, args: dict) -> str:
        return self.func(args)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> "ToolRegistry":
        self._tools[tool.name] = tool
        return self

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name}")
        return self._tools[name]

    def run(self, name: str, args: dict) -> str:
        return self.get(name).run(args)

    def specs(self) -> List[dict]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    def __contains__(self, name: str) -> bool:
        return name in self._tools


def default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(
        Tool(
            "calculator",
            "Evaluate an arithmetic expression. args: {expression: str}",
            lambda a: str(safe_arith(str(a["expression"]))),
        )
    )
    kb = {
        "france": "Paris is the capital of France.",
        "germany": "Berlin is the capital of Germany.",
    }
    reg.register(
        Tool(
            "lookup",
            "Look up a fact by keyword. args: {key: str}",
            lambda a: kb.get(str(a.get("key", "")).lower(), "No entry found."),
        )
    )
    return reg
