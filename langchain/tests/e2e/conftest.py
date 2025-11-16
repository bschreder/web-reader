"""Pytest configuration for LangChain E2E tests."""

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


@pytest.fixture(scope="session")
def test_questions() -> dict[str, str]:
    """Provide test questions for E2E testing."""
    return {
        "simple": "What is the capital of France?",
        "factual": "When was the Eiffel Tower built?",
        "comparison": "What is the difference between HTTP and HTTPS?",
        "multi_page": "What are the main features of Python programming language?",
    }
