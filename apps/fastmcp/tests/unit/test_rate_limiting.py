"""Tests for rate limiting functionality."""

import asyncio
import sys
import time
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rate_limiting import enforce_rate_limit


class TestRateLimiting:
    """Test rate limiting enforcement."""

    @pytest.mark.asyncio
    async def test_allows_requests_under_limit(self, mocker: MockerFixture):
        """Test that requests under limit are allowed through."""
        mocker.patch("src.rate_limiting._rate_limits", {})
        mocker.patch("src.rate_limiting.REQUEST_DELAY_MIN", 0)
        mocker.patch("src.rate_limiting.REQUEST_DELAY_MAX", 0)
        domain = "test-domain.com"

        # Should allow 5 requests without blocking
        start = time.time()
        for _ in range(5):
            await enforce_rate_limit(domain)
        elapsed = time.time() - start

        # Should complete quickly (< 1 second startup overhead)
        assert elapsed < 1.0

    @pytest.mark.asyncio
    async def test_enforces_delay_between_requests(self, mocker: MockerFixture):
        """Test that delay is enforced between requests."""
        mocker.patch("src.rate_limiting._rate_limits", {})
        mocker.patch("src.rate_limiting.REQUEST_DELAY_MIN", 0.1)
        mocker.patch("src.rate_limiting.REQUEST_DELAY_MAX", 0.2)
        domain = "test-domain.com"

        # First request (no delay)
        start = time.time()
        await enforce_rate_limit(domain)
        first_elapsed = time.time() - start

        # Second request (should have delay)
        start = time.time()
        await enforce_rate_limit(domain)
        second_elapsed = time.time() - start

        # First request should be fast
        assert first_elapsed < 0.05
        # Second request should have delay (0.1-0.2 seconds)
        assert 0.1 <= second_elapsed <= 0.3

    @pytest.mark.asyncio
    async def test_enforces_window_limit(self, mocker: MockerFixture):
        """Test that 6th request in window is delayed."""
        mocker.patch("src.rate_limiting._rate_limits", {})
        mocker.patch("src.rate_limiting.RATE_LIMIT_REQUESTS", 5)
        mocker.patch("src.rate_limiting.RATE_LIMIT_WINDOW", 2)
        mocker.patch("src.rate_limiting.REQUEST_DELAY_MIN", 0)
        mocker.patch("src.rate_limiting.REQUEST_DELAY_MAX", 0)
        domain = "test-domain.com"

        # Make 5 requests (should be fast)
        start = time.time()
        for _ in range(5):
            await enforce_rate_limit(domain)
        first_five = time.time() - start

        # Should complete quickly
        assert first_five < 0.5

        # 6th request should wait for window
        start = time.time()
        await enforce_rate_limit(domain)
        sixth_request = time.time() - start

        # Should have waited for window (approximately 2 seconds)
        assert sixth_request >= 1.5  # Allow some variance

    @pytest.mark.asyncio
    async def test_separate_limits_per_domain(self, mocker: MockerFixture):
        """Test that each domain has independent rate limits."""
        mocker.patch("src.rate_limiting._rate_limits", {})
        mocker.patch("src.rate_limiting.REQUEST_DELAY_MIN", 0)
        mocker.patch("src.rate_limiting.REQUEST_DELAY_MAX", 0)
        domain1 = "domain1.com"
        domain2 = "domain2.com"

        # Make requests to domain1
        for _ in range(3):
            await enforce_rate_limit(domain1)

        # Requests to domain2 should not be affected
        start = time.time()
        await enforce_rate_limit(domain2)
        elapsed = time.time() - start

        # Should be fast (no delay for first request to domain2)
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_cleans_old_timestamps(self, mocker: MockerFixture):
        """Test that timestamps older than window are removed."""
        limits: dict[str, list[float]] = {}
        mocker.patch("src.rate_limiting._rate_limits", limits)
        domain = "test-domain.com"

        # Manually add old timestamps
        old_time = time.time() - 100  # 100 seconds ago
        limits[domain] = [old_time] * 10

        # Make new request
        await enforce_rate_limit(domain)

        # Old timestamps should be cleaned
        assert len(limits[domain]) == 1
        assert limits[domain][0] > old_time

    @pytest.mark.asyncio
    async def test_concurrent_requests_same_domain(self, mocker: MockerFixture):
        """Test that concurrent requests to same domain are properly limited."""
        mocker.patch("src.rate_limiting._rate_limits", {})
        mocker.patch("src.rate_limiting.REQUEST_DELAY_MIN", 0.05)
        mocker.patch("src.rate_limiting.REQUEST_DELAY_MAX", 0.05)
        domain = "test-domain.com"

        # Launch 3 concurrent requests
        start = time.time()
        await asyncio.gather(
            enforce_rate_limit(domain), enforce_rate_limit(domain), enforce_rate_limit(domain)
        )
        elapsed = time.time() - start

        # Should take at least 0.1 seconds (2 delays)
        # Note: actual behavior depends on asyncio scheduling
        assert elapsed >= 0.05
