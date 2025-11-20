"""
MCP client wrapper.
Communicates with FastMCP server to execute browser automation tools.
"""

from typing import Any, Optional

import httpx
from loguru import logger

from .config import FASTMCP_URL, FASTMCP_HOST, FASTMCP_HEALTH_PORT


class MCPClient:
    """Client for communicating with FastMCP server."""

    def __init__(self, base_url: str = FASTMCP_URL, health_url: Optional[str] = None):
        """
        Initialize MCP client.

        Args:
            base_url: Base URL of FastMCP server
        """
        self.base_url = base_url
        # Health server runs on a separate port; default derive from host + FASTMCP_HEALTH_PORT
        if health_url is None:
            # Extract host from base_url (assumes http://host:port)
            try:
                host = base_url.split("://", 1)[1].split(":")[0]
            except Exception:
                host = FASTMCP_HOST
            self.health_url = f"http://{host}:{FASTMCP_HEALTH_PORT}"
        else:
            self.health_url = health_url
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Call a tool on the FastMCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            httpx.HTTPError: If request fails
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            logger.debug(f"Calling MCP tool: {tool_name} with args: {arguments}")

            response = await self._client.post(
                "/tools/call",
                json={"tool": tool_name, "arguments": arguments},
            )

            response.raise_for_status()
            result = response.json()

            logger.debug(f"MCP tool {tool_name} result: {result.get('status')}")
            return result

        except httpx.TimeoutException:
            logger.error(f"MCP tool {tool_name} timed out")
            return {
                "status": "error",
                "error": "Tool execution timed out",
                "recoverable": True,
            }

        except httpx.HTTPError as e:
            logger.error(f"MCP tool {tool_name} failed: {e}")
            return {
                "status": "error",
                "error": f"HTTP error: {str(e)}",
                "recoverable": False,
            }

        except Exception as e:
            logger.error(f"Unexpected error calling MCP tool {tool_name}: {e}")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "recoverable": False,
            }

    async def health_check(self) -> bool:
        """
        Check if FastMCP server is healthy.

        Returns:
            True if healthy, False otherwise
        """

        try:
            url = f"{self.health_url}/health"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return response.status_code == 200

        except Exception as e:
            logger.warning(f"FastMCP health check failed: {e}")
            return False


# ============================================================================
# Global Client Instance
# ============================================================================

_mcp_client: Optional[MCPClient] = None


async def get_mcp_client() -> MCPClient:
    """Get or create global MCP client."""
    global _mcp_client

    if _mcp_client is None:
        _mcp_client = MCPClient()
        await _mcp_client.__aenter__()

    return _mcp_client


async def close_mcp_client():
    """Close global MCP client."""
    global _mcp_client

    if _mcp_client:
        await _mcp_client.__aexit__(None, None, None)
        _mcp_client = None
