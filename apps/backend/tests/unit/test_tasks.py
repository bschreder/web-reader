"""
Tests for task queue management.
"""

import asyncio
import pytest
from datetime import datetime

from src.models import TaskStatus
from src.tasks import (
    Task,
    create_task,
    delete_task,
    execute_task,
    get_active_task_count,
    get_task,
    get_total_task_count,
    list_tasks,
)


# ==================================================================
# Task Class Tests
# ==================================================================


def test_task_creation():
    """Test Task object creation."""
    task = Task(
        task_id="test-123",
        question="What is Python?",
        seed_url="https://python.org",
        max_depth=3,
        max_pages=20,
        time_budget=120,
    )

    assert task.task_id == "test-123"
    assert task.question == "What is Python?"
    assert task.seed_url == "https://python.org"
    assert task.status == TaskStatus.CREATED
    assert task.answer is None
    assert task.citations == []
    assert task.screenshots == []
    assert task.error is None


def test_task_to_dict():
    """Test Task.to_dict() method."""
    task = Task(task_id="test-123", question="What is Python?")
    task_dict = task.to_dict()

    assert task_dict["task_id"] == "test-123"
    assert task_dict["question"] == "What is Python?"
    assert task_dict["status"] == "created"
    assert task_dict["answer"] is None
    assert task_dict["duration"] is None


def test_task_duration():
    """Test Task.duration property."""
    task = Task(task_id="test-123", question="Test")

    # No duration when not started
    assert task.duration is None

    # Set timestamps
    task.started_at = datetime.now()
    assert task.duration is None  # Still None without completed_at

    task.completed_at = datetime.now()
    assert task.duration is not None
    assert isinstance(task.duration, float)
    assert task.duration >= 0


@pytest.mark.asyncio
async def test_task_cancel():
    """Test Task.cancel() method."""
    task = Task(task_id="test-123", question="Test")

    await task.cancel("User requested")

    assert task.status == TaskStatus.CANCELLED
    assert task.error == "User requested"
    assert task.completed_at is not None
    assert task.is_cancelled() is True


@pytest.mark.asyncio
async def test_task_cancel_no_reason():
    """Test Task.cancel() without reason."""
    task = Task(task_id="test-123", question="Test")

    await task.cancel()

    assert task.status == TaskStatus.CANCELLED
    assert task.error == "Cancelled by user"


# ==================================================================
# Task Management Function Tests
# ==================================================================


@pytest.mark.asyncio
async def test_create_task():
    """Test create_task function."""
    task = await create_task(
        question="What is Python?",
        seed_url="https://python.org",
        max_depth=3,
        max_pages=20,
        time_budget=120,
    )

    assert task.task_id is not None
    assert task.question == "What is Python?"
    assert task.seed_url == "https://python.org"
    assert task.status == TaskStatus.CREATED

    # Verify task is in registry
    retrieved_task = await get_task(task.task_id)
    assert retrieved_task is task


@pytest.mark.asyncio
async def test_get_task_not_found():
    """Test get_task with non-existent ID."""
    task = await get_task("non-existent")
    assert task is None


@pytest.mark.asyncio
async def test_list_tasks_empty():
    """Test list_tasks with no tasks."""
    tasks, total = await list_tasks()
    assert tasks == []
    assert total == 0


@pytest.mark.asyncio
async def test_list_tasks():
    """Test list_tasks with multiple tasks."""
    # Create some tasks
    task1 = await create_task(question="Question 1")
    task2 = await create_task(question="Question 2")
    task3 = await create_task(question="Question 3")

    # List all tasks
    tasks, total = await list_tasks()
    assert len(tasks) == 3
    assert total == 3

    # Tasks should be in reverse chronological order
    assert tasks[0].task_id == task3.task_id
    assert tasks[1].task_id == task2.task_id
    assert tasks[2].task_id == task1.task_id


@pytest.mark.asyncio
async def test_list_tasks_pagination():
    """Test list_tasks with pagination."""
    # Create 10 tasks
    for i in range(10):
        await create_task(question=f"Question {i}")

    # Get first page
    tasks, total = await list_tasks(offset=0, limit=5)
    assert len(tasks) == 5
    assert total == 10

    # Get second page
    tasks, total = await list_tasks(offset=5, limit=5)
    assert len(tasks) == 5
    assert total == 10

    # Get beyond available tasks
    tasks, total = await list_tasks(offset=10, limit=5)
    assert len(tasks) == 0
    assert total == 10


