"""Unit tests for callbacks module."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.callbacks import WebSocketCallbackHandler


class TestWebSocketCallbackHandler:
    """Test WebSocket callback handler."""

    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket."""
        ws = MagicMock()
        ws.send_json = AsyncMock()
        return ws

    def test_handler_initialization(self, mock_websocket):
        """Test callback handler initialization."""
        handler = WebSocketCallbackHandler(mock_websocket)

        assert handler.websocket is mock_websocket

    @pytest.mark.asyncio
    async def test_on_llm_start(self, mock_websocket):
        """Test LLM start callback."""
        handler = WebSocketCallbackHandler(mock_websocket)

        await handler.on_llm_start(
            serialized={"name": "test_llm"},
            prompts=["test prompt"],
        )

        # Should send event
        assert mock_websocket.send_json.await_count >= 1

    @pytest.mark.asyncio
    async def test_on_tool_start(self, mock_websocket):
        """Test tool start callback."""
        handler = WebSocketCallbackHandler(mock_websocket)

        await handler.on_tool_start(
            serialized={"name": "navigate_to"},
            input_str="https://example.com",
        )

        # Should send tool_call event
        assert mock_websocket.send_json.await_count >= 1

    @pytest.mark.asyncio
    async def test_on_tool_end(self, mock_websocket):
        """Test tool end callback."""
        handler = WebSocketCallbackHandler(mock_websocket)

        await handler.on_tool_end(
            output="Tool completed successfully",
        )

        # Should send tool_result event
        assert mock_websocket.send_json.await_count >= 1

    @pytest.mark.asyncio
    async def test_on_tool_error(self, mock_websocket):
        """Test tool error callback."""
        handler = WebSocketCallbackHandler(mock_websocket)

        await handler.on_tool_error(
            error=Exception("Test error"),
        )

        # Should send error event
        assert mock_websocket.send_json.await_count >= 1

    @pytest.mark.asyncio
    async def test_on_agent_finish(self, mock_websocket):
        """Test agent finish callback."""
        handler = WebSocketCallbackHandler(mock_websocket)

        class Finish:
            def __init__(self):
                self.return_values = {"output": "Test answer"}

        await handler.on_agent_finish(
            finish=Finish(),
        )

        # Should send complete event
        assert mock_websocket.send_json.await_count >= 1

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_websocket):
        """Test that callback errors don't crash."""
        mock_websocket.send_json = AsyncMock(side_effect=Exception("WebSocket error"))
        handler = WebSocketCallbackHandler(mock_websocket)

        # Should not raise even if WebSocket fails
        try:
            await handler.on_tool_start(
                serialized={"name": "test"},
                input_str="test",
            )
        except Exception:
            pytest.fail("Callback should handle errors gracefully")
