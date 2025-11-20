"""
Configuration module.
Loads environment variables and provides application settings.
"""

import os
from pathlib import Path

# ============================================================================
# Service Configuration
# ============================================================================

SERVICE_HOST = os.getenv("LANGCHAIN_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("LANGCHAIN_PORT", "8001"))

# ============================================================================
# FastMCP Configuration
# ============================================================================

FASTMCP_HOST = os.getenv("FASTMCP_HOST", "localhost")
# Default FastMCP MCP server port is 3100 (compose default)
FASTMCP_PORT = int(os.getenv("FASTMCP_PORT", "3100"))
FASTMCP_HEALTH_PORT = int(os.getenv("FASTMCP_HEALTH_PORT", "3101"))
FASTMCP_URL = f"http://{FASTMCP_HOST}:{FASTMCP_PORT}"

# ============================================================================
# Ollama Configuration
# ============================================================================

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
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
LOG_TARGET = os.getenv("LOG_TARGET", "console").lower()
LOG_FILE = os.getenv("LOG_FILE", "logs/langchain.log")

# ============================================================================
# Directory Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
