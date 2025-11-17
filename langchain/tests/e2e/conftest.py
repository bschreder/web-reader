"""Pytest configuration for LangChain E2E tests."""

import asyncio
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for compatibility."""
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="session")
def test_questions() -> dict[str, str]:
    """Provide test questions for E2E testing."""
    return {
        "simple": "What is the capital of France?",
        "factual": "When was the Eiffel Tower built?",
        "comparison": "What is the difference between HTTP and HTTPS?",
        "multi_page": "What are the main features of Python programming language?",
    }


@pytest.fixture
def test_question_simple():
    """Simple test question."""
    return "What is 2+2?"


@pytest.fixture
def test_question_with_url():
    """Test question intended for use with seed URL."""
    return "What information is on this website?"


@pytest.fixture
def fastmcp_url() -> str:
    """Get FastMCP service URL."""
    import os

    host = os.getenv("FASTMCP_HOST", "fastmcp")
    port = os.getenv("FASTMCP_PORT", "3000")
    return f"http://{host}:{port}"


@pytest.fixture
def skip_if_no_services():
    """Skip test if required services not available."""
    import socket
    import os

    # Check FastMCP
    fastmcp_host = os.getenv("FASTMCP_HOST", "fastmcp")
    fastmcp_port = int(os.getenv("FASTMCP_PORT", "3000"))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)

    try:
        result = sock.connect_ex((fastmcp_host, fastmcp_port))
        if result != 0:
            pytest.skip(
                f"Required services not available (FastMCP at {fastmcp_host}:{fastmcp_port})"
            )
    except Exception:
        pytest.skip("Required services not available")
    finally:
        try:
            sock.close()
        except Exception:
            pass
