"""
Tests for Pydantic data models.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.models import (
    Citation,
    CompleteEvent,
    ErrorEvent,
    EventType,
    HealthResponse,
    ScreenshotEvent,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskStatus,
    ThinkingEvent,
    ToolCallEvent,
    ToolResultEvent,
)


# ==================================================================
# TaskCreate Tests
# ==================================================================


def test_task_create_valid():
    """Test valid TaskCreate model."""
    task = TaskCreate(question="What is Python?")
    assert task.question == "What is Python?"
    assert task.seed_url is None
    assert task.max_depth == 3
    assert task.max_pages == 20
    assert task.time_budget == 120


def test_task_create_with_all_fields():
    """Test TaskCreate with all fields."""
    task = TaskCreate(
        question="What is Python?",
        seed_url="https://python.org",
        max_depth=5,
        max_pages=50,
        time_budget=300,
    )
    assert task.question == "What is Python?"
    assert task.seed_url == "https://python.org"
    assert task.max_depth == 5
    assert task.max_pages == 50
    assert task.time_budget == 300


def test_task_create_empty_question():
    """Test TaskCreate with empty question fails."""
    with pytest.raises(ValidationError):
        TaskCreate(question="")


def test_task_create_question_too_long():
    """Test TaskCreate with question > 1000 chars fails."""
    with pytest.raises(ValidationError):
        TaskCreate(question="x" * 1001)


def test_task_create_invalid_max_depth():
    """Test TaskCreate with invalid max_depth fails."""
    with pytest.raises(ValidationError):
        TaskCreate(question="Test", max_depth=0)

    with pytest.raises(ValidationError):
        TaskCreate(question="Test", max_depth=10)


def test_task_create_invalid_time_budget():
    """Test TaskCreate with invalid time_budget fails."""
    with pytest.raises(ValidationError):
        TaskCreate(question="Test", time_budget=10)

    with pytest.raises(ValidationError):
        TaskCreate(question="Test", time_budget=1000)


# ==================================================================
# TaskResponse Tests
# ==================================================================


def test_task_response():
    """Test TaskResponse model."""
    now = datetime.now(timezone.utc)
    response = TaskResponse(
        task_id="test-123",
        status=TaskStatus.COMPLETED,
        question="What is Python?",
        created_at=now,
    )
    assert response.task_id == "test-123"
    assert response.status == TaskStatus.COMPLETED
    assert response.question == "What is Python?"
    assert response.answer is None
    assert response.citations == []
    assert response.screenshots == []


def test_task_response_with_results():
    """Test TaskResponse with answer and citations."""
    now = datetime.now(timezone.utc)
    citation = Citation(url="https://python.org", title="Python.org")
    response = TaskResponse(
        task_id="test-123",
        status=TaskStatus.COMPLETED,
        question="What is Python?",
        created_at=now,
        answer="Python is a programming language.",
        citations=[citation],
        screenshots=["/artifacts/test-123/screenshots/step_1.png"],
        duration=45.5,
    )
    assert response.answer == "Python is a programming language."
    assert len(response.citations) == 1
    assert response.citations[0].url == "https://python.org"
    assert len(response.screenshots) == 1
    assert response.duration == 45.5


# ==================================================================
# Citation Tests
# ==================================================================


def test_citation_minimal():
    """Test Citation with required fields only."""
    citation = Citation(url="https://example.com", title="Example")
    assert citation.url == "https://example.com"
    assert citation.title == "Example"
    assert citation.excerpt is None


def test_citation_with_excerpt():
    """Test Citation with excerpt."""
    citation = Citation(
        url="https://example.com",
        title="Example",
        excerpt="This is an example excerpt.",
    )
    assert citation.excerpt == "This is an example excerpt."


# ==================================================================
# TaskListResponse Tests
# ==================================================================


def test_task_list_response_empty():
    """Test TaskListResponse with empty list."""
    response = TaskListResponse(tasks=[], total=0, offset=0, limit=100)
    assert response.tasks == []
    assert response.total == 0
    assert response.offset == 0
    assert response.limit == 100


def test_task_list_response_with_tasks():
    """Test TaskListResponse with tasks."""
    now = datetime.now(timezone.utc)
    task1 = TaskResponse(
        task_id="test-1",
        status=TaskStatus.COMPLETED,
        question="Question 1",
        created_at=now,
    )
    task2 = TaskResponse(
        task_id="test-2",
        status=TaskStatus.RUNNING,
        question="Question 2",
        created_at=now,
    )
    response = TaskListResponse(tasks=[task1, task2], total=2, offset=0, limit=100)
    assert len(response.tasks) == 2
    assert response.total == 2


# ==================================================================
# HealthResponse Tests
# ==================================================================


def test_health_response():
    """Test HealthResponse model."""
    response = HealthResponse(
        langchain_connected=True,
        active_tasks=5,
        total_tasks=100,
    )
    assert response.status == "healthy"
    assert response.version == "0.1.0"
    assert response.langchain_connected is True
    assert response.active_tasks == 5
    assert response.total_tasks == 100


# ==================================================================
# WebSocket Event Tests
# ==================================================================


def test_thinking_event():
    """Test ThinkingEvent model."""
    event = ThinkingEvent(
        task_id="test-123",
        content="I should search for Python documentation...",
    )
    assert event.type == EventType.THINKING
    assert event.task_id == "test-123"
    assert event.content == "I should search for Python documentation..."
    assert isinstance(event.timestamp, datetime)


def test_tool_call_event():
    """Test ToolCallEvent model."""
    event = ToolCallEvent(
        task_id="test-123",
        tool="navigate_to",
        args={"url": "https://python.org"},
    )
    assert event.type == EventType.TOOL_CALL
    assert event.tool == "navigate_to"
    assert event.args == {"url": "https://python.org"}


def test_tool_result_event():
    """Test ToolResultEvent model."""
    event = ToolResultEvent(
        task_id="test-123",
        tool="navigate_to",
        result={"status": "success", "title": "Python.org"},
        success=True,
    )
    assert event.type == EventType.TOOL_RESULT
    assert event.success is True


def test_screenshot_event():
    """Test ScreenshotEvent model."""
    event = ScreenshotEvent(
        task_id="test-123",
        image_url="/artifacts/test-123/screenshots/step_1.png",
        full_page=True,
    )
    assert event.type == EventType.SCREENSHOT
    assert event.image_url == "/artifacts/test-123/screenshots/step_1.png"
    assert event.full_page is True


def test_complete_event():
    """Test CompleteEvent model."""
    citation = Citation(url="https://python.org", title="Python.org")
    event = CompleteEvent(
        task_id="test-123",
        answer="Python is a programming language.",
        citations=[citation],
        duration=45.5,
    )
    assert event.type == EventType.COMPLETE
    assert event.answer == "Python is a programming language."
    assert len(event.citations) == 1
    assert event.duration == 45.5


def test_error_event():
    """Test ErrorEvent model."""
    event = ErrorEvent(
        task_id="test-123",
        error="Navigation failed: timeout",
        recoverable=True,
    )
    assert event.type == EventType.ERROR
    assert event.error == "Navigation failed: timeout"
    assert event.recoverable is True


# ==================================================================
# TaskStatus Enum Tests
# ==================================================================


def test_task_status_values():
    """Test TaskStatus enum values."""
    assert TaskStatus.CREATED.value == "created"
    assert TaskStatus.QUEUED.value == "queued"
    assert TaskStatus.RUNNING.value == "running"
    assert TaskStatus.COMPLETED.value == "completed"
    assert TaskStatus.FAILED.value == "failed"
    assert TaskStatus.CANCELLED.value == "cancelled"
