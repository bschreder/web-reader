"""
Task queue management module.
Handles task lifecycle, concurrency limits, and state management.
"""

import asyncio
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional

from loguru import logger

from .config import MAX_CONCURRENT_TASKS, TASK_TIMEOUT
from .models import TaskStatus

# ============================================================================
# Global State
# ============================================================================

_tasks: dict[str, "Task"] = {}
_running_tasks: set[str] = set()
_task_lock = asyncio.Lock()

# ============================================================================
# Task Class
# ============================================================================


class Task:
    """
    Represents a research task with lifecycle management.
    """

    def __init__(
        self,
        task_id: str,
        question: str,
        seed_url: Optional[str] = None,
        max_depth: int = 3,
        max_pages: int = 20,
        time_budget: int = 120,
        search_engine: str = "duckduckgo",
        max_results: int = 10,
        safe_mode: bool = True,
        same_domain_only: bool = False,
        allow_external_links: bool = True,
    ):
        self.task_id = task_id
        self.question = question
        self.seed_url = seed_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.time_budget = time_budget
        self.search_engine = search_engine
        self.max_results = max_results
        self.safe_mode = safe_mode
        self.same_domain_only = same_domain_only
        self.allow_external_links = allow_external_links

        self.status = TaskStatus.CREATED
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        self.answer: Optional[str] = None
        self.citations: list[dict[str, Any]] = []
        self.screenshots: list[str] = []
        self.error: Optional[str] = None
        self.metadata: dict[str, Any] = {}

        self._cancel_event = asyncio.Event()
        self._executor_task: Optional[asyncio.Task] = None

    @property
    def duration(self) -> Optional[float]:
        """Calculate task duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary for API response."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "question": self.question,
            "seed_url": self.seed_url,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "duration": self.duration,
            "answer": self.answer,
            "citations": self.citations,
            "screenshots": self.screenshots,
            "error": self.error,
            "metadata": self.metadata,
            "search_engine": getattr(self, "search_engine", "duckduckgo"),
            "max_results": getattr(self, "max_results", 10),
            "safe_mode": getattr(self, "safe_mode", True),
            "same_domain_only": getattr(self, "same_domain_only", False),
            "allow_external_links": getattr(self, "allow_external_links", True),
        }

    async def cancel(self, reason: Optional[str] = None):
        """Cancel the task."""
        logger.info(f"Cancelling task {self.task_id}: {reason or 'user requested'}")
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
        self.error = reason or "Cancelled by user"
        self._cancel_event.set()

        if self._executor_task and not self._executor_task.done():
            self._executor_task.cancel()

    def is_cancelled(self) -> bool:
        """Check if task has been cancelled."""
        return self._cancel_event.is_set()


# ============================================================================
# Task Management Functions
# ============================================================================


async def create_task(
    question: str,
    seed_url: Optional[str] = None,
    max_depth: int = 3,
    max_pages: int = 20,
    time_budget: int = 120,
    search_engine: str = "duckduckgo",
    max_results: int = 10,
    safe_mode: bool = True,
    same_domain_only: bool = False,
    allow_external_links: bool = True,
) -> Task:
    """
    Create a new task and add it to the queue.

    Args:
        question: Research question
        seed_url: Optional starting URL
        max_depth: Maximum link depth
        max_pages: Maximum pages to visit
        time_budget: Time budget in seconds
        search_engine: Search engine to use
        max_results: Max search results to examine
        safe_mode: Filter unsafe content
        same_domain_only: Only follow same-domain links
        allow_external_links: Allow external links

    Returns:
        Created task
    """
    task_id = str(uuid.uuid4())
    task = Task(
        task_id,
        question,
        seed_url,
        max_depth,
        max_pages,
        time_budget,
        search_engine,
        max_results,
        safe_mode,
        same_domain_only,
        allow_external_links,
    )

    async with _task_lock:
        _tasks[task_id] = task
        logger.info(f"Created task {task_id}: {question[:50]}...")

    return task


async def get_task(task_id: str) -> Optional[Task]:
    """Get task by ID."""
    return _tasks.get(task_id)


async def list_tasks(offset: int = 0, limit: int = 100) -> tuple[list[Task], int]:
    """
    List all tasks with pagination.

    Args:
        offset: Number of tasks to skip
        limit: Maximum number of tasks to return

    Returns:
        Tuple of (tasks, total_count)
    """
    all_tasks = sorted(_tasks.values(), key=lambda t: t.created_at, reverse=True)
    total = len(all_tasks)
    tasks = all_tasks[offset : offset + limit]
    return tasks, total


async def delete_task(task_id: str) -> bool:
    """
    Delete a task.

    Args:
        task_id: Task ID to delete

    Returns:
        True if task was deleted, False if not found
    """
    async with _task_lock:
        if task_id in _tasks:
            task = _tasks[task_id]

            # Cancel if running
            if task.status in (TaskStatus.QUEUED, TaskStatus.RUNNING):
                await task.cancel("Task deleted")

            del _tasks[task_id]
            _running_tasks.discard(task_id)
            logger.info(f"Deleted task {task_id}")
            return True

    return False


async def can_start_task() -> bool:
    """Check if a new task can be started (within concurrency limit)."""
    return len(_running_tasks) < MAX_CONCURRENT_TASKS


async def execute_task(task: Task, executor: Callable):
    """
    Execute a task with the provided executor function.

    Args:
        task: Task to execute
        executor: Async function that executes the task
    """
    if not await can_start_task():
        task.status = TaskStatus.QUEUED
        logger.info(f"Task {task.task_id} queued (at capacity)")
        # Wait for slot to open
        while not await can_start_task():
            await asyncio.sleep(1)
            if task.is_cancelled():
                return

    # Start execution
    async with _task_lock:
        _running_tasks.add(task.task_id)

    task.status = TaskStatus.RUNNING
    task.started_at = datetime.now()
    logger.info(f"Task {task.task_id} started")

    try:
        # Execute with timeout
        async with asyncio.timeout(task.time_budget or TASK_TIMEOUT):
            await executor(task)

        if not task.is_cancelled():
            task.status = TaskStatus.COMPLETED
            logger.info(f"Task {task.task_id} completed successfully")

    except asyncio.TimeoutError:
        task.status = TaskStatus.FAILED
        task.error = f"Task exceeded time budget ({task.time_budget}s)"
        logger.error(f"Task {task.task_id} timed out")

    except asyncio.CancelledError:
        logger.info(f"Task {task.task_id} was cancelled")
        # Status already set by cancel()

    except Exception as e:
        task.status = TaskStatus.FAILED
        task.error = str(e)
        logger.error(f"Task {task.task_id} failed: {e}", exc_info=True)

    finally:
        task.completed_at = datetime.now()
        async with _task_lock:
            _running_tasks.discard(task.task_id)


async def get_active_task_count() -> int:
    """Get number of currently running tasks."""
    return len(_running_tasks)


async def get_total_task_count() -> int:
    """Get total number of tasks."""
    return len(_tasks)
