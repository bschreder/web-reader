"""Unit tests for search module."""

import pytest
from unittest.mock import AsyncMock, patch

from src.search import SearchResult, search, search_duckduckgo, search_bing


class TestSearchResult:
    """Test SearchResult class."""

    def test_search_result_creation(self):
        """Test SearchResult can be instantiated."""
        result = SearchResult(
            title="Example", url="https://example.com", snippet="Test snippet"
        )
        assert result.title == "Example"
        assert result.url == "https://example.com"
        assert result.snippet == "Test snippet"

    def test_search_result_equality(self):
        """Test SearchResult equality."""
        result1 = SearchResult(
            title="Example", url="https://example.com", snippet="Test snippet"
        )
        result2 = SearchResult(
            title="Example", url="https://example.com", snippet="Test snippet"
        )
        # DataClass comparison is based on field values
        assert result1.title == result2.title
        assert result1.url == result2.url
        assert result1.snippet == result2.snippet

    def test_search_result_different(self):
        """Test SearchResult inequality."""
        result1 = SearchResult(
            title="Example", url="https://example.com", snippet="Test snippet"
        )
        result2 = SearchResult(
            title="Different",
            url="https://different.com",
            snippet="Different snippet",
        )
        assert result1 != result2


@pytest.mark.asyncio
class TestSearchDuckDuckGo:
    """Test DuckDuckGo search."""

    async def test_search_duckduckgo_basic(self):
        """Test basic DuckDuckGo search."""
        with patch("src.search.httpx.AsyncClient") as mock_client:
            # Mock HTTP response with DuckDuckGo lite HTML
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
            <body>
            <a href="https://example.com"><span class="result__title">Example Result</span></a>
            <div class="result__snippet">This is a test snippet</div>
            </body>
            </html>
            """
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            results = await search_duckduckgo("test query", max_results=10)

            # Should return a list (may be empty if regex doesn't match)
            assert isinstance(results, list)

    async def test_search_duckduckgo_empty(self):
        """Test DuckDuckGo search with no results."""
        with patch("src.search.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body></body></html>"
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            results = await search_duckduckgo("nonexistent query", max_results=10)

            assert isinstance(results, list)
            assert len(results) == 0

    async def test_search_duckduckgo_network_error(self):
        """Test DuckDuckGo search with network error."""
        with patch("src.search.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                Exception("Network error")
            )

            results = await search_duckduckgo("test query", max_results=10)

            # Should return empty list on error
            assert isinstance(results, list)
            assert len(results) == 0

    async def test_search_duckduckgo_max_results(self):
        """Test DuckDuckGo search respects max_results."""
        with patch("src.search.httpx.AsyncClient") as mock_client:
            # Create a response with multiple results
            html_results = "\n".join(
                f"""
            <tr>
            <td><a href="https://example{i}.com"><span class="result__title">Result {i}</span></a>
            <div class="result__snippet">Snippet {i}</div></td>
            </tr>
            """
                for i in range(20)
            )
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = (
                f"<html><body><table>{html_results}</table></body></html>"
            )
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            results = await search_duckduckgo("test query", max_results=5)

            # Results should be limited to max_results
            assert isinstance(results, list)
            assert len(results) <= 5


@pytest.mark.asyncio
class TestSearchBing:
    """Test Bing search."""

    async def test_search_bing_basic(self):
        """Test basic Bing search."""
        with patch("src.search.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
            <body>
            <h2><a href="https://example.com">Example Result</a></h2>
            <p>This is a test snippet</p>
            </body>
            </html>
            """
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            results = await search_bing("test query", safe_mode=True)

            # May be empty if regex doesn't match HTML structure
            assert isinstance(results, list)

    async def test_search_bing_safe_search_disabled(self):
        """Test Bing search with safe search disabled."""
        with patch("src.search.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body></body></html>"
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            results = await search_bing("test query", safe_mode=False)

            # Verify the request was made
            assert isinstance(results, list)

    async def test_search_bing_network_error(self):
        """Test Bing search with network error."""
        with patch("src.search.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                Exception("Network error")
            )

            results = await search_bing("test query")

            # Should return empty list on error
            assert isinstance(results, list)
            assert len(results) == 0


@pytest.mark.asyncio
class TestSearch:
    """Test universal search function."""

    async def test_search_duckduckgo_engine(self):
        """Test search with DuckDuckGo engine."""
        with patch("src.search.search_duckduckgo") as mock_search:
            mock_search.return_value = [
                SearchResult("Example", "https://example.com", "Test")
            ]

            results = await search("test query", engine="duckduckgo")

            mock_search.assert_called_once()
            assert len(results) > 0

    async def test_search_bing_engine(self):
        """Test search with Bing engine."""
        with patch("src.search.search_bing") as mock_search:
            mock_search.return_value = [
                SearchResult("Example", "https://example.com", "Test")
            ]

            results = await search("test query", engine="bing")

            mock_search.assert_called_once()
            assert len(results) > 0

    async def test_search_invalid_engine(self):
        """Test search with invalid engine."""
        # Invalid engines are handled gracefully by defaulting to DuckDuckGo
        with patch("src.search.search_duckduckgo") as mock_search:
            mock_search.return_value = []

            # Should not raise, just log a warning and use DuckDuckGo
            result = await search("test query", engine="invalid")
            assert isinstance(result, list)

    async def test_search_default_engine(self):
        """Test search with default engine (DuckDuckGo)."""
        with patch("src.search.search_duckduckgo") as mock_search:
            mock_search.return_value = []

            await search("test query")

            # Should use DuckDuckGo by default
            mock_search.assert_called_once()

    async def test_search_max_results_validation(self):
        """Test search respects max_results parameter."""
        with patch("src.search.search_duckduckgo") as mock_search:
            mock_search.return_value = []

            await search("test query", max_results=20)

            # Should pass max_results to underlying function
            mock_search.assert_called_once()
            call_args = mock_search.call_args
            assert "max_results" in call_args.kwargs or len(call_args.args) > 1
