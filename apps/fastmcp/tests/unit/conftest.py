"""Pytest configuration and shared fixtures."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

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
