"""Pytest configuration for end-to-end tests.

E2E tests use live Playwright and navigate to real websites.
"""

import asyncio
import contextlib
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
    # Match the default in src/config.py for devcontainer compatibility
    host = os.getenv("PLAYWRIGHT_HOST", "host.docker.internal")
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


@pytest.fixture
def skip_if_no_playwright(playwright_url: str):
    """Skip test if Playwright container not available."""
    import socket

    # Parse host and port from URL
    host = playwright_url.split("://")[1].split(":")[0]
    port = int(playwright_url.split(":")[-1])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
    except socket.gaierror:
        pytest.skip(f"Playwright not resolvable at {playwright_url}")
    finally:
        with contextlib.suppress(Exception):
            sock.close()

    if result != 0:
        pytest.skip(f"Playwright not available at {playwright_url}")


@pytest.fixture(autouse=True)
async def cleanup_browser_after_test():
    """Clean up browser resources after each test to prevent event loop issues."""
    yield
    await cleanup_browser()
