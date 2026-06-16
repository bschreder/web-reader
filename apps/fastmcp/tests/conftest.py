"""Pytest configuration and shared fixtures for FastMCP tests.

Loads `.env` files early so modules that read environment variables at import
time see configured values. Uses `python-dotenv` and then applies safe
defaults for devcontainer runs.
"""

from __future__ import annotations

import asyncio
import os
import socket
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import urlparse

import pytest
from dotenv import load_dotenv

# Load .env files early so modules that read env vars at import time see values
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for candidate in (ROOT / ".env", ROOT / "fastmcp" / ".env", HERE / ".env"):
    load_dotenv(dotenv_path=str(candidate), override=False)

# Safe fallbacks for devcontainer test runs
os.environ.setdefault("OLLAMA_HOST", "ws-ollama")
os.environ.setdefault("OLLAMA_PORT", "11434")
os.environ.setdefault("FASTMCP_HOST", "fastmcp")
os.environ.setdefault("FASTMCP_PORT", "3100")
os.environ.setdefault("PLAYWRIGHT_WS_URL", "ws://playwright:3002")


def _normalize_playwright_ws_for_local_tests() -> None:
    """Use a reachable websocket host when compose DNS is unavailable locally."""
    ws_url = os.environ.get("PLAYWRIGHT_WS_URL", "")
    if not ws_url:
        return

    parsed = urlparse(ws_url)
    host = parsed.hostname
    port = parsed.port or 3002
    if not host:
        return

    try:
        socket.getaddrinfo(host, port)
    except OSError:
        for candidate in ("172.17.0.1", "host.docker.internal", "localhost"):
            try:
                with socket.create_connection((candidate, port), timeout=1):
                    os.environ["PLAYWRIGHT_WS_URL"] = f"ws://{candidate}:{port}"
                    return
            except OSError:
                continue


_normalize_playwright_ws_for_local_tests()

# Add parent directory to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for Windows compatibility."""
    return asyncio.get_event_loop_policy()


@pytest.fixture
async def mock_browser():
    """Mock Playwright browser."""
    browser = MagicMock()
    browser.new_context = AsyncMock()
    browser.close = AsyncMock()
    return browser


@pytest.fixture
async def mock_context():
    """Mock Playwright browser context."""
    context = MagicMock()
    context.new_page = AsyncMock()
    context.close = AsyncMock()
    return context


@pytest.fixture
async def mock_page():
    """Mock Playwright page."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.title = AsyncMock(return_value="Test Page")
    page.url = "https://example.com"
    page.content = AsyncMock(return_value="<html><body>Test</body></html>")
    page.screenshot = AsyncMock(return_value=b"fake_image_data")
    page.locator = MagicMock()
    return page


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    """Create temporary config directory with domain lists."""
    config_path = tmp_path / "config"
    config_path.mkdir()

    # Create allowed-domains.txt
    allowed = config_path / "allowed-domains.txt"
    allowed.write_text("# Allowed domains\n*.allowed.com\nexample.com\n")

    # Create disallowed-domains.txt
    disallowed = config_path / "disallowed-domains.txt"
    disallowed.write_text("# Disallowed domains\n*.blocked.com\nbad-site.com\n")

    return config_path
