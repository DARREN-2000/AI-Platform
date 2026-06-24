"""FastAPI surface for ChatService. Requires `pip install '.[serve]'`.

Kept deliberately thin: all logic lives in agentic_toolkit.service so it is
testable without a running server. Run with:

    uvicorn serving.app:app --reload
"""
from __future__ import annotations

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError as exc:  # pragma: no cover - import-time guard
    raise SystemExit("Install serve extras: pip install '.[serve]'") from exc

from agentic_toolkit.providers import RuleBasedLLM
from agentic_toolkit.rag import Retriever
from agentic_toolkit.service import ChatService

DOCS = [
    "Paris is the capital of France.",
    "Berlin is the capital of Germany.",
]

app = FastAPI(title="Agentic Toolkit")
_service = ChatService(provider=RuleBasedLLM(), retriever=Retriever.from_texts(DOCS, chunk=False))


class ChatRequest(BaseModel):
    question: str
    k: int = 2


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest) -> dict:
    return _service.chat(req.question, k=req.k)
