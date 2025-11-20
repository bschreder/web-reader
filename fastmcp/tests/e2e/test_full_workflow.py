"""End-to-end tests for complete FastMCP workflows."""

import time
from http import HTTPStatus

import pytest

from src.tools import get_page_content, navigate_to, take_screenshot


class TestFullWorkflow:
    """Test complete navigation and extraction workflows."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_navigate_and_extract_workflow(self, test_urls, mocker):
        """Test full workflow: navigate → extract content → take screenshot."""
        # Mock filtering and rate limiting
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        mocker.patch("src.tools.enforce_rate_limit", return_value=None)

        # Step 1: Navigate
        nav_result = await navigate_to(test_urls["example"])
        assert nav_result["status"] == "success"
        assert nav_result["http_status"] == HTTPStatus.OK

        # Step 2: Extract content
        content_result = await get_page_content()
        assert content_result["status"] == "success"
        assert len(content_result["data"]["text"]) > 0

        # Step 3: Screenshot
        screenshot_result = await take_screenshot()
        assert screenshot_result["status"] == "success"
        assert len(screenshot_result["data"]["image"]) > 0

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_404_error_handling(self, test_urls, mocker):
        """Test handling of HTTP error status codes."""
        # Mock filtering and rate limiting
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        mocker.patch("src.tools.enforce_rate_limit", return_value=None)

        result = await navigate_to(test_urls["http_status_404"])

        assert result["status"] == "error"
        # httpbin may return 404, 503, or other errors depending on availability
        assert result["http_status"] >= 400  # noqa: PLR2004

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_rate_limiting_enforcement(self, test_urls, mocker):
        """Test that rate limiting delays are enforced between requests."""
        # Mock domain filtering to avoid accidental blocks
        mocker.patch("src.tools.is_domain_allowed", return_value=True)

        # Constants for timing assertions
        max_navigation_time = 5.0  # Maximum expected time for first navigation
        min_rate_delay = 8.0  # Minimum rate limit delay (configured 10-20s with tolerance)

        # Make 3 quick requests to the same domain
        domain = "https://example.com"
        delays = []

        for _ in range(3):
            start = time.time()
            result = await navigate_to(domain)
            duration = time.time() - start
            delays.append(duration)
            assert result["status"] == "success"

        # First request should be fast (no rate limit delay)
        assert delays[0] < max_navigation_time

        # Second and third requests should include rate limit delays (10-20s each)
        # Since this is E2E and involves real network, be lenient with timing
        assert delays[1] > min_rate_delay
        assert delays[2] > min_rate_delay
