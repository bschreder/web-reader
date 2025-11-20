"""Tests for MCP client wrapper."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.mcp_client import MCPClient


class AsyncClientCtx:
    """Small helper that mimics ``httpx.AsyncClient`` used as an async
    context manager in ``src.mcp_client.health_check``.

    The context yields the provided mock client instance and exposes an
    ``aclose()`` coroutine so the real code can call ``aclose()`` without
    error.
    """

    def __init__(self, mock_client):
        self._mock = mock_client

    async def __aenter__(self):
        return self._mock

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def aclose(self):
        return None


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

        # Patch `httpx.AsyncClient` used inside `mcp_client.health_check` to
        # return our mock_http_client via the reusable `AsyncClientCtx` helper.
        mocker.patch(
            "src.mcp_client.httpx.AsyncClient",
            return_value=AsyncClientCtx(mock_http_client),
        )

        async with MCPClient(base_url="http://example.com:3000") as client:
            is_healthy = await client.health_check()

            assert is_healthy is True
            expected_url = f"{client.health_url}/health"
            mock_http_client.get.assert_called_once_with(expected_url)

    @pytest.mark.asyncio
    async def test_health_check_failure(self, mocker):
        """Test health check when service is down."""
        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(side_effect=Exception("Connection refused"))
        mock_http_client.aclose = AsyncMock()

        mocker.patch(
            "src.mcp_client.httpx.AsyncClient",
            return_value=AsyncClientCtx(mock_http_client),
        )

        async with MCPClient(base_url="http://test:3000") as client:
            is_healthy = await client.health_check()

            assert is_healthy is False

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test context manager lifecycle."""
        async with MCPClient(base_url="http://test:3000") as client:
            assert client._client is not None

        # Client should be closed after exiting context
        # (In real usage, but we can't easily verify without side effects)
