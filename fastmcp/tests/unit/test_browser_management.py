"""Tests for browser and context management."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.browser import create_context, get_browser


@pytest.fixture
def mock_browser() -> MagicMock:
    """Fixture that provides a mock browser instance."""
    browser = MagicMock()
    browser.new_context = AsyncMock()
    return browser


class TestGetBrowser:
    """Test browser initialization and connection."""

    @pytest.mark.asyncio
    async def test_creates_browser_once(self, mocker: MockerFixture):
        """Test that browser is created only once (singleton)."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_playwright.chromium.connect = AsyncMock(return_value=mock_browser)

        mocker.patch("src.browser._playwright", None)
        mocker.patch("src.browser._browser", None)
        mock_ap = mocker.patch("src.browser.async_playwright")
        mock_ap_instance = MagicMock()
        mock_ap_instance.start = AsyncMock(return_value=mock_playwright)
        mock_ap.return_value = mock_ap_instance

        # First call should create browser
        browser1 = await get_browser()
        # Second call should return same instance
        browser2 = await get_browser()

        assert browser1 is browser2
        mock_ap_instance.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_connects_to_remote_playwright(self, mocker: MockerFixture):
        """Test connection to remote Playwright server."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_playwright.chromium.connect = AsyncMock(return_value=mock_browser)

        mocker.patch("src.browser._playwright", None)
        mocker.patch("src.browser._browser", None)
        mocker.patch("src.browser.PLAYWRIGHT_HOST", "playwright")
        mocker.patch("src.browser.PLAYWRIGHT_PORT", 3002)
        mock_ap = mocker.patch("src.browser.async_playwright")
        mock_ap_instance = MagicMock()
        mock_ap_instance.start = AsyncMock(return_value=mock_playwright)
        mock_ap.return_value = mock_ap_instance

        _ = await get_browser()

        # Should have called connect with correct URL
        mock_playwright.chromium.connect.assert_called_once_with("ws://playwright:3002")

    @pytest.mark.asyncio
    async def test_remote_connection_failure_raises(self, mocker: MockerFixture):
        """Remote connection failure should propagate (no fallback)."""
        mock_playwright = MagicMock()
        mock_playwright.chromium.connect = AsyncMock(side_effect=Exception("Connection failed"))

        mocker.patch("src.browser._playwright", None)
        mocker.patch("src.browser._browser", None)
        mocker.patch("src.browser.PLAYWRIGHT_HOST", "playwright")
        mock_ap = mocker.patch("src.browser.async_playwright")
        mock_ap_instance = MagicMock()
        mock_ap_instance.start = AsyncMock(return_value=mock_playwright)
        mock_ap.return_value = mock_ap_instance

        with pytest.raises(Exception):
            await get_browser()

        mock_playwright.chromium.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_uses_local_launch_for_localhost(self, mocker: MockerFixture):
        """Test that localhost host triggers local browser launch."""
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=MagicMock())

        mocker.patch("src.browser._playwright", None)
        mocker.patch("src.browser._browser", None)
        mocker.patch("src.browser.PLAYWRIGHT_HOST", "localhost")
        mock_ap = mocker.patch("src.browser.async_playwright")
        mock_ap_instance = MagicMock()
        mock_ap_instance.start = AsyncMock(return_value=mock_playwright)
        mock_ap.return_value = mock_ap_instance

        _ = await get_browser()

        # Should launch locally, not connect
        mock_playwright.chromium.launch.assert_called_once()
        assert not mock_playwright.chromium.connect.called


class TestCreateContext:
    """Test browser context creation."""

    @pytest.mark.asyncio
    async def test_creates_deidentified_context(
        self, mocker: MockerFixture, mock_browser: MagicMock
    ):
        """Test that context has privacy features enabled."""
        mock_context = MagicMock()
        mock_context.add_init_script = AsyncMock(return_value=None)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mocker.patch("src.browser.get_browser", return_value=mock_browser)
        _ = await create_context()

        # Verify context was created
        mock_browser.new_context.assert_called_once()
        call_kwargs = mock_browser.new_context.call_args[1]

        # Check privacy settings
        assert call_kwargs["accept_downloads"] is False
        assert call_kwargs["ignore_https_errors"] is False
        assert "permissions" in call_kwargs
        assert call_kwargs["permissions"] == []

    @pytest.mark.asyncio
    async def test_uses_randomized_user_agent(self, mocker: MockerFixture, mock_browser: MagicMock):
        """Test that user agent is randomized."""
        mock_context = MagicMock()
        mock_context.add_init_script = AsyncMock(return_value=None)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mocker.patch("src.browser.get_browser", return_value=mock_browser)
        # Patch the list where it's used (imported into src.browser)
        mocker.patch("src.browser.USER_AGENTS", ["UA1", "UA2", "UA3"])

        # Create multiple contexts
        contexts_uas: list[str] = []
        for _ in range(10):
            await create_context()
            call_kwargs = mock_browser.new_context.call_args[1]
            contexts_uas.append(call_kwargs["user_agent"])

        # Should use user agents from the list
        assert all(ua in ["UA1", "UA2", "UA3"] for ua in contexts_uas)

    @pytest.mark.asyncio
    async def test_custom_viewport(self, mocker: MockerFixture, mock_browser: MagicMock):
        """Test context creation with custom viewport."""
        mock_context = MagicMock()
        mock_context.add_init_script = AsyncMock(return_value=None)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mocker.patch("src.browser.get_browser", return_value=mock_browser)
        viewport = {"width": 1920, "height": 1080}
        _ = await create_context(viewport=viewport)

        call_kwargs = mock_browser.new_context.call_args[1]
        assert call_kwargs["viewport"] == viewport

    @pytest.mark.asyncio
    async def test_custom_user_agent(self, mocker: MockerFixture, mock_browser: MagicMock):
        """Test context creation with custom user agent."""
        mock_context = MagicMock()
        mock_context.add_init_script = AsyncMock(return_value=None)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mocker.patch("src.browser.get_browser", return_value=mock_browser)
        custom_ua = "Custom User Agent"
        _ = await create_context(user_agent=custom_ua)

        call_kwargs = mock_browser.new_context.call_args[1]
        assert call_kwargs["user_agent"] == custom_ua
