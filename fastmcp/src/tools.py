"""MCP tool, resource, and prompt implementations.

This module defines the concrete browser automation tools exposed via the
Model Context Protocol as well as higher-level resources and prompts that
provide more structured access patterns for the LangChain orchestrator.
"""

import asyncio
import base64
import time
from typing import Any
from urllib.parse import urlparse

from loguru import logger
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from pydantic import BaseModel, Field

from .browser import get_current_page, normalize_url
from .config import (
    HTTP_ERROR_THRESHOLD,
    HTTP_STATUS_MESSAGES,
    MAX_LINKS,
    MAX_TEXT_CHARS,
    REQUEST_DELAY_MIN,
    REQUEST_DELAY_MAX,
)
from .filtering import is_domain_allowed
from .rate_limiting import enforce_rate_limit

# ============================================================================
# Pydantic Schemas for Tool Arguments
# ============================================================================


class NavigateToArgs(BaseModel):
    url: str = Field(..., description="Target URL (must be http or https)")
    wait_until: str = Field(
        "networkidle",
        description="When to consider navigation complete: 'load', 'domcontentloaded', 'networkidle'",
    )
    task_id: str = Field(
        "default",
        description="Task identifier for context isolation (default: 'default')",
    )


class ExtractDataArgs(BaseModel):
    extraction_schema: dict[str, Any] = Field(
        ..., description="Schema defining structure to extract"
    )
    task_id: str = Field(
        "default",
        description="Task identifier for context isolation (default: 'default')",
    )


class ScreenshotArgs(BaseModel):
    full_page: bool = Field(
        False, description="Capture full scrollable page (True) or viewport only (False)"
    )
    task_id: str = Field(
        "default",
        description="Task identifier for context isolation (default: 'default')",
    )


# ============================================================================
# Identity Decorators (for testing without FastMCP)
# ============================================================================


def tool():
    """Identity decorator for tool registration."""

    def deco(f):
        return f

    return deco


def resource():
    """Identity decorator for resource registration.

    When running under the FastMCP framework, this decorator will be
    replaced by :meth:`fastmcp.FastMCP.resource`. Keeping this identity
    implementation allows unit tests to run without importing FastMCP.
    """

    def deco(f):
        return f

    return deco


def prompt():
    """Identity decorator for prompt registration.

    When running under FastMCP, this will be swapped for
    :meth:`fastmcp.FastMCP.prompt`.
    """

    def deco(f):
        return f

    return deco


# ============================================================================
# MCP Tools
# ============================================================================


@tool()
async def navigate_to(
    url: str, wait_until: str = "networkidle", task_id: str = "default"
) -> dict[str, Any]:
    """
    Navigate to a URL and wait for page load.

    Args:
        url: Target URL (with or without protocol, http converted to https)
        wait_until: When to consider navigation complete
        task_id: Task identifier for context isolation

    Returns:
        Dict with status, title, url, and timing info
    """
    # Normalize URL: add https if missing, convert http to https
    original_url = url
    url = normalize_url(url)

    if url != original_url:
        logger.info(f"Normalized URL: {original_url} -> {url}")

    # Check domain filters
    if not is_domain_allowed(url):
        domain = urlparse(url).netloc
        return {"status": "error", "error": f"Domain blocked by allow/deny lists: {domain}"}

    # Enforce rate limiting
    await enforce_rate_limit(urlparse(url).netloc)

    try:
        page = await get_current_page(task_id=task_id)

        start_time = time.time()
        response = await page.goto(url, wait_until=wait_until, timeout=30000)
        load_time = time.time() - start_time

        if response is None:
            return {
                "status": "error",
                "error": "Navigation failed - no response received",
                "url": url,
            }

        # Handle error responses
        if response.status >= HTTP_ERROR_THRESHOLD:
            status_text = HTTP_STATUS_MESSAGES.get(response.status, "Unknown Error")

            # Special handling for 429: apply backoff and retry once
            if response.status == 429:
                try:
                    from .rate_limiting import REQUEST_DELAY_MIN, REQUEST_DELAY_MAX
                except Exception:
                    REQUEST_DELAY_MIN, REQUEST_DELAY_MAX = 10, 20

                # Exponential-ish backoff within configured window
                backoff = (REQUEST_DELAY_MIN + REQUEST_DELAY_MAX) / 2
                logger.warning(
                    f"HTTP 429 received for {url}. Backing off ~{backoff:.1f}s and retrying once."
                )
                await asyncio.sleep(backoff)
                retry_start = time.time()
                retry = await page.goto(url, wait_until=wait_until, timeout=30000)
                retry_time = time.time() - retry_start
                if retry and retry.status < HTTP_ERROR_THRESHOLD:
                    title = await page.title()
                    final_url = page.url
                    logger.info(
                        f"Retry succeeded for {final_url} in {retry_time:.2f}s (status: {retry.status})"
                    )
                    success_data = {
                        "title": title,
                        "url": final_url,
                        "http_status": retry.status,
                        "load_time": retry_time,
                        "redirected": final_url != url,
                    }
                    return {"status": "success", **success_data, "data": success_data}

            return {
                "status": "error",
                "http_status": response.status,
                "error": f"{response.status} {status_text}",
                "url": url,
            }

        title = await page.title()
        final_url = page.url

        logger.info(f"Navigated to {final_url} in {load_time:.2f}s (status: {response.status})")

        success_data = {
            "title": title,
            "url": final_url,
            "http_status": response.status,
            "load_time": load_time,
            "redirected": final_url != url,
        }

        # Include both flat keys and nested data for backward compatibility
        return {
            "status": "success",
            **success_data,
            "data": success_data,
        }

    except PlaywrightTimeoutError:
        logger.error(f"Navigation timeout for {url}")
        return {
            "status": "error",
            "error": "Page load timeout (30s exceeded)",
            "url": url,
        }
    except Exception as e:
        logger.error(f"Navigation error for {url}: {e}")
        return {"status": "error", "error": str(e), "url": url}


