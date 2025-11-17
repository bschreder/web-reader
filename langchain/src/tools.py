"""
LangChain tool wrappers for FastMCP tools.
Wraps MCP browser automation tools as LangChain StructuredTools.
"""


from langchain_core.tools import StructuredTool
from loguru import logger
from pydantic import BaseModel, Field

from .mcp_client import MCPClient
from .collector import get_collector


# ============================================================================
# Tool Argument Schemas
# ============================================================================


class NavigateToArgs(BaseModel):
    """Arguments for navigate_to tool."""

    url: str = Field(..., description="Target URL to navigate to")
    wait_until: str = Field(
        "networkidle",
        description="When to consider navigation complete: 'load', 'domcontentloaded', 'networkidle'",
    )


class GetPageContentArgs(BaseModel):
    """Arguments for get_page_content tool (no args needed)."""

    pass


class TakeScreenshotArgs(BaseModel):
    """Arguments for take_screenshot tool."""

    full_page: bool = Field(
        False,
        description="Capture full scrollable page (True) or viewport only (False)",
    )


# ============================================================================
# Tool Wrapper Functions
# ============================================================================


async def navigate_to_wrapper(url: str, wait_until: str, mcp_client: MCPClient) -> str:
    """
    Navigate browser to URL.

    Args:
        url: Target URL
        wait_until: Load event to wait for
        mcp_client: MCP client instance

    Returns:
        Human-readable result message
    """
    result = await mcp_client.call_tool(
        "navigate_to", {"url": url, "wait_until": wait_until}
    )

    if result.get("status") == "success":
        title = result.get("title", "Unknown")
        final_url = result.get("url", url)
        # Collect citation for the visited page
        try:
            get_collector().add_citation(final_url, title=title, source="navigate_to")
        except Exception:
            # Collector must never break tool output; best-effort only
            logger.debug("Failed to record citation in collector")
        return f"Successfully navigated to '{title}' at {final_url}"
    else:
        error = result.get("error", "Unknown error")
        return f"Navigation failed: {error}"


async def get_page_content_wrapper(mcp_client: MCPClient) -> str:
    """
    Extract content from current page.

    Args:
        mcp_client: MCP client instance

    Returns:
        Human-readable content summary
    """
    result = await mcp_client.call_tool("get_page_content", {})

    if result.get("status") == "success":
        title = result.get("title", "Unknown")
        text = result.get("text", "")
        word_count = result.get("word_count", 0)
        links = result.get("links", [])
        links_count = len(links)

        # Collect page citation and discovered links
        try:
            page_url = result.get("url")
            if page_url:
                get_collector().add_citation(
                    page_url, title=title, source="get_page_content"
                )
            for link in links[:10]:  # cap to avoid excessive growth
                get_collector().add_citation(
                    link, source="get_page_content", parent=page_url
                )
        except Exception:
            logger.debug("Failed to record content citations in collector")

        # Truncate text for agent consumption
        preview = text[:500] + "..." if len(text) > 500 else text

        return f"""Page: {title}
Content ({word_count} words, {links_count} links):
{preview}"""
    else:
        error = result.get("error", "Unknown error")
        return f"Content extraction failed: {error}"


async def take_screenshot_wrapper(full_page: bool, mcp_client: MCPClient) -> str:
    """
    Capture screenshot of current page.

    Args:
        full_page: Whether to capture full page
        mcp_client: MCP client instance

    Returns:
        Human-readable result message
    """
    result = await mcp_client.call_tool("take_screenshot", {"full_page": full_page})

    if result.get("status") == "success":
        image_b64 = result.get("image", "")
        image_size = len(image_b64) // 1024  # Rough KB estimate
        page_type = "full page" if full_page else "viewport"
        # Collect screenshot artifact
        try:
            if image_b64:
                get_collector().add_screenshot(image_b64)
        except Exception:
            logger.debug("Failed to record screenshot in collector")
        return f"Screenshot captured ({page_type}, ~{image_size}KB)"
    else:
        error = result.get("error", "Unknown error")
        return f"Screenshot failed: {error}"


# ============================================================================
# Tool Creation
# ============================================================================


def create_langchain_tools(mcp_client: MCPClient) -> list[StructuredTool]:
    """
    Create LangChain StructuredTool wrappers for MCP tools.

    Args:
        mcp_client: MCP client instance

    Returns:
        List of LangChain StructuredTools
    """
    tools = []

    # Navigate to URL tool
    navigate_tool = StructuredTool.from_function(
        coroutine=lambda url, wait_until="networkidle": navigate_to_wrapper(
            url, wait_until, mcp_client
        ),
        name="navigate_to",
        description="""Navigate browser to a URL and wait for page load.
Use this to visit web pages, search engines, or follow links.
The URL will be automatically normalized (http->https, add protocol if missing).
Returns success/failure message with page title.""",
        args_schema=NavigateToArgs,
    )
    tools.append(navigate_tool)

    # Get page content tool
    content_tool = StructuredTool.from_function(
        coroutine=lambda: get_page_content_wrapper(mcp_client),
        name="get_page_content",
        description="""Extract text content and links from the current page.
Use this after navigating to a page to read its content.
Returns page title, text content preview, word count, and number of links found.
The full content is available but truncated in the response for readability.""",
        args_schema=GetPageContentArgs,
    )
    tools.append(content_tool)

    # Take screenshot tool
    screenshot_tool = StructuredTool.from_function(
        coroutine=lambda full_page=False: take_screenshot_wrapper(
            full_page, mcp_client
        ),
        name="take_screenshot",
        description="""Capture a screenshot of the current page.
Use this to preserve visual evidence or capture images/diagrams.
Set full_page=True to capture entire scrollable page, or False for viewport only.
Returns confirmation message with approximate image size.""",
        args_schema=TakeScreenshotArgs,
    )
    tools.append(screenshot_tool)

    logger.info(f"Created {len(tools)} LangChain tools from MCP client")
    return tools
