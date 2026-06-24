"""Base ReAct agent loop (Reason → Act → Observe), provider-agnostic."""
import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from .llm import LLMProvider

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Implements a ReAct-style agent loop with tool calling.

    Subclasses define the system prompt, the tool schemas, and how to execute
    each tool. The provider (OpenAI/Anthropic) is injected so agents stay
    model-agnostic.
    """

    MAX_ITERATIONS = 10

    def __init__(self, provider: LLMProvider, tools: list[dict]):
        self.provider = provider
        self.tool_schemas = tools
        self.last_iterations = 0

    @abstractmethod
    def system_prompt(self) -> str:
        ...

    @abstractmethod
    async def execute_tool(self, name: str, args: dict) -> Any:
        ...

    async def run(self, user_message: str) -> str:
        messages: list[dict] = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": user_message},
        ]

        for iteration in range(self.MAX_ITERATIONS):
            self.last_iterations = iteration + 1
            response = await self.provider.complete(messages, self.tool_schemas)

            if not response.tool_calls:
                return response.content or ""

            # Record the assistant turn (raw provider message) then observations.
            messages.append(
                {
                    "role": "assistant",
                    "content": response.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                        }
                        for tc in response.tool_calls
                    ],
                }
            )

            for tc in response.tool_calls:
                logger.info(
                    "tool call", extra={"ctx_agent": self.__class__.__name__, "ctx_tool": tc.name}
                )
                try:
                    result = await self.execute_tool(tc.name, tc.arguments)
                    content = json.dumps(result, default=str)
                except Exception as exc:  # noqa: BLE001
                    content = json.dumps({"error": str(exc)})
                    logger.exception("tool failed: %s", tc.name)

                messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": content}
                )

        return "[Agent] Max iterations reached without a final answer."
