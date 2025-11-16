"""Tests for LangChain tool wrappers."""

import pytest

from src.tools import create_langchain_tools
from src.collector import reset_collector, get_collector


class TestToolWrappers:
    """Test LangChain tool wrapper functions."""

    @pytest.mark.asyncio
    async def test_navigate_to_wrapper_success(
        self, mock_mcp_client, sample_navigate_success
    ):
        """Test navigate_to wrapper with successful result."""
        from src.tools import navigate_to_wrapper

        mock_mcp_client.call_tool.return_value = sample_navigate_success

        reset_collector()
        result = await navigate_to_wrapper(
            "https://example.com", "networkidle", mock_mcp_client
        )

        assert isinstance(result, str)
        assert "Successfully navigated" in result
        assert "Example Domain" in result
        mock_mcp_client.call_tool.assert_called_once_with(
            "navigate_to", {"url": "https://example.com", "wait_until": "networkidle"}
        )
        collector = get_collector()
        assert any(c.url == "https://example.com" for c in collector.citations)

    @pytest.mark.asyncio
    async def test_navigate_to_wrapper_failure(self, mock_mcp_client):
        """Test navigate_to wrapper with failed result."""
        from src.tools import navigate_to_wrapper

        mock_mcp_client.call_tool.return_value = {
            "status": "error",
            "error": "Connection refused",
        }

        result = await navigate_to_wrapper(
            "https://example.com", "networkidle", mock_mcp_client
        )

        assert isinstance(result, str)
        assert "Navigation failed" in result
        assert "Connection refused" in result

    @pytest.mark.asyncio
    async def test_get_page_content_wrapper_success(
        self, mock_mcp_client, sample_content_success
    ):
        """Test get_page_content wrapper with successful result."""
        from src.tools import get_page_content_wrapper

        mock_mcp_client.call_tool.return_value = sample_content_success
        reset_collector()
        result = await get_page_content_wrapper(mock_mcp_client)

        assert isinstance(result, str)
        assert "Example Domain" in result
        assert "28 words" in result
        assert "1 links" in result
        mock_mcp_client.call_tool.assert_called_once_with("get_page_content", {})
        collector = get_collector()
        # Page citation
        assert any(c.url == "https://example.com" for c in collector.citations)
        # Link citations
        assert any(
            c.url == "https://www.iana.org/domains/example" for c in collector.citations
        )

    @pytest.mark.asyncio
    async def test_get_page_content_wrapper_failure(self, mock_mcp_client):
        """Test get_page_content wrapper with failed result."""
        from src.tools import get_page_content_wrapper

        mock_mcp_client.call_tool.return_value = {
            "status": "error",
            "error": "Page not loaded",
        }

        result = await get_page_content_wrapper(mock_mcp_client)

        assert isinstance(result, str)
        assert "Content extraction failed" in result
        assert "Page not loaded" in result

    @pytest.mark.asyncio
    async def test_take_screenshot_wrapper_success(
        self, mock_mcp_client, sample_screenshot_success
    ):
        """Test take_screenshot wrapper with successful result."""
        from src.tools import take_screenshot_wrapper

        mock_mcp_client.call_tool.return_value = sample_screenshot_success
        reset_collector()
        result = await take_screenshot_wrapper(False, mock_mcp_client)

        assert isinstance(result, str)
        assert "Screenshot captured" in result
        assert "viewport" in result
        mock_mcp_client.call_tool.assert_called_once_with(
            "take_screenshot", {"full_page": False}
        )
        collector = get_collector()
        assert len(collector.screenshots) == 1

    @pytest.mark.asyncio
    async def test_take_screenshot_wrapper_failure(self, mock_mcp_client):
        """Test take_screenshot wrapper with failed result."""
        from src.tools import take_screenshot_wrapper

        mock_mcp_client.call_tool.return_value = {
            "status": "error",
            "error": "Browser closed",
        }

        result = await take_screenshot_wrapper(False, mock_mcp_client)

        assert isinstance(result, str)
        assert "Screenshot failed" in result
        assert "Browser closed" in result

    def test_create_langchain_tools(self, mock_mcp_client):
        """Test creation of LangChain StructuredTools."""
        tools = create_langchain_tools(mock_mcp_client)

        assert len(tools) == 3
        assert all(hasattr(tool, "name") for tool in tools)
        assert all(hasattr(tool, "description") for tool in tools)

        tool_names = [tool.name for tool in tools]
        assert "navigate_to" in tool_names
        assert "get_page_content" in tool_names
        assert "take_screenshot" in tool_names
