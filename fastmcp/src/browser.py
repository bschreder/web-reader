"""
Browser management module.
Handles Playwright browser connections, contexts, and page management.
"""

import inspect
import random
from urllib.parse import urlparse

from loguru import logger
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from .config import PLAYWRIGHT_HOST, PLAYWRIGHT_PORT, USER_AGENTS

# ============================================================================
# Global State
# ============================================================================

_playwright: Playwright | None = None
_browser: Browser | None = None

# Task-scoped contexts (keyed by task_id or "default" for backwards compatibility)
_contexts: dict[str, BrowserContext] = {}
_pages: dict[str, Page] = {}

# ============================================================================
# Helper Functions
# ============================================================================


async def _maybe_await(result):
    """Helper to handle both awaitable and non-awaitable results (for testing)."""
    return await result if inspect.isawaitable(result) else result


def normalize_url(url: str) -> str:
    """
    Normalize URL: convert http to https, add https if no protocol.

    Args:
        url: Input URL

    Returns:
        Normalized URL with https protocol
    """
    url = url.strip()

    # If no protocol, add https://
    if not url.startswith(("http://", "https://")):
        return f"https://{url}"

    # Convert http:// to https://
    if url.startswith("http://"):
        return url.replace("http://", "https://", 1)

    return url


# ============================================================================
# Browser Connection
# ============================================================================


async def get_browser() -> Browser:
    """
    Get or create shared browser instance.

    For localhost: launches local browser directly
    For remote hosts: connects to remote Playwright server (fails on connection error)

    Returns:
        Browser instance

    Raises:
        Exception: If remote connection fails (no fallback)
    """
    global _playwright, _browser

    if _browser is None:
        logger.info("Initializing Playwright and connecting to browser")
        _playwright = await async_playwright().start()

        # For localhost, use local browser directly (for tests)
        if PLAYWRIGHT_HOST == "localhost":
            logger.info("Using local browser launch for localhost host")
            _browser = await _maybe_await(
                _playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                    ],
                )
            )
        else:
            # For remote hosts, connect to Playwright server (FAIL on error, no fallback)
            playwright_url = f"ws://{PLAYWRIGHT_HOST}:{PLAYWRIGHT_PORT}"
            logger.info(f"Connecting to Playwright server at {playwright_url}")
            _browser = await _maybe_await(_playwright.chromium.connect(playwright_url))
            logger.info("Connected to Playwright server successfully")

        logger.info("Browser initialized successfully")

    return _browser


# ============================================================================
# Browser Context Management
# ============================================================================


async def create_context(
    task_id: str = "default",
    user_agent: str | None = None,
    viewport: dict[str, int] | None = None,
) -> BrowserContext:
    """
    Create a new deidentified browser context for a specific task.

    Each task gets its own isolated context with no shared cookies, storage, or history.
    This ensures privacy and prevents data leakage between research tasks.

    Args:
        task_id: Unique task identifier (default: "default" for backwards compatibility)
        user_agent: Custom user agent (randomized if not provided)
        viewport: Custom viewport size (randomized if not provided)

    Returns:
        New browser context with privacy settings
    """
    browser = await get_browser()

    # Randomize user agent if not provided
    if user_agent is None:
        user_agent = random.choice(USER_AGENTS)

    # Randomize viewport if not provided
    if viewport is None:
        viewport = {
            "width": random.randint(1280, 1920),
            "height": random.randint(720, 1080),
        }

    logger.info(
        f"Creating browser context for task '{task_id}' "
        f"(viewport: {viewport['width']}x{viewport['height']})"
    )

    context = await browser.new_context(
        user_agent=user_agent,
        viewport=viewport,
        ignore_https_errors=False,  # Enforce HTTPS validation for security
        java_script_enabled=True,
        accept_downloads=False,
        has_touch=False,
        is_mobile=False,
        permissions=[],  # No permissions granted
        geolocation=None,
        extra_http_headers={
            "DNT": "1",  # Do Not Track
            "Sec-GPC": "1",  # Global Privacy Control
        },
    )

    # Enable tracking prevention
    await context.add_init_script("""
        // Block tracking scripts
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
    """)

    # Store context for this task
    _contexts[task_id] = context
    logger.debug(f"Stored context for task '{task_id}' (total contexts: {len(_contexts)})")

    return context


async def get_current_page(task_id: str = "default") -> Page:
    """
    Get the current page for a task, creating a new context if needed.

    Args:
        task_id: Unique task identifier (default: "default" for backwards compatibility)

    Returns:
        Current page instance for this task
    """
    global _contexts, _pages

    # Create context and page if they don't exist for this task
    if task_id not in _contexts or task_id not in _pages:
        context = await create_context(task_id=task_id)
        page = await context.new_page()
        _pages[task_id] = page
        logger.info(f"Created new page for task '{task_id}'")

    return _pages[task_id]


# ============================================================================
# Cleanup
# ============================================================================


async def cleanup_task_context(task_id: str) -> None:
    """
    Clean up browser context for a specific task.

    This should be called after each research task completes to:
    - Free memory from unused contexts
    - Ensure no data persists between tasks
    - Maintain privacy guarantees

    Args:
        task_id: Task identifier whose context should be cleaned up
    """
    global _contexts, _pages

    # Close and remove page
    if task_id in _pages:
        try:
            await _pages[task_id].close()
            logger.debug(f"Closed page for task '{task_id}'")
        except Exception as e:
            logger.warning(f"Error closing page for task '{task_id}': {e}")
        finally:
            del _pages[task_id]

    # Close and remove context
    if task_id in _contexts:
        try:
            await _contexts[task_id].close()
            logger.info(
                f"Cleaned up context for task '{task_id}' (remaining: {len(_contexts) - 1})"
            )
        except Exception as e:
            logger.warning(f"Error closing context for task '{task_id}': {e}")
        finally:
            del _contexts[task_id]


async def cleanup_browser():
    """Clean up all browser resources (called on server shutdown)."""
    global _playwright, _browser, _contexts, _pages

    # Close all pages
    for task_id in list(_pages.keys()):
        try:
            await _pages[task_id].close()
        except Exception as e:
            logger.warning(f"Error closing page for task '{task_id}': {e}")
    _pages.clear()

    # Close all contexts
    for task_id in list(_contexts.keys()):
        try:
            await _contexts[task_id].close()
        except Exception as e:
            logger.warning(f"Error closing context for task '{task_id}': {e}")
    _contexts.clear()

    # Close browser and playwright
    if _browser:
        await _browser.close()
        _browser = None

    if _playwright:
        await _playwright.stop()
        _playwright = None

    logger.info("Browser resources cleaned up")
