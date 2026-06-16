"""
Configuration module for Backend API.
Loads and validates environment variables.
"""

import os
from datetime import datetime
from pathlib import Path
import sys
from urllib.parse import urlparse

from loguru import logger

# ============================================================================
# Environment Configuration
# ============================================================================


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


# Server configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = _require_env("CORS_ORIGINS").split(",")

# LangChain orchestrator
LANGCHAIN_URL = _require_env("LANGCHAIN_INTERNAL_URL").rstrip("/")
_langchain_parsed = urlparse(LANGCHAIN_URL)
if not _langchain_parsed.hostname or not _langchain_parsed.port:
    raise RuntimeError(
        "LANGCHAIN_INTERNAL_URL must include host and port (e.g., http://langchain:8001)"
    )
LANGCHAIN_HOST = _langchain_parsed.hostname
LANGCHAIN_PORT = _langchain_parsed.port

# Task management
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "3"))
TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", "300"))  # 5 minutes
TASK_DEFAULT_TIME_BUDGET = int(
    os.getenv("TASK_DEFAULT_TIME_BUDGET", os.getenv("TIME_BUDGET", "300"))
)
TASK_MIN_TIME_BUDGET = int(os.getenv("TASK_MIN_TIME_BUDGET", "30"))
TASK_MAX_TIME_BUDGET = int(os.getenv("TASK_MAX_TIME_BUDGET", "600"))
LANGCHAIN_REQUEST_TIMEOUT_BUFFER = float(
    os.getenv("LANGCHAIN_REQUEST_TIMEOUT_BUFFER", "30")
)
ARTIFACT_DIR = Path(os.getenv("ARTIFACT_DIR", "artifacts"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
LOG_TARGET = os.getenv("LOG_TARGET", "both")

# Dynamic JSON log filename: logs/log-backend-YYYYMMDD.json (overridable via LOG_FILE)
_date_str = datetime.now().strftime("%Y%m%d")
LOG_FILE = os.getenv("LOG_FILE", f"logs/log-backend-{_date_str}.json")

# ============================================================================
# Logging Setup
# ============================================================================


def configure_logging():
    """Configure Loguru to log to console and JSON file."""
    # Remove default logger
    logger.remove()

    # Add console handler (human-friendly)
    if LOG_TARGET in ("console", "both"):
        logger.add(
            sys.stderr,
            level=LOG_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True,
        )

    # Add file handler (Json Handler)
    if LOG_TARGET in ("file", "both"):
        logger.add(
            LOG_FILE,
            level=LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="100 MB",
            retention="7 days",
        )

    logger.info(
        f"Backend API configured (log level: {LOG_LEVEL}, target: {LOG_TARGET})"
    )


# Ensure artifact directory exists
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
