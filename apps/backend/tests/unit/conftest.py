"""Pytest configuration for backend unit tests."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def mock_langchain_client():
    """Mock LangChain client for testing."""
    client = MagicMock()
    client.execute_task = AsyncMock()
    client.cancel_task = AsyncMock()
    return client


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    ws = MagicMock()
    ws.send_json = AsyncMock()
    ws.close = AsyncMock()
    ws.accept = AsyncMock()
    return ws


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "question": "What is the capital of France?",
        "seed_url": None,
        "max_depth": 3,
        "max_pages": 20,
        "time_budget": 120,
    }
