"""
Pytest configuration and shared fixtures for backend tests.
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator
import sys

import pytest
from httpx import AsyncClient

# Ensure the backend package root is on sys.path so `import src` works
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import ARTIFACT_DIR


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_artifact_dir(tmp_path: Path) -> Path:
    """Create a temporary artifact directory for tests."""
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    from server import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_langchain_client(mocker):
    """Mock LangChain client for testing."""
    mock = mocker.AsyncMock()
    mock.health_check.return_value = True
    mock.execute_task.return_value = {
        "answer": "Test answer",
        "citations": [
            {"url": "https://example.com", "title": "Example", "excerpt": "Test"}
        ],
        "screenshots": [],
        "metadata": {},
    }
    return mock


@pytest.fixture(autouse=True)
async def cleanup_tasks():
    """Clean up tasks between tests."""
    yield
    # Import here to avoid circular imports
    from src.tasks import _tasks, _running_tasks

    _tasks.clear()
    _running_tasks.clear()


@pytest.fixture(autouse=True)
async def cleanup_artifacts(test_artifact_dir):
    """Clean up artifacts between tests."""
    yield
    # Clean up after test
    import shutil

    if test_artifact_dir.exists():
        shutil.rmtree(test_artifact_dir)
