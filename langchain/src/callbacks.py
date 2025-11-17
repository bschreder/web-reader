"""
WebSocket callback handler for streaming agent events.

This module provides a LangChain callback handler that streams agent
execution events to connected WebSocket clients in real-time.
"""

from __future__ import annotations

import json
from datetime import datetime, UTC
from typing import Any, Dict, List

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult
from loguru import logger


class WebSocketCallbackHandler(AsyncCallbackHandler):
    """
    Stream LangChain agent events to a WebSocket connection.

    Events streamed:
    - agent:thinking - LLM is processing
    - agent:tool_call - Tool is being invoked
    - agent:tool_result - Tool execution completed
    - agent:complete - Agent finished successfully
    - agent:error - Error occurred during execution
    """

    def __init__(self, websocket):
        """
        Initialize callback handler.

        Args:
            websocket: FastAPI WebSocket connection instance
        """
        self.websocket = websocket
        self.start_time = datetime.now(UTC)

    async def _send_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Send an event to the WebSocket client.

        Args:
            event_type: Type of event (e.g., "agent:thinking")
            data: Event payload
        """
        try:
            event = {
                "type": event_type,
                "timestamp": datetime.now(UTC).isoformat(),
                "elapsed": (datetime.now(UTC) - self.start_time).total_seconds(),
                **data,
            }
            await self.websocket.send_json(event)
            logger.debug(f"Sent event: {event_type}")
        except Exception as e:
            logger.error(f"Failed to send WebSocket event: {e}")
            # Don't raise - callback errors should not break agent execution

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Called when LLM starts generating."""
        await self._send_event(
            "agent:thinking",
            {
                "content": "Analyzing your question...",
                "metadata": {"prompt_count": len(prompts)},
            },
        )

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM finishes generating."""
        # Extract generated text from response
        text = ""
        if response.generations:
            if response.generations[0]:
                text = response.generations[0][0].text

        await self._send_event(
            "agent:thought",
            {
                "content": text[:500],  # Truncate for display
                "metadata": {
                    "tokens": response.llm_output.get("token_usage")
                    if response.llm_output
                    else None
                },
            },
        )

    async def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Called when a tool starts executing."""
        tool_name = serialized.get("name", "unknown")

        # Parse tool arguments if they're JSON
        try:
            args = (
                json.loads(input_str)
                if input_str.startswith("{")
                else {"input": input_str}
            )
        except Exception:
            args = {"input": input_str}

        await self._send_event(
            "agent:tool_call",
            {
                "tool": tool_name,
                "args": args,
                "metadata": {"run_id": kwargs.get("run_id")},
            },
        )

    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when a tool finishes executing."""
        await self._send_event(
            "agent:tool_result",
            {
                "output": output[:1000],  # Truncate long outputs
                "metadata": {"run_id": kwargs.get("run_id")},
            },
        )

    async def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when a tool encounters an error."""
        await self._send_event(
            "agent:tool_error",
            {
                "error": str(error),
                "metadata": {"run_id": kwargs.get("run_id")},
            },
        )

    async def on_agent_action(self, action, **kwargs: Any) -> None:
        """Called when agent takes an action."""
        await self._send_event(
            "agent:action",
            {
                "tool": action.tool,
                "tool_input": str(action.tool_input)[:500],
                "log": action.log[:500] if action.log else "",
            },
        )

    async def on_agent_finish(self, finish, **kwargs: Any) -> None:
        """Called when agent finishes execution."""
        await self._send_event(
            "agent:finish",
            {
                "output": str(finish.return_values.get("output", ""))[:500],
                "metadata": {
                    "total_elapsed": (
                        datetime.now(UTC) - self.start_time
                    ).total_seconds(),
                },
            },
        )

    async def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when the chain encounters an error."""
        await self._send_event(
            "agent:error",
            {
                "error": str(error),
                "error_type": type(error).__name__,
            },
        )
