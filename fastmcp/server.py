"""
Web Reader FastMCP Server - Main Entry Point
==============================================
MCP protocol server providing browser automation tools via Playwright.

This module serves as the main entry point, coordinating configuration,
lifecycle management, and tool registration.
"""

import json
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from loguru import logger
import os

from src.browser import cleanup_browser, cleanup_task_context
from src.config import configure_logging
from src.filtering import load_allowed_domains, load_disallowed_domains
from src.tools import get_page_content, navigate_to, take_screenshot

# ============================================================================
# Configuration
# ============================================================================

# Configure logging first
configure_logging()

# ============================================================================
# Lightweight Health Server (HTTP) - No extra deps
# ============================================================================

_health_server: ThreadingHTTPServer | None = None
_health_thread: threading.Thread | None = None


class _HealthHandler(BaseHTTPRequestHandler):
    def _json(self, status: str, code: int = 200):
        payload = {"status": status, "service": "fastmcp"}
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path in ("/health", "/live", "/ready"):
            return self._json("ok", 200)
        return self._json("not-found", 404)

    def log_message(self, format, *args):  # noqa: A003 - silence default logging
        return


def _start_health_server(port: int | None = None):
    global _health_server, _health_thread
    if _health_server is not None:
        return
    try:
        if port is None:
            # Default to 3101 to match docker-compose; allow override via env
            port = int(os.getenv("HEALTH_SERVER_PORT", "3101"))
        server = ThreadingHTTPServer(("0.0.0.0", port), _HealthHandler)
        thread = threading.Thread(target=server.serve_forever, name="fastmcp-health", daemon=True)
        thread.start()
        _health_server = server
        _health_thread = thread
        logger.info(f"FastMCP health server listening on :{port}")
    except Exception as e:
        logger.warning(f"Failed to start health server: {e}")


def _stop_health_server():
    global _health_server
    if _health_server is None:
        return
    try:
        _health_server.shutdown()
        _health_server.server_close()
        logger.info("FastMCP health server stopped")
    finally:
        _health_server = None


# ============================================================================
# Lifecycle Handler
# ============================================================================


@asynccontextmanager
async def lifespan_handler(mcp: "FastMCP") -> AsyncIterator[dict[str, str]]:  # noqa: F821
    """Initialize and cleanup server resources."""
    logger.info("FastMCP server initializing...")

    # Load domain lists
    load_allowed_domains("config/allowed-domains.txt")
    load_disallowed_domains("config/disallowed-domains.txt")

    logger.info("FastMCP server ready")
    _start_health_server()

    yield {"status": "ready"}

    logger.info("FastMCP server shutting down...")
    await cleanup_browser()
    logger.info("FastMCP server stopped")
    _stop_health_server()


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting FastMCP server...")
    try:
        from fastmcp import FastMCP  # type: ignore
        import os

        mcp = FastMCP("Web Reader Browser Tools", lifespan=lifespan_handler)

        # Register tools at runtime
        mcp.tool()(navigate_to)
        mcp.tool()(get_page_content)
        mcp.tool()(take_screenshot)

        # Register cleanup tool (to be called after task completion)
        mcp.tool()(cleanup_task_context)

        # Run as HTTP server (not stdio)
        port = int(os.getenv("MCP_SERVER_PORT", "3000"))
        mcp.run(transport="http", host="0.0.0.0", port=port)
    except Exception as e:  # pragma: no cover
        logger.error(f"Failed to start MCP server: {e}")
        raise
