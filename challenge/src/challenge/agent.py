"""Agent composition for the challenge.

Builds an agent / chat service from the toolkit. Defaults are offline (the
RuleBasedLLM provider) so this runs with zero API keys; switch providers via
env. Storage is selected by ``DATABASE_URL`` through the toolkit's storage
adapter.
"""
from __future__ import annotations

from typing import List, Optional

from agentic_toolkit import (
    ChatService,
    ReActAgent,
    Retriever,
    build_provider,
    default_input_guard,
)
from agentic_toolkit.storage import KeyValueStore, make_store

from .config import Settings


def get_settings(settings: Optional[Settings] = None) -> Settings:
    return settings or Settings.from_env()


def build_store(settings: Optional[Settings] = None) -> KeyValueStore:
    settings = get_settings(settings)
    return make_store(settings.database_url)


def build_agent(settings: Optional[Settings] = None) -> ReActAgent:
    settings = get_settings(settings)
    provider = build_provider(settings.provider)
    return ReActAgent(provider=provider, max_steps=settings.max_steps)


def _build_retriever(docs: Optional[List[str]]) -> Optional[Retriever]:
    if not docs:
        return None
    # from_texts fits a TF-IDF embedder over the docs and chunks them.
    return Retriever.from_texts(docs)


def build_service(
    settings: Optional[Settings] = None, docs: Optional[List[str]] = None
) -> ChatService:
    settings = get_settings(settings)
    provider = build_provider(settings.provider)
    return ChatService(
        provider=provider,
        retriever=_build_retriever(docs),
        max_steps=settings.max_steps,
    )


def guarded_input(text: str) -> str:
    """Run the default input guardrail (redacts PII, flags injection)."""
    return default_input_guard().run(text).text
