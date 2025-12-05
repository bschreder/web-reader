"""Test bootstrap for LangChain tests.

Loads `.env` files early (repo root, `langchain/`, or the test dir) so modules
that read environment variables at import time see test/CI configuration.

This uses `python-dotenv` for robust parsing; falling back to safe defaults
after loading any `.env` entries so tests in the devcontainer can resolve
service hostnames (`ws-ollama`, `fastmcp`).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

from dotenv import load_dotenv
import pytest


# Load .env files early so modules that read env vars at import time see values.
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for candidate in (ROOT / ".env", ROOT / "langchain" / ".env", HERE / ".env"):
    load_dotenv(dotenv_path=str(candidate), override=False)

# Provide sensible defaults for devcontainer/docker-compose test runs when a .env
# file is not present. These will not overwrite env vars explicitly set.
os.environ.setdefault("OLLAMA_HOST", "ws-ollama")
os.environ.setdefault("OLLAMA_PORT", "11434")
os.environ.setdefault("FASTMCP_HOST", "fastmcp")
os.environ.setdefault("FASTMCP_PORT", "3100")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_mcp_client() -> AsyncMock:
    """Mock MCP client for testing."""
    client = AsyncMock()
    client.call_tool = AsyncMock()
    client.health_check = AsyncMock(return_value=True)
    return client


@pytest.fixture
def mock_llm() -> MagicMock:
    """Mock Ollama LLM for testing."""
    llm = MagicMock()
    llm.invoke = AsyncMock(return_value="Test answer from LLM")
    return llm


@pytest.fixture
def sample_navigate_success() -> Dict[str, Any]:
    """Sample successful navigate_to result."""
    return {
        "status": "success",
        "title": "Example Domain",
        "url": "https://example.com",
        "http_status": 200,
    }


@pytest.fixture
def sample_content_success() -> Dict[str, Any]:
    """Sample successful get_page_content result."""
    return {
        "status": "success",
        "title": "Example Domain",
        "url": "https://example.com",
        "text": "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.",
        "truncated": False,
        "links": ["https://www.iana.org/domains/example"],
        "metadata": {},
        "word_count": 28,
    }


@pytest.fixture
def sample_screenshot_success() -> Dict[str, Any]:
    """Sample successful take_screenshot result."""
    return {
        "status": "success",
        "image": "base64_encoded_image_data_here",
        "format": "png",
        "full_page": False,
    }
