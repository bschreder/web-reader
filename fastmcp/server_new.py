"""
Web Reader FastMCP Server - Main Entry Point
==============================================
MCP protocol server providing browser automation tools via Playwright.

This module serves as the main entry point, coordinating configuration,
lifecycle management, and tool registration.
"""

from loguru import logger

from src.browser import cleanup_browser
from src.config import configure_logging
from src.filtering import load_allowed_domains, load_disallowed_domains
from src.tools import navigate_to, get_page_content, take_screenshot

# ============================================================================
# Configuration
# ============================================================================

# Configure logging first
configure_logging()

# ============================================================================
# Identity Decorators (for testing without FastMCP)
# ============================================================================


def on_startup(fn):
    """Identity decorator for startup handler."""
    return fn


def on_shutdown(fn):
    """Identity decorator for shutdown handler."""
    return fn


# ============================================================================
# Lifecycle Handlers
# ============================================================================


@on_startup
async def startup() -> None:
    """Initialize server resources."""
    logger.info("FastMCP server initializing...")

    # Load domain lists
    load_allowed_domains("config/allowed-domains.txt")
    load_disallowed_domains("config/disallowed-domains.txt")

    logger.info("FastMCP server ready")


@on_shutdown
async def shutdown() -> None:
    """Clean up server resources."""
    logger.info("FastMCP server shutting down...")

    await cleanup_browser()

    logger.info("FastMCP server stopped")


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting FastMCP server...")
    try:
        from fastmcp import FastMCP  # type: ignore

        mcp = FastMCP("Web Reader Browser Tools")

        # Register tools and lifecycle handlers at runtime
        navigate_to = mcp.tool()(navigate_to)
        get_page_content = mcp.tool()(get_page_content)
        take_screenshot = mcp.tool()(take_screenshot)
        startup = mcp.on_startup(startup)
        shutdown = mcp.on_shutdown(shutdown)

        mcp.run()
    except Exception as e:  # pragma: no cover
        logger.error(f"Failed to start MCP server: {e}")
        raise
