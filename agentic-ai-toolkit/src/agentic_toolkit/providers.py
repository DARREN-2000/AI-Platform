"""LLM provider abstraction + deterministic offline stand-ins.

The `Provider` Protocol is intentionally tiny so swapping OpenAI <-> Anthropic
<-> a local model never touches agent or eval logic. `ScriptedLLM` and
`RuleBasedLLM` make the whole stack runnable and testable with zero API keys.
"""
from __future__ import annotations

import os
import random
import re
import time
from dataclasses import dataclass, field
from typing import Callable, List, Protocol, Sequence


@dataclass(frozen=True)
class Message:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str


class Provider(Protocol):
    name: str

    def complete(
        self,
        messages: Sequence[Message],
        *,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> str: ...


def with_retries(fn: Callable[[], str], *, attempts: int = 3, base_delay: float = 0.5) -> str:
    """Retry with exponential backoff + jitter. Real provider calls flake."""
    last_exc: Exception | None = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - SDKs raise varied errors
            last_exc = exc
            if attempt == attempts - 1:
                break
            time.sleep(base_delay * (2 ** attempt) + random.uniform(0, base_delay))
    assert last_exc is not None
    raise last_exc


@dataclass
class ScriptedLLM:
    """Replays queued responses in order. Deterministic - ideal for unit tests."""

    responses: List[str] = field(default_factory=list)
    name: str = "scripted"
    _i: int = 0

    def complete(self, messages, *, temperature: float = 0.0, max_tokens: int = 512) -> str:
        if self._i >= len(self.responses):
            return "FINAL: (no scripted response)"
        out = self.responses[self._i]
        self._i += 1
        return out


_ARITH = re.compile(r"[-+]?\d[\d\s\.\+\-\*\/\(\)]*[\+\-\*\/]\s*\d[\d\s\.\+\-\*\/\(\)]*")


@dataclass
class RuleBasedLLM:
    """A tiny deterministic 'reasoner' for offline demos. If the prompt contains
    arithmetic and no tool observation exists yet, it calls the calculator tool;
    once an observation is present, it produces a final answer."""

    name: str = "rules"

    def complete(self, messages, *, temperature: float = 0.0, max_tokens: int = 512) -> str:
        has_obs = any(m.role == "tool" for m in messages)
        user = next((m.content for m in messages if m.role == "user"), "")
        if has_obs:
            obs = [m.content for m in messages if m.role == "tool"][-1]
            return f"FINAL: The result is {obs}."
        match = _ARITH.search(user)
        if match:
            return 'ACTION: calculator {"expression": "%s"}' % match.group().strip()
        return f"FINAL: {user}"


@dataclass
class OpenAIProvider:
    """OpenAI-compatible provider. `pip install .[openai]` and set OPENAI_API_KEY.

    Works with any OpenAI-compatible endpoint (OpenRouter, Together, a local
    server) by setting ``base_url`` or the ``OPENAI_BASE_URL`` env var plus an
    ``api_key``. When unset, the SDK's own env handling applies.
    """

    model: str = "gpt-4o-mini"
    name: str = "openai"
    base_url: str | None = None
    api_key: str | None = None

    def complete(self, messages, *, temperature: float = 0.0, max_tokens: int = 512) -> str:
        from openai import OpenAI  # lazy import; production only

        client_kwargs: dict = {}
        base_url = self.base_url or os.getenv("OPENAI_BASE_URL")
        if base_url:
            client_kwargs["base_url"] = base_url
        if self.api_key:
            client_kwargs["api_key"] = self.api_key
        client = OpenAI(**client_kwargs)

        def _call() -> str:
            resp = client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[{"role": m.role, "content": m.content} for m in messages],
            )
            return resp.choices[0].message.content or ""

        return with_retries(_call)


@dataclass
class AnthropicProvider:
    """Production provider. `pip install .[anthropic]` and set ANTHROPIC_API_KEY."""

    model: str = "claude-3-5-sonnet-latest"
    name: str = "anthropic"

    def complete(self, messages, *, temperature: float = 0.0, max_tokens: int = 512) -> str:
        from anthropic import Anthropic  # lazy import

        client = Anthropic()
        system = "\n".join(m.content for m in messages if m.role == "system")
        chat = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]

        def _call() -> str:
            resp = client.messages.create(
                model=self.model,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=chat,
            )
            return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")

        return with_retries(_call)
