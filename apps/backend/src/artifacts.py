"""
Artifact persistence module.
Handles storing and retrieving task artifacts (results, screenshots, logs).
"""

import json
import shutil
from pathlib import Path
from typing import Any, Optional

import aiofiles
from loguru import logger

from .config import ARTIFACT_DIR

# ============================================================================
# Artifact Management
# ============================================================================


def get_task_dir(task_id: str) -> Path:
    """Get artifact directory for a task."""
    task_dir = ARTIFACT_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    return task_dir


def get_screenshot_dir(task_id: str) -> Path:
    """Get screenshot directory for a task."""
    screenshot_dir = get_task_dir(task_id) / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    return screenshot_dir


async def save_task_result(task_id: str, data: dict[str, Any]) -> None:
    """
    Save task result to disk.

    Args:
        task_id: Task ID
        data: Task data dictionary
    """
    try:
        task_dir = get_task_dir(task_id)
        task_file = task_dir / "task.json"

        async with aiofiles.open(task_file, "w") as f:
            await f.write(json.dumps(data, indent=2))

        logger.debug(f"Saved task result for {task_id}")

    except Exception as e:
        logger.error(f"Failed to save task result for {task_id}: {e}")
        raise


async def load_task_result(task_id: str) -> Optional[dict[str, Any]]:
    """
    Load task result from disk.

    Args:
        task_id: Task ID

    Returns:
        Task data dictionary or None if not found
    """
    try:
        task_dir = get_task_dir(task_id)
        task_file = task_dir / "task.json"

        if not task_file.exists():
            return None

        async with aiofiles.open(task_file, "r") as f:
            content = await f.read()
            return json.loads(content)

    except Exception as e:
        logger.error(f"Failed to load task result for {task_id}: {e}")
        return None


async def save_screenshot(task_id: str, step: int, image_data: bytes) -> str:
    """
    Save screenshot to disk.

    Args:
        task_id: Task ID
        step: Step number
        image_data: PNG image bytes

    Returns:
        Relative path to screenshot
    """
    try:
        screenshot_dir = get_screenshot_dir(task_id)
        filename = f"step_{step}.png"
        filepath = screenshot_dir / filename

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(image_data)

        # Return relative path for API response
        relative_path = f"artifacts/{task_id}/screenshots/{filename}"
        logger.debug(f"Saved screenshot for {task_id}: {filename}")
        return relative_path

    except Exception as e:
        logger.error(f"Failed to save screenshot for {task_id}: {e}")
        raise


async def save_logs(task_id: str, logs: str) -> None:
    """
    Save task logs to disk.

    Args:
        task_id: Task ID
        logs: Log content
    """
    try:
        task_dir = get_task_dir(task_id)
        log_file = task_dir / "logs.txt"

        async with aiofiles.open(log_file, "w") as f:
            await f.write(logs)

        logger.debug(f"Saved logs for {task_id}")

    except Exception as e:
        logger.error(f"Failed to save logs for {task_id}: {e}")
        raise


async def save_sources(task_id: str, sources: list[dict[str, Any]]) -> None:
    """
    Save visited sources/citations to disk.

    Args:
        task_id: Task ID
        sources: List of source dictionaries
    """
    try:
        task_dir = get_task_dir(task_id)
        sources_file = task_dir / "sources.json"

        async with aiofiles.open(sources_file, "w") as f:
            await f.write(json.dumps(sources, indent=2))

        logger.debug(f"Saved sources for {task_id}")

    except Exception as e:
        logger.error(f"Failed to save sources for {task_id}: {e}")
        raise


async def delete_task_artifacts(task_id: str) -> bool:
    """
    Delete all artifacts for a task.

    Args:
        task_id: Task ID

    Returns:
        True if artifacts were deleted, False if not found
    """
    try:
        task_dir = get_task_dir(task_id)

        if task_dir.exists():
            shutil.rmtree(task_dir)
            logger.info(f"Deleted artifacts for task {task_id}")
            return True

        return False

    except Exception as e:
        logger.error(f"Failed to delete artifacts for {task_id}: {e}")
        return False


def get_screenshot_path(task_id: str, filename: str) -> Optional[Path]:
    """
    Get full path to a screenshot file.

    Args:
        task_id: Task ID
        filename: Screenshot filename

    Returns:
        Path object or None if not found
    """
    screenshot_dir = get_screenshot_dir(task_id)
    filepath = screenshot_dir / filename

    if filepath.exists() and filepath.is_file():
        return filepath

    return None


async def get_artifact_stats(task_id: str) -> dict[str, Any]:
    """
    Get statistics about task artifacts.

    Args:
        task_id: Task ID

    Returns:
        Dictionary with artifact statistics
    """
    task_dir = get_task_dir(task_id)

    if not task_dir.exists():
        return {"exists": False}

    screenshot_dir = get_screenshot_dir(task_id)
    screenshots = list(screenshot_dir.glob("*.png")) if screenshot_dir.exists() else []

    total_size = sum(f.stat().st_size for f in task_dir.rglob("*") if f.is_file())

    return {
        "exists": True,
        "total_size_bytes": total_size,
        "screenshot_count": len(screenshots),
        "has_logs": (task_dir / "logs.txt").exists(),
        "has_sources": (task_dir / "sources.json").exists(),
        "has_result": (task_dir / "task.json").exists(),
    }
