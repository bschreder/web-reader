"""Pytest configuration for integration tests.

Integration tests connect to real Playwright container but may mock other services.
"""

import asyncio
import contextlib
import os
import socket
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
    host = os.getenv("PLAYWRIGHT_HOST", "host.docker.internal")
    port = os.getenv("PLAYWRIGHT_PORT", "3002")
    return f"ws://{host}:{port}"


@pytest.fixture
def skip_if_no_playwright(playwright_url: str):
    """Skip test if Playwright container not available."""
    # Parse host and port from URL
    host = playwright_url.split("://")[1].split(":")[0]
    port = int(playwright_url.split(":")[-1])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
    except socket.gaierror:
        # DNS resolution failed; treat as not available and skip
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
