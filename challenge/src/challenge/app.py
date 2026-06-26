"""FastAPI app for the challenge (lazy imports so the module loads without
fastapi installed). Reuses the toolkit ChatService via challenge.agent.
"""
from __future__ import annotations

from typing import Optional

from .agent import build_service
from .config import Settings


def create_app(settings: Optional[Settings] = None):
    from fastapi import FastAPI  # lazy
    from pydantic import BaseModel  # lazy

    settings = settings or Settings.from_env()
    service = build_service(settings)
    app = FastAPI(title="challenge", version="0.1.0")

    class ChatRequest(BaseModel):
        question: str
        k: int = 3

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "provider": settings.provider}

    @app.post("/chat")
    def chat(req: ChatRequest) -> dict:
        return service.chat(req.question, k=req.k)

    return app


def __getattr__(name: str):
    # Lazily build `app` only when something (e.g. uvicorn) asks for it.
    if name == "app":
        return create_app()
    raise AttributeError(name)
