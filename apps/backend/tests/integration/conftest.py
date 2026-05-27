"""Pytest configuration for backend integration tests."""

import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="session")
def langchain_url() -> str:
    """Get LangChain service URL from environment."""
    host = os.getenv("LANGCHAIN_HOST", "langchain")
    port = os.getenv("LANGCHAIN_PORT", "8001")
    return f"http://{host}:{port}"


@pytest.fixture
def skip_if_no_langchain(langchain_url: str):
    """Skip test if LangChain service not available."""
    import socket

    # Parse host and port from URL
    host = langchain_url.split("://")[1].split(":")[0]
    port = int(langchain_url.split(":")[-1])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()

    if result != 0:
        pytest.skip(f"LangChain not available at {langchain_url}")
