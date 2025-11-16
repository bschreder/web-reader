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
