"""FastAPI surface for ChatService. Requires `pip install '.[serve]'`.

Kept deliberately thin: all logic lives in agentic_toolkit.service so it is
testable without a running server. The app is built by `create_app()` and is
configured entirely via environment variables (see agentic_toolkit.config), so
adapting it to a challenge is usually just editing `.env` or the ConfigMap.

Run with:

    uvicorn serving.app:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError as exc:  # pragma: no cover - import-time guard
    raise SystemExit("Install serve extras: pip install '.[serve]'") from exc

from agentic_toolkit import __version__
from agentic_toolkit.config import build_provider, load_docs
from agentic_toolkit.rag import Retriever
from agentic_toolkit.service import ChatService


class ChatRequest(BaseModel):
    question: str
    k: int = 3


def create_app() -> "FastAPI":
    app = FastAPI(title="Agentic Toolkit", version=__version__)
    service = ChatService(
        provider=build_provider(),
        retriever=Retriever.from_texts(load_docs(), chunk=False),
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "version": __version__}

    @app.post("/chat")
    def chat(req: ChatRequest) -> dict:
        return service.chat(req.question, k=req.k)

    return app


app = create_app()
