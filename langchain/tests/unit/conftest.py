"""Pytest configuration for LangChain unit tests."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama LLM client."""
    client = MagicMock()
    client.ainvoke = AsyncMock()
    client.astream = AsyncMock()
    return client


@pytest.fixture
def mock_mcp_client():
    """Mock FastMCP client."""
    client = MagicMock()
    client.call_tool = AsyncMock()
    client.list_tools = AsyncMock()
    client.connect = AsyncMock()
    client.disconnect = AsyncMock()
    return client


@pytest.fixture
def mock_agent():
    """Mock LangChain agent."""
    agent = MagicMock()
    agent.ainvoke = AsyncMock()
    agent.astream_events = AsyncMock()
    return agent
