"""Pytest configuration for end-to-end tests.

E2E tests use live Playwright and navigate to real websites.
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import after path setup
from src.browser import cleanup_browser


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for compatibility."""
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="session")
def playwright_url() -> str:
    """Get Playwright WebSocket URL from environment."""
    # Use Docker network hostname for devcontainer access
    host = os.getenv("PLAYWRIGHT_HOST", "ws-playwright")
    port = os.getenv("PLAYWRIGHT_PORT", "3002")
    return f"ws://{host}:{port}"


@pytest.fixture(scope="session")
def test_urls() -> dict[str, str]:
    """Provide URLs for E2E testing."""
    return {
        "example": "https://example.com",
        "httpbin": "https://httpbin.org",
        "http_status_404": "https://httpbin.org/status/404",
        "http_status_429": "https://httpbin.org/status/429",
    }


@pytest.fixture(autouse=True)
async def cleanup_browser_after_test():
    """Clean up browser resources after each test to prevent event loop issues."""
    yield
    await cleanup_browser()
