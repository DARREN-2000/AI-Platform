"""Environment-driven configuration helpers.

Centralizing provider/doc selection here means adapting the service to a new
challenge is usually a one-line env change, not a code change.
"""
from __future__ import annotations

import os
from typing import List

from .providers import AnthropicProvider, OpenAIProvider, Provider, RuleBasedLLM

DEFAULT_DOCS: List[str] = [
    "Paris is the capital of France and sits on the Seine river.",
    "Berlin is the capital of Germany.",
    "The mitochondria is the powerhouse of the cell.",
]


def build_provider(name: str | None = None) -> Provider:
    """Build an LLM provider from a name or the AGENTIC_PROVIDER env var.

    Defaults to the offline RuleBasedLLM so the service runs with zero keys.
    """
    name = (name or os.getenv("AGENTIC_PROVIDER", "rules")).lower()
    if name in ("rules", "rule", "offline", "mock"):
        return RuleBasedLLM()
    if name == "openai":
        return OpenAIProvider(model=os.getenv("AGENTIC_MODEL") or "gpt-4o-mini")
    if name == "anthropic":
        return AnthropicProvider(
            model=os.getenv("AGENTIC_MODEL") or "claude-3-5-sonnet-latest"
        )
    raise ValueError(f"unknown provider: {name!r}")


def load_docs() -> List[str]:
    """Load RAG documents from AGENTIC_DOCS_PATH (one per line) or fall back to
    the built-in demo corpus."""
    path = os.getenv("AGENTIC_DOCS_PATH")
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            docs = [line.strip() for line in fh if line.strip()]
        if docs:
            return docs
    return list(DEFAULT_DOCS)
