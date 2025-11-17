"""Tests for FastMCP tool implementations."""

from base64 import b64decode
import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from http import HTTPStatus

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from pytest_mock import MockerFixture

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import get_page_content, navigate_to, take_screenshot
from src.config import MAX_TEXT_CHARS


class TestNavigateTo:
    """Test navigate_to tool."""

    @pytest.mark.asyncio
    async def test_successful_navigation(self, mocker: MockerFixture, mock_page) -> None:
        """Test successful page navigation."""
        mock_response = MagicMock()
        mock_response.status = int(HTTPStatus.OK)
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.title = AsyncMock(return_value="Test Page")
        mock_page.url = "https://example.com"
        mocker.patch("src.tools.get_current_page", return_value=mock_page)
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        rate_limit_mock = AsyncMock()
        mocker.patch("src.tools.enforce_rate_limit", rate_limit_mock)

        result = await navigate_to("https://example.com")

        assert result["status"] == "success"
        assert result["title"] == "Test Page"
        assert result["url"] == "https://example.com"
        assert result["http_status"] == HTTPStatus.OK
        mock_page.goto.assert_called_once()

    @pytest.mark.asyncio
    async def test_normalizes_url_protocol(self, mocker: MockerFixture, mock_page) -> None:
        """Test that URLs are normalized (http→https, no protocol→https)."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_page.goto = AsyncMock(return_value=mock_response)
        mocker.patch("src.tools.get_current_page", return_value=mock_page)
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        mocker.patch("src.tools.enforce_rate_limit", AsyncMock())

        # Test http → https
        await navigate_to("http://example.com")
        mock_page.goto.assert_called()
        call_args = mock_page.goto.call_args[0][0]
        assert call_args == "https://example.com"

        # Test no protocol → https
        mock_page.goto.reset_mock()
        await navigate_to("example.com")
        call_args = mock_page.goto.call_args[0][0]
        assert call_args == "https://example.com"

    @pytest.mark.asyncio
    async def test_blocked_domain(self, mocker: Any, mock_page) -> None:
        """Test that blocked domains are rejected."""
        mocker.patch("src.tools.is_domain_allowed", return_value=False)
        result = await navigate_to("https://blocked.com")

        assert result["status"] == "error"
        assert "blocked" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_http_error_status(self, mocker: Any, mock_page) -> None:
        """Test handling of HTTP error status codes."""
        mock_response = MagicMock()
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_response.status = HTTPStatus.NOT_FOUND
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        mocker.patch("src.tools.enforce_rate_limit", AsyncMock())

        result = await navigate_to("https://example.com/notfound")

        assert result["status"] == "error"
        assert result["http_status"] == HTTPStatus.NOT_FOUND

        assert result["http_status"] == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_timeout_error(self, mocker: Any, mock_page) -> None:
        """Test handling of timeout errors."""
        mock_page.goto = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))
        mocker.patch("src.tools.get_current_page", return_value=mock_page)
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        mocker.patch("src.tools.enforce_rate_limit", AsyncMock())

        result = await navigate_to("https://slow-site.com")

        assert result["status"] == "error"
        assert "timeout" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_rate_limiting_called(self, mocker: Any, mock_page) -> None:
        """Test that rate limiting is enforced."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_page.goto = AsyncMock(return_value=mock_response)
        mocker.patch("src.tools.get_current_page", return_value=mock_page)
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        rate_limit_mock = AsyncMock()
        mocker.patch("src.tools.enforce_rate_limit", rate_limit_mock)

        await navigate_to("https://example.com")

        rate_limit_mock.assert_called_once_with("example.com")


