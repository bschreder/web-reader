"""
Tests for artifact persistence.
"""

import json
import pytest

from src.artifacts import (
    delete_task_artifacts,
    get_artifact_stats,
    get_screenshot_path,
    get_task_dir,
    save_logs,
    save_screenshot,
    save_sources,
    save_task_result,
    load_task_result,
)


@pytest.mark.asyncio
async def test_get_task_dir(test_artifact_dir, monkeypatch):
    """Test get_task_dir creates directory."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    task_id = "test-123"
    task_dir = get_task_dir(task_id)

    assert task_dir.exists()
    assert task_dir.is_dir()
    assert task_dir.name == task_id


@pytest.mark.asyncio
async def test_save_and_load_task_result(test_artifact_dir, monkeypatch):
    """Test saving and loading task result."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    task_id = "test-123"
    task_data = {
        "task_id": task_id,
        "question": "What is Python?",
        "answer": "Python is a programming language.",
        "status": "completed",
    }

    # Save result
    await save_task_result(task_id, task_data)

    # Load result
    loaded_data = await load_task_result(task_id)

    assert loaded_data is not None
    assert loaded_data["task_id"] == task_id
    assert loaded_data["question"] == "What is Python?"
    assert loaded_data["answer"] == "Python is a programming language."


@pytest.mark.asyncio
async def test_load_task_result_not_found(test_artifact_dir, monkeypatch):
    """Test loading non-existent task result."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    result = await load_task_result("non-existent")
    assert result is None


@pytest.mark.asyncio
async def test_save_screenshot(test_artifact_dir, monkeypatch):
    """Test saving screenshot."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    task_id = "test-123"
    step = 1
    image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"  # Fake PNG header

    # Save screenshot
    relative_path = await save_screenshot(task_id, step, image_data)

    assert "test-123" in relative_path
    assert "step_1.png" in relative_path

    # Verify file exists
    screenshot_dir = get_task_dir(task_id) / "screenshots"
    screenshot_file = screenshot_dir / "step_1.png"
    assert screenshot_file.exists()

    # Verify content
    with open(screenshot_file, "rb") as f:
        content = f.read()
    assert content == image_data


@pytest.mark.asyncio
async def test_save_logs(test_artifact_dir, monkeypatch):
    """Test saving logs."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    task_id = "test-123"
    logs = "Log line 1\nLog line 2\nLog line 3"

    # Save logs
    await save_logs(task_id, logs)

    # Verify file exists
    task_dir = get_task_dir(task_id)
    log_file = task_dir / "logs.txt"
    assert log_file.exists()

    # Verify content
    with open(log_file, "r") as f:
        content = f.read()
    assert content == logs


@pytest.mark.asyncio
async def test_save_sources(test_artifact_dir, monkeypatch):
    """Test saving sources/citations."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    task_id = "test-123"
    sources = [
        {"url": "https://python.org", "title": "Python.org", "excerpt": "Python is..."},
        {
            "url": "https://docs.python.org",
            "title": "Python Docs",
            "excerpt": "Documentation...",
        },
    ]

    # Save sources
    await save_sources(task_id, sources)

    # Verify file exists
    task_dir = get_task_dir(task_id)
    sources_file = task_dir / "sources.json"
    assert sources_file.exists()

    # Verify content
    with open(sources_file, "r") as f:
        loaded_sources = json.load(f)
    assert len(loaded_sources) == 2
    assert loaded_sources[0]["url"] == "https://python.org"


@pytest.mark.asyncio
async def test_delete_task_artifacts(test_artifact_dir, monkeypatch):
    """Test deleting task artifacts."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    task_id = "test-123"

    # Create some artifacts
    await save_task_result(task_id, {"task_id": task_id})
    await save_logs(task_id, "Some logs")
    await save_sources(task_id, [{"url": "https://example.com", "title": "Example"}])

    # Verify artifacts exist
    task_dir = get_task_dir(task_id)
    assert task_dir.exists()

    # Delete artifacts
    result = await delete_task_artifacts(task_id)
    assert result is True

    # Verify artifacts are gone
    assert not task_dir.exists()


@pytest.mark.asyncio
async def test_delete_task_artifacts_not_found(test_artifact_dir, monkeypatch):
    """Test deleting non-existent artifacts."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    task_id = "non-existent"

    # Don't create the directory - delete should return True because get_task_dir creates it
    # but there are no actual artifact files
    result = await delete_task_artifacts(task_id)
    assert result is True  # Directory was created and deleted


def test_get_screenshot_path(test_artifact_dir, monkeypatch):
    """Test get_screenshot_path."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    task_id = "test-123"
    filename = "step_1.png"

    # Create screenshot file
    screenshot_dir = get_task_dir(task_id) / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot_file = screenshot_dir / filename
    screenshot_file.write_bytes(b"fake image data")

    # Get path
    path = get_screenshot_path(task_id, filename)
    assert path is not None
    assert path.exists()
    assert path.name == filename


def test_get_screenshot_path_not_found(test_artifact_dir, monkeypatch):
    """Test get_screenshot_path with non-existent file."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    path = get_screenshot_path("test-123", "non-existent.png")
    assert path is None


@pytest.mark.asyncio
async def test_get_artifact_stats(test_artifact_dir, monkeypatch):
    """Test get_artifact_stats."""
    from src import artifacts

    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", test_artifact_dir)

    task_id = "test-123"

    # get_task_dir creates the directory, so exists will be True
    # but there are no actual artifact files
    stats = await get_artifact_stats(task_id)
    assert stats["exists"] is True  # Directory created by get_task_dir
    assert stats["has_result"] is False  # But no artifact files yet
    assert stats["has_logs"] is False
    assert stats["has_sources"] is False
    assert stats["screenshot_count"] == 0

    # Create artifacts
    await save_task_result(task_id, {"task_id": task_id, "question": "Test"})
    await save_logs(task_id, "Some logs")
    await save_sources(task_id, [{"url": "https://example.com", "title": "Example"}])
    await save_screenshot(task_id, 1, b"fake image 1")
    await save_screenshot(task_id, 2, b"fake image 2")

    # Get stats
    stats = await get_artifact_stats(task_id)
    assert stats["exists"] is True
    assert stats["has_result"] is True
    assert stats["has_logs"] is True
    assert stats["has_sources"] is True
    assert stats["screenshot_count"] == 2
    assert stats["total_size_bytes"] > 0
