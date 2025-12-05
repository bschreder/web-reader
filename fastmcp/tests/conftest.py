"""Pytest configuration and shared fixtures for FastMCP tests.

Loads `.env` files early so modules that read environment variables at import
time see configured values. Uses `python-dotenv` and then applies safe
defaults for devcontainer runs.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

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
