"""ChatService wires retrieval + agent + tracing into one call. It is framework
agnostic on purpose, so the same logic sits behind FastAPI, a CLI, or a queue
worker unchanged (see serving/app.py for the HTTP layer).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .agent import ReActAgent
from .providers import Provider
from .rag import Retriever, build_grounded_prompt
from .tracing import Tracer


@dataclass
class ChatService:
    provider: Provider
    retriever: Optional[Retriever] = None
    max_steps: int = 6

    def chat(self, question: str, *, k: int = 3) -> dict:
        tracer = Tracer()
        retrieved = []
        system = ""
        with tracer.span("chat", {"question": question}):
            if self.retriever is not None:
                with tracer.span("retrieve", {"k": k}):
                    hits = self.retriever.retrieve(question, k)
                retrieved = [
                    {"id": d.id, "score": round(s, 4), "text": d.text} for s, d in hits
                ]
                system = build_grounded_prompt(question, hits)
            agent = ReActAgent(provider=self.provider, tracer=tracer, max_steps=self.max_steps)
            state = agent.run(question, system=system)
        return {
            "answer": state.answer,
            "trajectory": [s.__dict__ for s in state.trajectory],
            "retrieved": retrieved,
            "trace": tracer.export(),
        }
