from __future__ import annotations

from typing import Any, Optional

import httpx
from fastmcp import Client as FastMCPClient
from loguru import logger

from .config import FASTMCP_HEALTH_PORT, FASTMCP_HOST, FASTMCP_URL

"""MCP client wrapper built on FastMCP 2.0 client abstractions.

This module provides a thin, opinionated wrapper around :class:`fastmcp.Client`
for use by the LangChain orchestration service. It preserves the previous
``call_tool`` interface and health check behavior while delegating protocol
details to FastMCP itself.
"""


class MCPClient:
    """Client for communicating with the FastMCP server.

    This wraps :class:`fastmcp.Client` and exposes a small, stable surface area
    used by the LangChain tools layer:

    - ``call_tool(name, arguments)`` to invoke a single MCP tool
    - ``health_check()`` to check the out-of-band HTTP health server
    """

    def __init__(self, base_url: str = FASTMCP_URL, health_url: Optional[str] = None):
        # Normalize provided base_url and ensure it points at the FastMCP
        # HTTP transport path (`/mcp`).
        self.base_url = base_url.rstrip("/")
        if not self.base_url.endswith("/mcp"):
            self.base_url = f"{self.base_url}/mcp"

        # FastMCP client expects the MCP server URL; we run it over HTTP
        # (not stdio) as configured in ``fastmcp/server.py``.
        self._client: Optional[FastMCPClient] = None

        # Health server runs on a separate port; default derive from host
        if health_url is None:
            try:
                host = self.base_url.split("://", 1)[1].split(":")[0]
            except Exception:
                host = FASTMCP_HOST
            self.health_url = f"http://{host}:{FASTMCP_HEALTH_PORT}"
        else:
            self.health_url = health_url

    async def __aenter__(self) -> "MCPClient":
        """Async context manager entry.

        We create an underlying :class:`fastmcp.Client` bound to the HTTP
        transport endpoint exposed by the FastMCP server.
        """

        self._client = FastMCPClient(self.base_url)
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit.

        Ensures the underlying FastMCP client is closed cleanly.
        """

        if self._client is not None:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)
            self._client = None

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Call a tool on the FastMCP server.

        Args:
            tool_name: MCP tool name (as registered on the FastMCP server).
            arguments: Tool arguments.

        Returns:
            Tool execution result as a dict. If an error occurs, a structured
            ``{"status": "error", "error": str, "recoverable": bool}``
            payload is returned instead of raising.
        """

        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            logger.debug(
                f"Calling MCP tool via FastMCP client: {tool_name} {arguments}"
            )

            result = await self._client.call_tool(name=tool_name, arguments=arguments)

            if not isinstance(result, dict):
                logger.debug("Wrapping non-dict MCP result from tool %s", tool_name)
                return {"status": "success", "data": result}

            logger.debug(f"MCP tool {tool_name} result status: {result.get('status')}")
            return result

        except Exception as e:  # pragma: no cover - network / protocol edge cases
            logger.error(
                f"Unexpected error calling MCP tool {tool_name} via FastMCP client: {e.__class__.__name__}: {e!r}"
            )
            return {
                "status": "error",
                "error": f"Unexpected error: {e.__class__.__name__}: {e!r}",
                "recoverable": False,
            }

    async def health_check(self) -> bool:
        """Check if the FastMCP server is healthy.

        This hits the lightweight HTTP health server that runs alongside the
        MCP HTTP transport inside the FastMCP container.
        """

        try:
            url = f"{self.health_url}/health"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return response.status_code == 200

        except Exception as e:  # pragma: no cover - network flakiness
            logger.warning(f"FastMCP health check failed: {e}")
            return False


_mcp_client: Optional[MCPClient] = None


async def get_mcp_client() -> MCPClient:
    """Get or create global MCP client.

    This mirrors the previous behavior so existing call sites need no
    modification beyond the internal implementation change.
    """

    global _mcp_client

    if _mcp_client is None:
        _mcp_client = MCPClient()
        await _mcp_client.__aenter__()

    return _mcp_client


async def close_mcp_client() -> None:
    """Close global MCP client if it was created."""

    global _mcp_client

    if _mcp_client is not None:
        await _mcp_client.__aexit__(None, None, None)
        _mcp_client = None