@tool()
async def get_page_content(task_id: str = "default") -> dict[str, Any]:
    """
    Extract text content and metadata from the current page.

    Args:
        task_id: Task identifier for context isolation

    Returns:
        Dict with title, text, url, links, and metadata
    """
    try:
        page = await get_current_page(task_id=task_id)

        title = await page.title()
        url = page.url

        # Extract structured content
        content = await page.evaluate("""
            () => {
                // Remove unwanted elements
                const exclude = 'nav, footer, aside, .ad, .advertisement, script, style';
                document.querySelectorAll(exclude).forEach(el => el.remove());

                // Get main content
                const main = document.querySelector('main, article, .content, #content')
                             || document.body;

                return {
                    text: main.innerText,
                    html: main.innerHTML
                };
            }
        """)

        # Extract links
        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: a.innerText.trim(),
                href: a.href,
                rel: a.rel
            })).filter(link => link.text && link.href)
        """)

        # Extract metadata
        metadata = await page.evaluate("""
            () => {
                const getMeta = (name) => {
                    const el = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
                    return el ? el.content : null;
                };

                return {
                    description: getMeta('description') || getMeta('og:description'),
                    keywords: getMeta('keywords'),
                    author: getMeta('author'),
                    published: getMeta('article:published_time'),
                    og_image: getMeta('og:image')
                };
            }
        """)

        text = content["text"]
        truncated = False
        if len(text) > MAX_TEXT_CHARS:
            text = text[:MAX_TEXT_CHARS]
            truncated = True

        logger.info(f"Extracted content from {url} ({len(text)} chars, {len(links)} links)")

        content_data = {
            "title": title,
            "url": url,
            "text": text,
            "truncated": truncated,
            "links": links[:MAX_LINKS],
            "metadata": metadata,
            "word_count": len(content["text"].split()),
        }

        # Include both flat keys and nested data for compatibility
        return {
            "status": "success",
            **content_data,
            "data": content_data,
        }

    except Exception as e:
        logger.error(f"Content extraction error: {e}")
        return {"status": "error", "error": str(e)}


@tool()
async def take_screenshot(full_page: bool = False, task_id: str = "default") -> dict[str, Any]:
    """
    Capture a screenshot of the current page.

    Args:
        full_page: If True, capture entire scrollable page. If False, capture viewport only.
        task_id: Task identifier for context isolation

    Returns:
        Dict with base64-encoded PNG image and metadata
    """
    try:
        page = await get_current_page(task_id=task_id)

        screenshot_bytes = await page.screenshot(full_page=full_page, type="png")

        # Convert to base64
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        logger.info(
            f"Captured screenshot (full_page={full_page}, size={len(screenshot_bytes)} bytes)"
        )

        screenshot_data = {
            "image": screenshot_b64,
            "format": "png",
            "full_page": full_page,
        }

        # Include both flat keys and nested data for compatibility
        return {
            "status": "success",
            **screenshot_data,
            "data": screenshot_data,
        }

    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return {"status": "error", "error": str(e)}


# =========================================================================
# Higher-level Resources and Prompts
# =========================================================================


@resource()
async def current_page_resource(task_id: str = "default") -> dict[str, Any]:
    """MCP resource exposing the current page's structured content.

    This is a thin wrapper around :func:`get_page_content` so that
    orchestrators can use the FastMCP resource API (``get_resource``)
    instead of always going through tools.
    """

    return await get_page_content(task_id=task_id)


@prompt()
async def summarize_current_page(task_id: str = "default") -> str:
    """Prompt helper that returns a textual summary target for the LLM.

    The LangChain layer can fetch this as a prompt and feed it directly to
    the model, ensuring consistent summarisation behavior.
    """

    result = await get_page_content(task_id=task_id)
    if result.get("status") != "success":  # pragma: no cover - thin wrapper
        return f"Unable to summarise page: {result.get('error', 'unknown error')}"

    title = result.get("title", "Untitled")
    text = result.get("text", "")
    return f"Page title: {title}\n\nContent:\n{text}"
