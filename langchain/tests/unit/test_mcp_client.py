"""Tests for MCP client wrapper."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.mcp_client import MCPClient


class TestMCPClient:
    """Test MCP client functionality."""

    @pytest.mark.asyncio
    async def test_call_tool_success(self, mocker):
        """Test successful tool call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "title": "Example",
            "url": "https://example.com",
        }
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)
        mock_http_client.aclose = AsyncMock()

        async with MCPClient(base_url="http://test:3000") as client:
            client._client = mock_http_client

            result = await client.call_tool(
                "navigate_to", {"url": "https://example.com"}
            )

            assert result["status"] == "success"
            assert result["url"] == "https://example.com"
            mock_http_client.post.assert_called_once_with(
                "/tools/call",
                json={
                    "tool": "navigate_to",
                    "arguments": {"url": "https://example.com"},
                },
            )

    @pytest.mark.asyncio
    async def test_call_tool_timeout(self, mocker):
        """Test tool call timeout handling."""
        import httpx

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        mock_http_client.aclose = AsyncMock()

        async with MCPClient(base_url="http://test:3000") as client:
            client._client = mock_http_client

            result = await client.call_tool(
                "navigate_to", {"url": "https://example.com"}
            )

            assert result["status"] == "error"
            assert "timed out" in result["error"].lower()
            assert result["recoverable"] is True

    @pytest.mark.asyncio
    async def test_call_tool_http_error(self, mocker):
        """Test tool call HTTP error handling."""
        import httpx

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(
            side_effect=httpx.HTTPError("Connection failed")
        )
        mock_http_client.aclose = AsyncMock()

        async with MCPClient(base_url="http://test:3000") as client:
            client._client = mock_http_client

            result = await client.call_tool(
                "navigate_to", {"url": "https://example.com"}
            )

            assert result["status"] == "error"
            assert "HTTP error" in result["error"]
            assert result["recoverable"] is False

    @pytest.mark.asyncio
    async def test_health_check_success(self, mocker):
        """Test health check when service is healthy."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.aclose = AsyncMock()

        async with MCPClient(base_url="http://test:3000") as client:
            client._client = mock_http_client

            is_healthy = await client.health_check()

            assert is_healthy is True
            mock_http_client.get.assert_called_once_with("/health")

    @pytest.mark.asyncio
    async def test_health_check_failure(self, mocker):
        """Test health check when service is down."""
        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(side_effect=Exception("Connection refused"))
        mock_http_client.aclose = AsyncMock()

        async with MCPClient(base_url="http://test:3000") as client:
            client._client = mock_http_client

            is_healthy = await client.health_check()

            assert is_healthy is False

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test context manager lifecycle."""
        async with MCPClient(base_url="http://test:3000") as client:
            assert client._client is not None

        # Client should be closed after exiting context
        # (In real usage, but we can't easily verify without side effects)
