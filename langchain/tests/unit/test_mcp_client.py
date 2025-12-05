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
        # Patch the FastMCP client used by `MCPClient` so no network calls
        # occur. We return an async context-like mock object that exposes
        # `call_tool` and async context manager methods.
        mock_fastmcp = AsyncMock()
        mock_fastmcp.call_tool = AsyncMock(
            return_value={
                "status": "success",
                "title": "Example",
                "url": "https://example.com",
            }
        )
        mock_fastmcp.__aenter__ = AsyncMock(return_value=None)
        mock_fastmcp.__aexit__ = AsyncMock(return_value=None)

        mocker.patch("src.mcp_client.FastMCPClient", return_value=mock_fastmcp)

        async with MCPClient(base_url="http://test:3000") as client:
            result = await client.call_tool(
                "navigate_to", {"url": "https://example.com"}
            )

            assert result["status"] == "success"
            assert result["url"] == "https://example.com"
            mock_fastmcp.call_tool.assert_called_once_with(
                name="navigate_to", arguments={"url": "https://example.com"}
            )

    @pytest.mark.asyncio
    async def test_call_tool_timeout(self, mocker):
        """Test tool call timeout handling."""
        import httpx

        mock_fastmcp = AsyncMock()
        mock_fastmcp.call_tool = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        mock_fastmcp.__aenter__ = AsyncMock(return_value=None)
        mock_fastmcp.__aexit__ = AsyncMock(return_value=None)

        mocker.patch("src.mcp_client.FastMCPClient", return_value=mock_fastmcp)

        async with MCPClient(base_url="http://test:3000") as client:
            result = await client.call_tool(
                "navigate_to", {"url": "https://example.com"}
            )

            assert result["status"] == "error"
            assert (
                "timeout" in result["error"].lower()
                or "timeoutexception" in result["error"].lower()
            )
            # Under the FastMCP client shape we consider these unexpected
            # exceptions non-recoverable in the wrapper.
            assert result["recoverable"] is False

    @pytest.mark.asyncio
    async def test_call_tool_http_error(self, mocker):
        """Test tool call HTTP error handling."""
        import httpx

        mock_fastmcp = AsyncMock()
        mock_fastmcp.call_tool = AsyncMock(
            side_effect=httpx.HTTPError("Connection failed")
        )
        mock_fastmcp.__aenter__ = AsyncMock(return_value=None)
        mock_fastmcp.__aexit__ = AsyncMock(return_value=None)

        mocker.patch("src.mcp_client.FastMCPClient", return_value=mock_fastmcp)

        async with MCPClient(base_url="http://test:3000") as client:
            result = await client.call_tool(
                "navigate_to", {"url": "https://example.com"}
            )

            assert result["status"] == "error"
            assert "http" in result["error"].lower()
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

        # Patch FastMCP client to avoid network calls during the context
        mock_fastmcp = AsyncMock()
        mock_fastmcp.__aenter__ = AsyncMock(return_value=None)
        mock_fastmcp.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("src.mcp_client.FastMCPClient", return_value=mock_fastmcp)

        async with MCPClient(base_url="http://example.com:3000") as client:
            # Since health_check uses httpx.AsyncClient directly we only need
            # to ensure the FastMCP client enters cleanly.
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

        # Patch FastMCP client to avoid network calls during the context
        mock_fastmcp = AsyncMock()
        mock_fastmcp.__aenter__ = AsyncMock(return_value=None)
        mock_fastmcp.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("src.mcp_client.FastMCPClient", return_value=mock_fastmcp)

        async with MCPClient(base_url="http://test:3000") as client:
            is_healthy = await client.health_check()

            assert is_healthy is False

    @pytest.mark.asyncio
    async def test_context_manager(self, mocker):
        """Test context manager lifecycle."""
        # Patch the FastMCP client so context manager entry does not attempt
        # to make network calls.
        mock_fastmcp = AsyncMock()
        mock_fastmcp.__aenter__ = AsyncMock(return_value=None)
        mock_fastmcp.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("src.mcp_client.FastMCPClient", return_value=mock_fastmcp)

        async with MCPClient(base_url="http://test:3000") as client:
            assert client._client is not None

        # Client should be closed after exiting context
        # (In real usage, but we can't easily verify without side effects)
