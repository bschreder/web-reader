"""
Configuration module for FastMCP server.
Loads and validates environment variables.
"""

import os
from pathlib import Path
from typing import Final

from loguru import logger

# ============================================================================
# Environment Configuration
# ============================================================================

# Playwright connection
PLAYWRIGHT_HOST: Final[str] = os.getenv("PLAYWRIGHT_HOST", "host.docker.internal")
PLAYWRIGHT_PORT: Final[int] = int(os.getenv("PLAYWRIGHT_PORT", "3002"))
BROWSER_TYPE: Final[str] = os.getenv("BROWSER_TYPE", "chromium")

# Rate limiting
ENABLE_RATE_LIMITING: Final[bool] = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
RATE_LIMIT_REQUESTS: Final[int] = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
RATE_LIMIT_WINDOW: Final[int] = int(os.getenv("RATE_LIMIT_WINDOW", "90"))
REQUEST_DELAY_MIN: Final[int] = int(os.getenv("REQUEST_DELAY_MIN", "10"))
REQUEST_DELAY_MAX: Final[int] = int(os.getenv("REQUEST_DELAY_MAX", "20"))

# Content limits
MAX_TEXT_CHARS: Final[int] = int(os.getenv("MAX_TEXT_CHARS", "10000"))
MAX_LINKS: Final[int] = int(os.getenv("MAX_LINKS", "50"))

# Logging
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "info").upper()
LOG_TARGET: Final[str] = os.getenv("LOG_TARGET", "console")
LOG_FILE: Final[str] = os.getenv("LOG_FILE", "logs/fastmcp.log")

# Robots.txt (future enhancement)
RESPECT_ROBOTS_TXT: Final[bool] = os.getenv("RESPECT_ROBOTS_TXT", "true").lower() == "true"

# ============================================================================
# Constants
# ============================================================================

# User agents for deidentification
USER_AGENTS: Final[list[str]] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# HTTP status codes
HTTP_ERROR_THRESHOLD: Final[int] = 400
HTTP_STATUS_MESSAGES: Final[dict[int, str]] = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
}

# ============================================================================
# Logging Setup
# ============================================================================


def configure_logging():  # pragma: no cover
    """Configure Loguru logger based on environment settings.

    Note: Logging setup is excluded from coverage as behavior is environment-driven.
    """
    logger.remove()  # Remove default handler

    if LOG_TARGET in ("console", "both"):
        logger.add(
            lambda msg: print(msg, end=""),
            colorize=True,
            level=LOG_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        )

    if LOG_TARGET in ("file", "both"):
        Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            LOG_FILE,
            rotation="10 MB",
            retention="14 days",
            compression="zip",
            level=LOG_LEVEL,
            serialize=True,
        )

    logger.info(f"FastMCP server configured (log level: {LOG_LEVEL}, target: {LOG_TARGET})")
