"""Integration tests for FastMCP with live Playwright container."""

from http import HTTPStatus
import pytest

from src.browser import create_context, get_browser
from src.tools import get_page_content, navigate_to


class TestPlaywrightIntegration:
    """Test integration with live Playwright container."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_browser_connection(self, skip_if_no_playwright):
        """Test connection to Playwright container."""
        browser = await get_browser()
        assert browser is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_context_creation(self, skip_if_no_playwright):
        """Test creating browser context."""
        context = await create_context()
        assert context is not None
        await context.close()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_navigation_with_real_browser(self, skip_if_no_playwright, mocker):
        """Test page navigation with real browser."""
        # Mock filtering and rate limiting to speed up test
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        mocker.patch("src.tools.enforce_rate_limit", return_value=None)

        result = await navigate_to("https://example.com")

        assert result["status"] == "success"
        assert result["http_status"] == HTTPStatus.OK
        assert "example" in result["title"].lower() or "example" in result["url"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_content_extraction_with_real_browser(self, skip_if_no_playwright, mocker):
        """Test content extraction with real browser."""
        # Mock filtering and rate limiting
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        mocker.patch("src.tools.enforce_rate_limit", return_value=None)

        # Navigate first
        nav_result = await navigate_to("https://example.com")
        assert nav_result["status"] == "success"

        # Extract content
        content_result = await get_page_content()

        assert content_result["status"] == "success"
        assert "text" in content_result["data"]
        assert len(content_result["data"]["text"]) > 0
