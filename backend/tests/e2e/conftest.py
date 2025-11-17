"""Pytest configuration for backend E2E tests."""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for compatibility."""
    return asyncio.get_event_loop_policy()


@pytest.fixture
def api_url() -> str:
    """Get API URL from environment."""
    host = os.getenv("API_HOST", "localhost")
    port = os.getenv("API_PORT", "8000")
    return f"http://{host}:{port}"


@pytest.fixture
def skip_if_no_services():
    """Skip test if required services (LangChain, FastMCP, Ollama) not available."""
    import socket

    # Check LangChain
    langchain_host = os.getenv("LANGCHAIN_HOST", "localhost")
    langchain_port = int(os.getenv("LANGCHAIN_PORT", "8001"))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)

    try:
        result = sock.connect_ex((langchain_host, langchain_port))
        if result != 0:
            pytest.skip(
                f"Required services not available (LangChain at {langchain_host}:{langchain_port})"
            )
    except Exception:
        pytest.skip("Required services not available")
    finally:
        try:
            sock.close()
        except Exception:
            pass
