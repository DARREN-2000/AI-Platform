"""LLM provider abstraction — swap between OpenAI and Anthropic without touching agents."""
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    content: Optional[str] = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any = None


class LLMProvider(ABC):
    """Common interface for chat-completions with tool calling."""

    @abstractmethod
    async def complete(
        self, messages: list[dict], tools: list[dict]
    ) -> LLMResponse:
        ...


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def complete(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools or None,
            tool_choice="auto" if tools else None,
        )
        msg = resp.choices[0].message
        tool_calls = [
            ToolCall(id=tc.id, name=tc.function.name, arguments=json.loads(tc.function.arguments))
            for tc in (msg.tool_calls or [])
        ]
        return LLMResponse(content=msg.content, tool_calls=tool_calls, raw=msg)


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    @staticmethod
    def _to_anthropic_tools(tools: list[dict]) -> list[dict]:
        return [
            {
                "name": t["function"]["name"],
                "description": t["function"].get("description", ""),
                "input_schema": t["function"]["parameters"],
            }
            for t in tools
        ]

    async def complete(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        system = ""
        chat: list[dict] = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                chat.append(m)

        resp = await self.client.messages.create(
            model=self.model,
            system=system,
            messages=chat,
            tools=self._to_anthropic_tools(tools) if tools else [],
            max_tokens=2048,
        )
        content_text = ""
        tool_calls: list[ToolCall] = []
        for block in resp.content:
            if block.type == "text":
                content_text += block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(id=block.id, name=block.name, arguments=block.input))
        return LLMResponse(content=content_text or None, tool_calls=tool_calls, raw=resp)


def build_provider(provider: str, api_key: str, model: str) -> LLMProvider:
    provider = provider.lower()
    if provider == "openai":
        return OpenAIProvider(api_key=api_key, model=model)
    if provider == "anthropic":
        return AnthropicProvider(api_key=api_key, model=model)
    raise ValueError(f"Unsupported LLM provider: {provider}")
