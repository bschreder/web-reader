"""
Configuration module for Backend API.
Loads and validates environment variables.
"""

import os
from pathlib import Path

from loguru import logger

# ============================================================================
# Environment Configuration
# ============================================================================

# Server configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# LangChain orchestrator
LANGCHAIN_HOST = os.getenv("LANGCHAIN_HOST", "localhost")
LANGCHAIN_PORT = int(os.getenv("LANGCHAIN_PORT", "8001"))
LANGCHAIN_URL = f"http://{LANGCHAIN_HOST}:{LANGCHAIN_PORT}"

# Task management
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "3"))
TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", "300"))  # 5 minutes
ARTIFACT_DIR = Path(os.getenv("ARTIFACT_DIR", "artifacts"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
LOG_TARGET = os.getenv("LOG_TARGET", "console")
LOG_FILE = os.getenv("LOG_FILE", "logs/backend.log")

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

    logger.info(
        f"Backend API configured (log level: {LOG_LEVEL}, target: {LOG_TARGET})"
    )


# Ensure artifact directory exists
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