class TestGetPageContent:
    """Test get_page_content tool."""

    @pytest.mark.asyncio
    async def test_extracts_text_content(self, mocker: Any, mock_page) -> None:
        """Test text content extraction."""
        mock_page.content = AsyncMock(
            return_value="""
        <html>
            <body>
                <h1>Test Title</h1>
                <p>This is test content.</p>
            </body>
        </html>
        """
        )

        mock_locator = MagicMock()
        mock_locator.all_text_contents = AsyncMock(
            return_value=["Test Title", "This is test content."]
        )
        mock_page.locator = MagicMock(return_value=mock_locator)

        # Mock evaluate calls: content, links, metadata
        mock_page.evaluate = AsyncMock(
            side_effect=[
                {"text": "Test Title\nThis is test content.", "html": "<h1>Test Title</h1>..."},
                [
                    {"text": "Link 1", "href": "https://example.com/1", "rel": "nofollow"},
                    {"text": "Link 2", "href": "https://example.com/2", "rel": ""},
                ],
                {
                    "description": "desc",
                    "keywords": "k1,k2",
                    "author": "me",
                    "published": None,
                    "og_image": None,
                },
            ]
        )

        mocker.patch("src.tools.get_current_page", return_value=mock_page)
        result = await get_page_content()

        assert result["status"] == "success"
        assert "Test Title" in result["text"]
        assert "This is test content" in result["text"]

    @pytest.mark.asyncio
    async def test_truncates_long_content(self, mocker: Any, mock_page: Any) -> None:
        """Test that content longer than 10k chars is truncated."""
        long_text = "x" * 15000
        mock_page.content = AsyncMock(return_value=f"<html><body>{long_text}</body></html>")

        mock_locator = MagicMock()
        mock_locator.all_text_contents = AsyncMock(return_value=[long_text])
        mock_page.locator = MagicMock(return_value=mock_locator)

        # Mock evaluate calls for long content
        mock_page.evaluate = AsyncMock(
            side_effect=[
                {"text": long_text, "html": f"<div>{long_text}</div>"},
                [],
                {
                    "description": None,
                    "keywords": None,
                    "author": None,
                    "published": None,
                    "og_image": None,
                },
            ]
        )

        mocker.patch("src.tools.get_current_page", return_value=mock_page)
        result = await get_page_content()

        assert result["status"] == "success"
        assert len(result["text"]) == MAX_TEXT_CHARS

    @pytest.mark.asyncio
    async def test_no_current_page_error(self, mocker: Any) -> None:
        """Test error when no page is available."""
        mock_get = AsyncMock(side_effect=Exception("No page available"))
        mocker.patch("src.tools.get_current_page", mock_get)
        result = await get_page_content()

        assert result["status"] == "error"
        assert "no page" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_extraction_error(self, mocker: Any, mock_page: Any) -> None:
        """Test handling of extraction errors."""
        mock_page.content = AsyncMock(side_effect=Exception("Extraction failed"))
        mocker.patch("src.tools.get_current_page", return_value=mock_page)
        result = await get_page_content()

        assert result["status"] == "error"


class TestTakeScreenshot:
    """Test take_screenshot tool."""

    @pytest.mark.asyncio
    async def test_captures_screenshot(self, mocker: Any, mock_page: Any) -> None:
        """Test screenshot capture."""
        fake_image = b"fake_png_data_12345"
        mock_page.screenshot = AsyncMock(return_value=fake_image)
        mocker.patch("src.tools.get_current_page", return_value=mock_page)
        result = await take_screenshot()

        assert result["status"] == "success"
        assert result["format"] == "png"

        # Verify base64 encoding
        decoded = b64decode(result["image"])
        assert decoded == fake_image

    @pytest.mark.asyncio
    async def test_full_page_screenshot(self, mocker: Any, mock_page: Any) -> None:
        """Test full page screenshot option."""
        mock_page.screenshot = AsyncMock(return_value=b"full_page_image")
        mocker.patch("src.tools.get_current_page", return_value=mock_page)
        result = await take_screenshot(full_page=True)

        assert result["status"] == "success"
        mock_page.screenshot.assert_called_once()
        call_kwargs = mock_page.screenshot.call_args[1]
        assert call_kwargs["full_page"] is True

    @pytest.mark.asyncio
    async def test_no_current_page_error(self, mocker: Any) -> None:
        """Test error when no page is available."""
        mock_get = AsyncMock(side_effect=Exception("No page available"))
        mocker.patch("src.tools.get_current_page", mock_get)
        result = await take_screenshot()

        assert result["status"] == "error"
        assert "no page" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_screenshot_error(self, mocker: Any, mock_page: Any) -> None:
        """Test handling of screenshot errors."""
        mock_page.screenshot = AsyncMock(side_effect=Exception("Screenshot failed"))
        mocker.patch("src.tools.get_current_page", return_value=mock_page)
        result = await take_screenshot()

        assert result["status"] == "error"
