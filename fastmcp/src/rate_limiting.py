"""
Rate limiting module.
Enforces request limits per domain to avoid overwhelming servers.
"""

import asyncio
import random
import time
from loguru import logger

from .config import (
    ENABLE_RATE_LIMITING,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    REQUEST_DELAY_MIN,
    REQUEST_DELAY_MAX,
)

# ============================================================================
# Global State
# ============================================================================

_rate_limits: dict[str, list[float]] = {}

# ============================================================================
# Rate Limiting
# ============================================================================


async def enforce_rate_limit(domain: str) -> None:
    """
    Enforce rate limiting: max N requests per window per domain.
    Adds randomized delay between requests.

    Args:
        domain: Domain to rate limit
    """
    if not ENABLE_RATE_LIMITING:
        return

    now = time.time()

    # Clean old timestamps (>window ago)
    if domain in _rate_limits:
        _rate_limits[domain] = [t for t in _rate_limits[domain] if now - t < RATE_LIMIT_WINDOW]
    else:
        _rate_limits[domain] = []

    # Check rate limit
    if len(_rate_limits[domain]) >= RATE_LIMIT_REQUESTS:
        oldest = _rate_limits[domain][0]
        wait_time = RATE_LIMIT_WINDOW - (now - oldest)
        if wait_time > 0:
            logger.warning(f"Rate limit reached for {domain}, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            now = time.time()
            _rate_limits[domain] = []

    # Random delay (between min/max) if not first request
    if _rate_limits[domain]:
        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        logger.debug(f"Rate limit delay: {delay:.1f}s for {domain}")
        await asyncio.sleep(delay)

    # Record this request
    _rate_limits[domain].append(time.time())


def reset_rate_limits():
    """Reset all rate limit state (useful for testing)."""
    global _rate_limits
    _rate_limits = {}
