"""Tests for LangChain tool wrappers."""

import pytest
from src.collector import get_collector, reset_collector
from src.tools import create_langchain_tools


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

        assert len(tools) == 4
        assert all(hasattr(tool, "name") for tool in tools)
        assert all(hasattr(tool, "description") for tool in tools)

        tool_names = [tool.name for tool in tools]
        assert "navigate_to" in tool_names
        assert "get_page_content" in tool_names
        assert "take_screenshot" in tool_names

    def test_create_langchain_tools_with_search_and_links(self, mock_mcp_client):
        """Test optional search/link tool registration."""
        tools = create_langchain_tools(mock_mcp_client, include_search_and_links=True)

        assert len(tools) == 6
        tool_names = [tool.name for tool in tools]
        assert "search_for_question" in tool_names
        assert "extract_links_from_page" in tool_names

    @pytest.mark.asyncio
    async def test_search_for_question_wrapper_validation(self):
        """Test validation errors for search wrapper input."""
        from src.tools import search_for_question_wrapper

        result = await search_for_question_wrapper("q", "duckduckgo", 0)
        assert "max_results must be between 1 and 50" in result

        result = await search_for_question_wrapper("q", "invalid", 5)
        assert "Unknown search engine" in result

    @pytest.mark.asyncio
    async def test_search_for_question_wrapper_success_and_empty(self, monkeypatch):
        """Test successful and empty search responses."""
        from src.search import SearchResult
        from src.tools import search_for_question_wrapper

        async def fake_search(_query, engine, max_results):
            assert engine == "duckduckgo"
            assert max_results == 2
            return [
                SearchResult(
                    title="Result One",
                    url="https://example.com/1",
                    snippet="Snippet one",
                ),
                SearchResult(
                    title="Result Two",
                    url="https://example.com/2",
                    snippet="Snippet two",
                ),
            ]

        async def fake_empty(*_args, **_kwargs):
            return []

        monkeypatch.setattr("src.tools.search", fake_search)
        reset_collector()
        result = await search_for_question_wrapper("question", "duckduckgo", 2)
        assert "Found 2 results" in result
        collector = get_collector()
        assert any(c.url == "https://example.com/1" for c in collector.citations)

        monkeypatch.setattr("src.tools.search", fake_empty)
        result = await search_for_question_wrapper("question", "duckduckgo", 2)
        assert "No results found" in result

    @pytest.mark.asyncio
    async def test_search_for_question_wrapper_exception(self, monkeypatch):
        """Test search wrapper error path."""
        from src.tools import search_for_question_wrapper

        async def fake_search_error(*_args, **_kwargs):
            raise RuntimeError("search service unavailable")

        monkeypatch.setattr("src.tools.search", fake_search_error)
        result = await search_for_question_wrapper("question", "duckduckgo", 3)
        assert "Search error:" in result

    @pytest.mark.asyncio
    async def test_extract_links_from_page_wrapper_paths(self, monkeypatch):
        """Test link extraction wrapper for success and edge paths."""
        from src.link_extractor import Link
        from src.tools import extract_links_from_page_wrapper

        sample_links = [
            Link(url="https://example.com/a", text="A", depth=0),
            Link(url="https://example.com/b", text="B", depth=0),
        ]

        def fake_extract(*_args, **_kwargs):
            return sample_links

        def fake_filter(*_args, **_kwargs):
            return sample_links

        monkeypatch.setattr("src.tools.extract_links", fake_extract)
        monkeypatch.setattr("src.tools.filter_links", fake_filter)

        result = await extract_links_from_page_wrapper(
            "<html></html>", "https://example.com", 1, False, True, 2
        )
        assert "Extracted 1 links" in result

        monkeypatch.setattr("src.tools.extract_links", lambda *_a, **_k: [])
        result = await extract_links_from_page_wrapper(
            "<html></html>", "https://example.com", 10, False, True, 2
        )
        assert result == "No links found in page content"

        monkeypatch.setattr("src.tools.extract_links", fake_extract)
        monkeypatch.setattr("src.tools.filter_links", lambda *_a, **_k: [])
        result = await extract_links_from_page_wrapper(
            "<html></html>", "https://example.com", 10, False, True, 2
        )
        assert result == "No valid links found after filtering"

    @pytest.mark.asyncio
    async def test_extract_links_from_page_wrapper_exception(self, monkeypatch):
        """Test link extraction wrapper exception path."""
        from src.tools import extract_links_from_page_wrapper

        def fake_extract_error(*_args, **_kwargs):
            raise RuntimeError("parse failed")

        monkeypatch.setattr("src.tools.extract_links", fake_extract_error)
        result = await extract_links_from_page_wrapper(
            "<html></html>", "https://example.com", 10, False, True, 2
        )
        assert "Link extraction error:" in result
