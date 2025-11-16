"""
Unit tests for task-scoped browser context isolation.

Tests ensure that each task gets its own isolated browser context,
maintaining privacy and preventing data leakage between tasks.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.browser import (
    create_context,
    get_current_page,
    cleanup_task_context,
    _contexts,
    _pages,
)


class TestTaskScopedContexts:
    """Test task-scoped browser context isolation."""

    @pytest.mark.asyncio
    async def test_different_tasks_get_different_contexts(self):
        """Each task should get its own isolated context."""
        with patch("src.browser.get_browser") as mock_get_browser:
            mock_browser = AsyncMock()
            mock_context1 = AsyncMock()
            mock_context2 = AsyncMock()
            mock_browser.new_context.side_effect = [mock_context1, mock_context2]
            mock_get_browser.return_value = mock_browser

            # Create contexts for two different tasks
            context1 = await create_context(task_id="task-1")
            context2 = await create_context(task_id="task-2")

            # Should have created two separate contexts
            assert mock_browser.new_context.call_count == 2
            assert context1 == mock_context1
            assert context2 == mock_context2
            assert context1 != context2

    @pytest.mark.asyncio
    async def test_same_task_reuses_context(self):
        """Same task should reuse its existing context."""
        with patch("src.browser.get_browser") as mock_get_browser:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()
            mock_context.new_page.return_value = mock_page
            mock_browser.new_context.return_value = mock_context
            mock_get_browser.return_value = mock_browser

            # Get page for same task twice
            page1 = await get_current_page(task_id="task-1")
            page2 = await get_current_page(task_id="task-1")

            # Should create context only once
            assert mock_browser.new_context.call_count == 1
            assert mock_context.new_page.call_count == 1
            assert page1 == page2

    @pytest.mark.asyncio
    async def test_cleanup_task_context_removes_context_and_page(self):
        """Cleanup should close and remove task's context and page."""
        with (
            patch("src.browser.get_browser") as mock_get_browser,
            patch("src.browser._contexts", {}) as mock_contexts,
            patch("src.browser._pages", {}) as mock_pages,
        ):
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()
            mock_context.new_page.return_value = mock_page
            mock_browser.new_context.return_value = mock_context
            mock_get_browser.return_value = mock_browser

            # Manually populate the dictionaries
            from src.browser import _contexts, _pages

            _contexts["task-1"] = mock_context
            _pages["task-1"] = mock_page

            # Verify context exists
            assert "task-1" in _contexts
            assert "task-1" in _pages

            # Clean up the task
            await cleanup_task_context(task_id="task-1")

            # Verify cleanup
            mock_page.close.assert_awaited_once()
            mock_context.close.assert_awaited_once()
            assert "task-1" not in _contexts
            assert "task-1" not in _pages

    @pytest.mark.asyncio
    async def test_cleanup_nonexistent_task_is_safe(self):
        """Cleaning up non-existent task should not raise error."""
        # Should not raise
        await cleanup_task_context(task_id="nonexistent-task")

    @pytest.mark.asyncio
    async def test_multiple_tasks_maintain_isolation(self):
        """Multiple concurrent tasks should have isolated contexts."""
        with patch("src.browser.get_browser") as mock_get_browser:
            mock_browser = AsyncMock()

            # Create separate mock contexts for each task
            contexts = {}
            pages = {}

            def create_mock_context(*args, **kwargs):
                mock_ctx = AsyncMock()
                mock_pg = AsyncMock()
                mock_ctx.new_page.return_value = mock_pg
                return mock_ctx

            mock_browser.new_context.side_effect = create_mock_context
            mock_get_browser.return_value = mock_browser

            # Create pages for 3 different tasks
            page1 = await get_current_page(task_id="task-1")
            page2 = await get_current_page(task_id="task-2")
            page3 = await get_current_page(task_id="task-3")

            # Should have 3 contexts and 3 pages
            assert len(_contexts) >= 3
            assert len(_pages) >= 3
            assert "task-1" in _contexts
            assert "task-2" in _contexts
            assert "task-3" in _contexts

            # All pages should be different objects
            assert page1 != page2 != page3

    @pytest.mark.asyncio
    async def test_default_task_id_maintains_backward_compatibility(self):
        """Not providing task_id should use 'default' for backward compatibility."""
        with patch("src.browser.get_browser") as mock_get_browser:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()
            mock_context.new_page.return_value = mock_page
            mock_browser.new_context.return_value = mock_context
            mock_get_browser.return_value = mock_browser

            # Call without task_id
            page = await get_current_page()

            # Should use "default" task_id
            assert "default" in _contexts
            assert "default" in _pages

    @pytest.mark.asyncio
    async def test_cleanup_handles_close_errors_gracefully(self):
        """Cleanup should handle errors during close operations."""
        with patch("src.browser.get_browser") as mock_get_browser:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            # Make close operations raise errors
            mock_page.close.side_effect = Exception("Page close error")
            mock_context.close.side_effect = Exception("Context close error")

            mock_context.new_page.return_value = mock_page
            mock_browser.new_context.return_value = mock_context
            mock_get_browser.return_value = mock_browser

            # Create context
            await get_current_page(task_id="error-task")

            # Cleanup should not raise despite errors
            await cleanup_task_context(task_id="error-task")

            # Should still remove from dictionaries
            assert "error-task" not in _contexts
            assert "error-task" not in _pages


class TestTaskScopedTools:
    """Test that tools respect task_id parameter."""

    @pytest.mark.asyncio
    async def test_navigate_to_uses_task_id(self):
        """navigate_to should pass task_id to get_current_page."""
        from src.tools import navigate_to

        with (
            patch("src.tools.get_current_page") as mock_get_page,
            patch("src.tools.is_domain_allowed", return_value=True),
            patch("src.tools.enforce_rate_limit"),
        ):
            mock_page = AsyncMock()
            mock_response = MagicMock()
            mock_response.status = 200
            mock_page.goto.return_value = mock_response
            mock_page.title.return_value = "Test Page"
            mock_page.url = "https://example.com"
            mock_get_page.return_value = mock_page

            # Call with task_id
            await navigate_to(url="https://example.com", task_id="test-task")

            # Should pass task_id to get_current_page
            mock_get_page.assert_called_once_with(task_id="test-task")

    @pytest.mark.asyncio
    async def test_get_page_content_uses_task_id(self):
        """get_page_content should pass task_id to get_current_page."""
        from src.tools import get_page_content

        with patch("src.tools.get_current_page") as mock_get_page:
            mock_page = AsyncMock()
            mock_page.title.return_value = "Test Page"
            mock_page.url = "https://example.com"
            mock_page.evaluate.return_value = {"text": "content", "html": "<p>content</p>"}
            mock_get_page.return_value = mock_page

            # Call with task_id
            await get_page_content(task_id="test-task")

            # Should pass task_id to get_current_page
            mock_get_page.assert_called_once_with(task_id="test-task")

    @pytest.mark.asyncio
    async def test_take_screenshot_uses_task_id(self):
        """take_screenshot should pass task_id to get_current_page."""
        from src.tools import take_screenshot

        with patch("src.tools.get_current_page") as mock_get_page:
            mock_page = AsyncMock()
            mock_page.screenshot.return_value = b"fake_image_data"
            mock_get_page.return_value = mock_page

            # Call with task_id
            await take_screenshot(task_id="test-task")

            # Should pass task_id to get_current_page
            mock_get_page.assert_called_once_with(task_id="test-task")
