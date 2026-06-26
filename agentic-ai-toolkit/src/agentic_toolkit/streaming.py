"""Token streaming utilities.

Production chat UIs stream tokens as they are generated. This keeps the same
Provider seam: `StreamingProvider` wraps any Provider and exposes `stream()`
yielding chunks, while still supporting a blocking `complete()`. The offline
`word_stream` chunker makes streaming testable without a network model.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Iterator

from .providers import Provider


def word_stream(text: str) -> Iterator[str]:
    """Yield `text` in whitespace-preserving chunks (offline token stand-in)."""
    for part in re.split(r"(\s+)", text):
        if part:
            yield part


def collect(chunks: Iterable[str]) -> str:
    return "".join(chunks)


@dataclass
class StreamingProvider:
    """Adapts a blocking Provider into a chunk generator (offline-safe)."""

    inner: Provider

    @property
    def name(self) -> str:
        return getattr(self.inner, "name", "streaming")

    def complete(self, messages, *, temperature: float = 0.0, max_tokens: int = 512) -> str:
        return self.inner.complete(
            messages, temperature=temperature, max_tokens=max_tokens
        )

    def stream(
        self, messages, *, temperature: float = 0.0, max_tokens: int = 512
    ) -> Iterator[str]:
        text = self.inner.complete(
            messages, temperature=temperature, max_tokens=max_tokens
        )
        yield from word_stream(text)
