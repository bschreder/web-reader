"""
Configuration module.
Loads environment variables and provides application settings.
"""

import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# ============================================================================
# Service Configuration
# ============================================================================


def _require_env(name: str) -> str:
	value = os.getenv(name)
	if value is None or value.strip() == "":
		raise RuntimeError(f"Missing required environment variable: {name}")
	return value.strip()

SERVICE_HOST = os.getenv("LANGCHAIN_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("LANGCHAIN_PORT", "8001"))

# ============================================================================
# FastMCP Configuration
# ============================================================================

FASTMCP_URL = _require_env("FASTMCP_INTERNAL_URL").rstrip("/")
_fastmcp_parsed = urlparse(FASTMCP_URL)
if not _fastmcp_parsed.hostname or not _fastmcp_parsed.port:
	raise RuntimeError("FASTMCP_INTERNAL_URL must include host and port (e.g., http://fastmcp:3100/mcp)")
FASTMCP_HOST = _fastmcp_parsed.hostname
FASTMCP_PORT = _fastmcp_parsed.port
FASTMCP_HEALTH_PORT = int(os.getenv("FASTMCP_HEALTH_PORT", "3101"))

# ============================================================================
# Ollama Configuration
# ============================================================================

OLLAMA_BASE_URL = _require_env("OLLAMA_BASE_URL").rstrip("/")
_ollama_parsed = urlparse(OLLAMA_BASE_URL)
if not _ollama_parsed.hostname or not _ollama_parsed.port:
	raise RuntimeError("OLLAMA_BASE_URL must include host and port (e.g., http://ollama:11434)")
OLLAMA_HOST = _ollama_parsed.hostname
OLLAMA_PORT = _ollama_parsed.port
# Default model aligned with infrastructure docker-compose
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")

# ============================================================================
# Agent Configuration
# ============================================================================

MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "15"))
MAX_EXECUTION_TIME = int(os.getenv("AGENT_MAX_EXECUTION_TIME", "300"))
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.0"))
AGENT_VERBOSE = os.getenv("AGENT_VERBOSE", "true").lower() == "true"

# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
# Default to logging to both console and file
LOG_TARGET = os.getenv("LOG_TARGET", "both").lower()

# Dynamic JSON log filename: logs/log-langchain-YYYYMMDD.json
_date_str = datetime.now().strftime("%Y%m%d")
LOG_FILE = os.getenv("LOG_FILE", f"logs/log-langchain-{_date_str}.json")

# ============================================================================
# Directory Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
