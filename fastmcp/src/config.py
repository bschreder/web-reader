"""
Configuration module for FastMCP server.
Loads and validates environment variables.
"""

import os
from pathlib import Path
from loguru import logger

# ============================================================================
# Environment Configuration
# ============================================================================

# Playwright connection
PLAYWRIGHT_HOST = os.getenv("PLAYWRIGHT_HOST", "host.docker.internal")
PLAYWRIGHT_PORT = int(os.getenv("PLAYWRIGHT_PORT", "3002"))
BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chromium")

# Rate limiting
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "90"))
REQUEST_DELAY_MIN = int(os.getenv("REQUEST_DELAY_MIN", "10"))
REQUEST_DELAY_MAX = int(os.getenv("REQUEST_DELAY_MAX", "20"))

# Content limits
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "10000"))
MAX_LINKS = int(os.getenv("MAX_LINKS", "50"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
LOG_TARGET = os.getenv("LOG_TARGET", "console")
LOG_FILE = os.getenv("LOG_FILE", "logs/fastmcp.log")

# Robots.txt (future enhancement)
RESPECT_ROBOTS_TXT = os.getenv("RESPECT_ROBOTS_TXT", "true").lower() == "true"

# ============================================================================
# Constants
# ============================================================================

# User agents for deidentification
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# HTTP status codes
HTTP_ERROR_THRESHOLD = 400
HTTP_STATUS_MESSAGES = {
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


def configure_logging():
    """Configure Loguru logger based on environment settings."""
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
