"""LLM provider abstraction.

Keep this interface tiny on purpose: swapping OpenAI <-> Anthropic <-> a local
model must never touch eval logic. The MockProvider makes the whole harness
runnable with zero API keys, which keeps tests fast and deterministic.
"""
from __future__ import annotations

import json
import random
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Protocol, Sequence


@dataclass(frozen=True)
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


class Provider(Protocol):
    """Minimal LLM provider interface."""

    name: str

    def complete(
        self,
        messages: Sequence[Message],
        *,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> str: ...


def with_retries(fn: Callable[[], str], *, attempts: int = 3, base_delay: float = 0.5) -> str:
    """Retry with exponential backoff + jitter. Real provider calls flake; evals should not."""
    last_exc: Exception | None = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - provider SDKs raise varied errors
            last_exc = exc
            if attempt == attempts - 1:
                break
            time.sleep(base_delay * (2 ** attempt) + random.uniform(0, base_delay))
    assert last_exc is not None
    raise last_exc


@dataclass
class MockProvider:
    """Deterministic, offline provider.

    Acts as a stand-in judge: it reads the structured <eval-input> block that
    judge.py embeds and scores 1..5 by how many rubric keywords the answer hits.
    Override behaviour for specific prompts via ``scripted``.
    """

    name: str = "mock"
    scripted: dict[str, str] = field(default_factory=dict)

    def complete(self, messages, *, temperature: float = 0.0, max_tokens: int = 512) -> str:
        prompt = messages[-1].content if messages else ""
        for needle, response in self.scripted.items():
            if needle in prompt:
                return response
        return self._mock_judge(prompt)

    @staticmethod
    def _mock_judge(prompt: str) -> str:
        match = re.search(r"<eval-input>(.*?)</eval-input>", prompt, re.DOTALL)
        if not match:
            return json.dumps({"score": 1, "reasoning": "No eval-input block found."})
        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            return json.dumps({"score": 1, "reasoning": "eval-input was not valid JSON."})
        answer = (payload.get("answer") or "").lower()
        keywords = [k.lower() for k in payload.get("expected_keywords", [])]
        if not keywords:
            return json.dumps({"score": 3, "reasoning": "No keywords provided; neutral score."})
        hits = sum(1 for k in keywords if k in answer)
        score = int(round(1 + 4 * (hits / len(keywords))))
        return json.dumps({"score": score, "reasoning": f"Matched {hits}/{len(keywords)} rubric keywords."})


@dataclass
class OpenAIProvider:
    """Production provider. Requires `pip install .[openai]` and OPENAI_API_KEY."""

    model: str = "gpt-4o-mini"
    name: str = "openai"

    def complete(self, messages, *, temperature: float = 0.0, max_tokens: int = 512) -> str:
        from openai import OpenAI  # lazy import; only needed in production

        client = OpenAI()

        def _call() -> str:
            resp = client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
                messages=[{"role": m.role, "content": m.content} for m in messages],
            )
            return resp.choices[0].message.content or ""

        return with_retries(_call)


@dataclass
class AnthropicProvider:
    """Production provider. Requires `pip install .[anthropic]` and ANTHROPIC_API_KEY."""

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