@pytest.mark.asyncio
async def test_delete_task():
    """Test delete_task function."""
    task = await create_task(question="Test question")
    task_id = task.task_id

    # Verify task exists
    assert await get_task(task_id) is not None

    # Delete task
    result = await delete_task(task_id)
    assert result is True

    # Verify task is gone
    assert await get_task(task_id) is None


@pytest.mark.asyncio
async def test_delete_task_not_found():
    """Test delete_task with non-existent ID."""
    result = await delete_task("non-existent")
    assert result is False


@pytest.mark.asyncio
async def test_get_task_counts():
    """Test get_active_task_count and get_total_task_count."""
    # Initially empty
    assert await get_active_task_count() == 0
    assert await get_total_task_count() == 0

    # Create some tasks
    await create_task(question="Question 1")
    await create_task(question="Question 2")

    # Check counts
    assert await get_active_task_count() == 0  # Not running yet
    assert await get_total_task_count() == 2


@pytest.mark.asyncio
async def test_execute_task_success():
    """Test execute_task with successful execution."""
    task = await create_task(question="Test question", time_budget=5)

    # Mock executor function
    async def mock_executor(t):
        await asyncio.sleep(0.1)
        t.answer = "Test answer"
        t.status = TaskStatus.COMPLETED

    await execute_task(task, mock_executor)

    assert task.status == TaskStatus.COMPLETED
    assert task.answer == "Test answer"
    assert task.started_at is not None
    assert task.completed_at is not None
    assert task.duration is not None


@pytest.mark.asyncio
async def test_execute_task_timeout():
    """Test execute_task with timeout."""
    task = await create_task(question="Test question", time_budget=1)

    # Mock executor that takes too long
    async def slow_executor(t):
        await asyncio.sleep(10)

    await execute_task(task, slow_executor)

    assert task.status == TaskStatus.FAILED
    assert "time budget" in task.error.lower()


@pytest.mark.asyncio
async def test_execute_task_error():
    """Test execute_task with executor error."""
    task = await create_task(question="Test question")

    # Mock executor that raises error
    async def failing_executor(t):
        raise ValueError("Test error")

    await execute_task(task, failing_executor)

    assert task.status == TaskStatus.FAILED
    assert "Test error" in task.error


@pytest.mark.asyncio
async def test_execute_task_cancellation():
    """Test execute_task with cancellation."""
    task = await create_task(question="Test question")

    # Mock executor that sleeps
    async def slow_executor(t):
        for _ in range(10):
            if t.is_cancelled():
                return
            await asyncio.sleep(0.1)

    # Start execution
    exec_task = asyncio.create_task(execute_task(task, slow_executor))

    # Wait a bit then cancel
    await asyncio.sleep(0.2)
    await task.cancel("User cancelled")

    # Wait for execution to complete
    await exec_task

    assert task.status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_execute_task_concurrency_limit():
    """Test execute_task respects concurrency limit."""
    from src.config import MAX_CONCURRENT_TASKS

    # Create more tasks than the limit
    tasks = []
    for i in range(MAX_CONCURRENT_TASKS + 2):
        task = await create_task(question=f"Question {i}")
        tasks.append(task)

    # Mock executor that sleeps
    async def slow_executor(t):
        t.status = TaskStatus.RUNNING
        await asyncio.sleep(0.5)
        t.answer = "Done"

    # Start all tasks
    exec_tasks = [
        asyncio.create_task(execute_task(task, slow_executor)) for task in tasks
    ]

    # Give them time to queue
    await asyncio.sleep(0.1)

    # Check that at most MAX_CONCURRENT_TASKS are running
    running_count = sum(1 for t in tasks if t.status == TaskStatus.RUNNING)
    assert running_count <= MAX_CONCURRENT_TASKS

    # Wait for all to complete
    await asyncio.gather(*exec_tasks)

    # All should be completed
    assert all(t.status == TaskStatus.COMPLETED for t in tasks)
