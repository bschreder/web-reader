"""Pytest configuration for LangChain integration tests."""

import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="session")
def ollama_url() -> str:
    """Get Ollama service URL from environment."""
    host = os.getenv("OLLAMA_HOST", "ollama")
    port = os.getenv("OLLAMA_PORT", "11434")
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def fastmcp_url() -> str:
    """Get FastMCP service URL from environment.

    Defaults align with docker-compose: MCP on 3100, container name 'web-reader-fastmcp'.
    """
    # Use the short container hostname by default so tests run inside the
    # devcontainer can resolve the service as `fastmcp` on the Docker
    # bridge network.
    host = os.getenv("FASTMCP_HOST", "fastmcp")
    port = os.getenv("FASTMCP_PORT", "3100")
    return f"http://{host}:{port}"


@pytest.fixture
def skip_if_no_ollama(ollama_url: str):
    """Fail test if Ollama service not available."""
    import socket

    host = ollama_url.split("://")[1].split(":")[0]
    port = int(ollama_url.split(":")[-1])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()

    if result != 0:
        pytest.fail(f"Ollama not available at {ollama_url}")


@pytest.fixture
def skip_if_no_fastmcp(fastmcp_url: str):
    """Fail test if FastMCP service not available."""
    import socket

    host = fastmcp_url.split("://")[1].split(":")[0]
    port = int(fastmcp_url.split(":")[-1])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()

    if result != 0:
        pytest.fail(f"FastMCP not available at {fastmcp_url}")
