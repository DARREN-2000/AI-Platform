"""Conversation memory strategies for multi-turn agents.

Real chat agents need bounded, well-managed context. These memories store a
list of Messages and expose .history() for prompt assembly:

  * BufferMemory       - keep everything (good default for short chats)
  * WindowMemory       - keep only the last N messages
  * TokenWindowMemory  - keep as many recent messages as fit a token budget
  * SummarizingMemory  - compress overflow into a running summary via a Provider

All are dependency-free and run offline. SummarizingMemory degrades gracefully
to a deterministic placeholder summary when no Provider is supplied.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .instrumentation import estimate_tokens
from .providers import Message, Provider


@dataclass
class BufferMemory:
    """Stores the full message history. `system` is prepended on history()."""

    system: Optional[str] = None
    messages: List[Message] = field(default_factory=list)

    def add(self, role: str, content: str) -> "BufferMemory":
        self.messages.append(Message(role, content))
        return self

    def add_user(self, content: str) -> "BufferMemory":
        return self.add("user", content)

    def add_assistant(self, content: str) -> "BufferMemory":
        return self.add("assistant", content)

    def _head(self) -> List[Message]:
        return [Message("system", self.system)] if self.system else []

    def history(self) -> List[Message]:
        return self._head() + list(self.messages)

    def clear(self) -> "BufferMemory":
        self.messages.clear()
        return self


@dataclass
class WindowMemory(BufferMemory):
    """Keeps only the most recent `max_messages` messages."""

    max_messages: int = 10

    def history(self) -> List[Message]:
        return self._head() + list(self.messages[-self.max_messages :])


@dataclass
class TokenWindowMemory(BufferMemory):
    """Keeps as many recent messages as fit within `max_tokens` (estimated)."""

    max_tokens: int = 1024

    def history(self) -> List[Message]:
        kept: List[Message] = []
        budget = self.max_tokens
        for m in reversed(self.messages):
            cost = estimate_tokens(m.content)
            if kept and cost > budget:
                break
            budget -= cost
            kept.append(m)
        kept.reverse()
        return self._head() + kept


@dataclass
class SummarizingMemory(BufferMemory):
    """Summarizes older turns once the buffer exceeds `max_messages`.

    Recent messages stay verbatim; older ones are folded into a rolling summary
    so the prompt stays bounded while keeping long-range context.
    """

    provider: Optional[Provider] = None
    max_messages: int = 8
    summary: str = ""

    def _summarize(self, older: List[Message]) -> str:
        if self.provider is None:
            count = len(older) + (1 if self.summary else 0)
            base = self.summary + " " if self.summary else ""
            return f"{base}[summary of {count} earlier message(s)]"
        prior = f"Existing summary: {self.summary}\n" if self.summary else ""
        convo = "\n".join(f"{m.role}: {m.content}" for m in older)
        prompt = [
            Message(
                "system",
                "Update the running summary of this conversation in 2-3 "
                "sentences. Preserve names, facts, and decisions.",
            ),
            Message("user", prior + convo),
        ]
        return self.provider.complete(prompt).strip()

    def add(self, role: str, content: str) -> "SummarizingMemory":
        super().add(role, content)
        if len(self.messages) > self.max_messages:
            keep_from = len(self.messages) - self.max_messages
            overflow = self.messages[:keep_from]
            self.messages = self.messages[keep_from:]
            self.summary = self._summarize(overflow)
        return self

    def history(self) -> List[Message]:
        head = self._head()
        if self.summary:
            head.append(Message("system", f"Summary so far: {self.summary}"))
        return head + list(self.messages)
