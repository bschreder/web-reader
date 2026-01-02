"""
Search integration module for web research.
Provides SERP parsing and search result extraction for UC-01.
"""

import re
from typing import Optional

import httpx
from loguru import logger


class SearchResult:
    """Represents a single search result."""

    def __init__(self, title: str, url: str, snippet: str):
        self.title = title
        self.url = url
        self.snippet = snippet

    def __repr__(self) -> str:
        return f"SearchResult(title='{self.title[:50]}...', url='{self.url}')"


async def search_duckduckgo(
    query: str,
    max_results: int = 10,
    safe_mode: bool = True,
) -> list[SearchResult]:
    """
    Search DuckDuckGo and parse results.

    Args:
        query: Search query
        max_results: Maximum number of results to return (1-50)
        safe_mode: Enable safe search

    Returns:
        List of SearchResult objects
    """
    max_results = max(1, min(50, max_results))

    try:
        # Construct DuckDuckGo search URL
        params = {
            "q": query,
            "t": "h",  # html mode
            "ia": "web",
        }

        if safe_mode:
            params["kp"] = "1"  # safe search on

        async with httpx.AsyncClient(
            timeout=10.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        ) as client:
            # Note: DuckDuckGo's actual SERP endpoint is behind JavaScript
            # This is a simplified implementation that would work with DuckDuckGo's lite version
            url = "https://lite.duckduckgo.com/lite"
            response = await client.get(url, params=params)
            response.raise_for_status()

        # Parse HTML results (simplified regex-based parsing)
        results = _parse_duckduckgo_html(response.text, max_results)
        logger.info(f"DuckDuckGo search for '{query}': {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        return []


async def search_bing(
    query: str,
    max_results: int = 10,
    safe_mode: bool = True,
) -> list[SearchResult]:
    """
    Search Bing and parse results.

    Args:
        query: Search query
        max_results: Maximum number of results to return (1-50)
        safe_mode: Enable safe search

    Returns:
        List of SearchResult objects
    """
    max_results = max(1, min(50, max_results))

    try:
        params = {
            "q": query,
        }

        if safe_mode:
            params["adlt"] = "strict"

        async with httpx.AsyncClient(
            timeout=10.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        ) as client:
            url = "https://www.bing.com/search"
            response = await client.get(url, params=params)
            response.raise_for_status()

        results = _parse_bing_html(response.text, max_results)
        logger.info(f"Bing search for '{query}': {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"Bing search failed: {e}")
        return []


async def search_google(
    query: str,
    max_results: int = 10,
    safe_mode: bool = True,
) -> list[SearchResult]:
    """
    Search Google and parse results.

    Note: Google actively blocks automated SERP requests.
    This is a placeholder implementation.

    Args:
        query: Search query
        max_results: Maximum number of results to return (1-50)
        safe_mode: Enable safe search

    Returns:
        List of SearchResult objects (empty if blocked)
    """
    logger.warning(
        "Google search requires browser automation due to anti-bot measures. "
        "Use navigate_to with 'https://www.google.com/search?q=...' instead."
    )
    return []


async def search(
    query: str,
    engine: str = "duckduckgo",
    max_results: int = 10,
    safe_mode: bool = True,
) -> list[SearchResult]:
    """
    Universal search function.

    Args:
        query: Search query
        engine: Search engine ('duckduckgo', 'bing', 'google')
        max_results: Maximum number of results
        safe_mode: Enable safe search

    Returns:
        List of SearchResult objects
    """
    engine = engine.lower().strip()

    if engine == "duckduckgo":
        return await search_duckduckgo(query, max_results, safe_mode)
    elif engine == "bing":
        return await search_bing(query, max_results, safe_mode)
    elif engine == "google":
        return await search_google(query, max_results, safe_mode)
    else:
        logger.warning(f"Unknown search engine: {engine}. Using DuckDuckGo.")
        return await search_duckduckgo(query, max_results, safe_mode)


# ============================================================================
# HTML Parsing Helpers
# ============================================================================


def _parse_duckduckgo_html(html: str, max_results: int) -> list[SearchResult]:
    """Parse DuckDuckGo lite HTML response."""
    results = []

    # Simple regex-based parsing for DuckDuckGo lite format
    # Pattern: <a href="URL">Title</a> followed by snippet
    pattern = r'<a href="([^"]+)">([^<]+)</a>\s*(?:<br>\s*)?<div[^>]*>([^<]+)'

    for match in re.finditer(pattern, html):
        url = match.group(1)
        title = match.group(2).strip()
        snippet = match.group(3).strip()

        # Skip non-HTTP URLs and ads
        if not url.startswith("http"):
            continue
        if "duckduckgo.com" in url:
            continue

        results.append(SearchResult(title, url, snippet))

        if len(results) >= max_results:
            break

    return results


def _parse_bing_html(html: str, max_results: int) -> list[SearchResult]:
    """Parse Bing HTML response."""
    results = []

    # Simple regex-based parsing for Bing format
    # Bing uses <h2> for titles and <p> for snippets
    pattern = r'<h2><a[^>]*href="([^"]+)"[^>]*>([^<]+)</a></h2>.*?<p>([^<]+)</p>'

    for match in re.finditer(pattern, html, re.DOTALL):
        url = match.group(1).strip()
        title = match.group(2).strip()
        snippet = match.group(3).strip()

        # Remove HTML tags from snippet
        snippet = re.sub(r"<[^>]+>", "", snippet)

        # Skip non-HTTP URLs
        if not url.startswith("http"):
            continue

        results.append(SearchResult(title, url, snippet))

        if len(results) >= max_results:
            break

    return results
