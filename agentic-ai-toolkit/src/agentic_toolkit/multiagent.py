"""Multi-agent orchestration: a supervisor routes each request to a named
specialist agent. This is the 'graph of agents' / supervisor pattern - the
natural extension when a single ReAct loop is not enough. Routing can be
keyword-based (deterministic) or delegated to an LLM.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .providers import Message, Provider


@dataclass
class NamedAgent:
    """Wraps any callable handler as a routable, named specialist."""

    name: str
    description: str
    handler: Callable[[str], str]

    def run(self, question: str) -> str:
        return self.handler(question)


@dataclass
class RouteDecision:
    agent: str
    reason: str = ""


def keyword_router(
    routes: Dict[str, List[str]], default: str
) -> Callable[[str], RouteDecision]:
    def route(query: str) -> RouteDecision:
        low = query.lower()
        for agent, keywords in routes.items():
            if any(k.lower() in low for k in keywords):
                return RouteDecision(agent, "keyword match")
        return RouteDecision(default, "default route")

    return route


def llm_router(
    provider: Provider, agents: List[NamedAgent], default: str
) -> Callable[[str], RouteDecision]:
    catalog = "\n".join(f"- {a.name}: {a.description}" for a in agents)
    system = (
        "Route the request to exactly one agent. Reply with only the agent "
        f"name.\nAgents:\n{catalog}"
    )

    def route(query: str) -> RouteDecision:
        out = provider.complete([Message("system", system), Message("user", query)])
        chosen = out.strip().lower()
        for a in agents:
            if a.name.lower() in chosen:
                return RouteDecision(a.name, "llm route")
        return RouteDecision(default, "llm route fallback")

    return route


@dataclass
class Supervisor:
    """Holds named agents and routes each query to one of them."""

    agents: Dict[str, NamedAgent] = field(default_factory=dict)
    router: Optional[Callable[[str], RouteDecision]] = None
    default: Optional[str] = None

    def register(self, agent: NamedAgent) -> "Supervisor":
        self.agents[agent.name] = agent
        if self.default is None:
            self.default = agent.name
        return self

    def _decide(self, query: str) -> RouteDecision:
        if self.router is not None:
            return self.router(query)
        assert self.default is not None, "no agents registered"
        return RouteDecision(self.default, "default route")

    def run(self, query: str) -> dict:
        decision = self._decide(query)
        agent = self.agents.get(decision.agent) or self.agents[self.default]
        return {
            "agent": agent.name,
            "reason": decision.reason,
            "answer": agent.run(query),
        }
