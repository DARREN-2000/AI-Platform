"""Plan-and-execute agent: plan first, then solve each sub-step.

Where ReActAgent interleaves thought and action, this agent first decomposes a
task into an explicit, inspectable plan, then executes each step with a ReAct
sub-agent, threading results forward as context. Planning up front is stronger
for multi-part tasks and lets you grade the plan before any tool runs.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from .agent import ReActAgent
from .providers import Message, Provider
from .tools import ToolRegistry, default_registry

_STEP_RE = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+(.*\S)\s*$")

PLANNER_SYSTEM = (
    "You are a planner. Break the user's task into a short numbered list of "
    "concrete, ordered sub-steps. Output ONLY the list, one step per line."
)


def parse_plan(text: str) -> List[str]:
    steps: List[str] = []
    for line in text.splitlines():
        m = _STEP_RE.match(line)
        if m:
            steps.append(m.group(1).strip())
    return steps


@dataclass
class PlanStep:
    description: str
    result: str = ""


@dataclass
class PlanAndExecuteResult:
    plan: List[str]
    steps: List[PlanStep]
    answer: str


@dataclass
class PlanAndExecuteAgent:
    provider: Provider
    registry: ToolRegistry = field(default_factory=default_registry)
    max_steps_per_task: int = 4
    planner_system: str = PLANNER_SYSTEM

    def plan(self, task: str) -> List[str]:
        out = self.provider.complete(
            [Message("system", self.planner_system), Message("user", task)]
        )
        return parse_plan(out) or [task]

    def execute(self, task: str) -> PlanAndExecuteResult:
        plan = self.plan(task)
        executor = ReActAgent(
            provider=self.provider,
            registry=self.registry,
            max_steps=self.max_steps_per_task,
        )
        steps: List[PlanStep] = []
        context = ""
        for desc in plan:
            question = desc if not context else f"{desc}\n\nContext so far:\n{context}"
            state = executor.run(question)
            result = state.answer or ""
            steps.append(PlanStep(desc, result))
            context += f"- {desc} -> {result}\n"
        answer = steps[-1].result if steps else ""
        return PlanAndExecuteResult(plan=plan, steps=steps, answer=answer)
