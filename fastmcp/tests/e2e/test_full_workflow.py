"""End-to-end tests for complete FastMCP workflows."""

import pytest

from src.tools import get_page_content, navigate_to, take_screenshot


class TestFullWorkflow:
    """Test complete navigation and extraction workflows."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_navigate_and_extract_workflow(self, skip_if_no_playwright, test_urls, mocker):
        """Test full workflow: navigate → extract content → take screenshot."""
        # Mock filtering and rate limiting
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        mocker.patch("src.tools.enforce_rate_limit", return_value=None)

        # Step 1: Navigate
        nav_result = await navigate_to(test_urls["example"])
        assert nav_result["status"] == "success"
        assert nav_result["http_status"] == 200

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
    async def test_404_error_handling(self, skip_if_no_playwright, test_urls, mocker):
        """Test handling of 404 errors."""
        # Mock filtering and rate limiting
        mocker.patch("src.tools.is_domain_allowed", return_value=True)
        mocker.patch("src.tools.enforce_rate_limit", return_value=None)

        result = await navigate_to(test_urls["http_status_404"])

        assert result["status"] == "error"
        assert result["http_status"] == 404

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_rate_limiting_enforcement(self, skip_if_no_playwright, test_urls, mocker):
        """Test that rate limiting is enforced across requests."""
        import time

        # Mock domain filtering to avoid accidental blocks
        mocker.patch("src.tools.is_domain_allowed", return_value=True)

        domain = "httpbin.org"

        # Make 5 requests (should be allowed)
        start = time.time()
        for i in range(5):
            result = await navigate_to(f"https://httpbin.org/delay/0")
            assert result["status"] == "success"

        # Track time for first 5 requests
        five_requests_time = time.time() - start

        # 6th request should trigger rate limit wait
        start = time.time()
        result = await navigate_to("https://httpbin.org/delay/0")
        sixth_request_time = time.time() - start

        # Should have waited longer for 6th request
        assert sixth_request_time > 1.0  # At least some delay enforced
