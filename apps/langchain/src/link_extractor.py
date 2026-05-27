"""
Link extraction and following module for web research.
Handles link discovery, filtering, and depth tracking for UC-02.
"""

import re
from typing import Optional
from urllib.parse import urljoin, urlparse

from loguru import logger


class Link:
    """Represents a discovered link."""

    def __init__(self, url: str, text: str, depth: int = 0):
        self.url = url
        self.text = text
        self.depth = depth
        self.normalized_url = _normalize_url(url)

    def __repr__(self) -> str:
        return f"Link(url='{self.url[:50]}...', depth={self.depth})"

    def __hash__(self) -> int:
        return hash(self.normalized_url)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Link):
            return False
        return self.normalized_url == other.normalized_url


def _normalize_url(url: str) -> str:
    """
    Normalize URL for comparison.
    Removes fragments and normalizes query params.
    """
    # Remove fragment
    url = url.split("#")[0]
    # Remove trailing slash
    url = url.rstrip("/")
    return url.lower()


def extract_links(
    html: str,
    base_url: str,
    current_depth: int = 0,
) -> list[Link]:
    """
    Extract all links from HTML content.

    Args:
        html: HTML content
        base_url: Base URL for resolving relative links
        current_depth: Current depth for tracking

    Returns:
        List of Link objects
    """
    links = []

    # Extract <a> tags with href attributes
    pattern = (
        r'<a\s+(?:[^>]*?\s+)?href=["\']((?:[^"\'\\]|\\.)*)["\'](?:[^>]*?)>([^<]*)</a>'
    )

    for match in re.finditer(pattern, html, re.IGNORECASE | re.DOTALL):
        href = match.group(1).strip()
        text = match.group(2).strip()

        if not href:
            continue

        # Resolve relative URLs
        try:
            absolute_url = urljoin(base_url, href)
        except Exception:
            logger.debug(f"Failed to resolve URL: {href}")
            continue

        # Skip non-HTTP(S) URLs
        if not absolute_url.startswith(("http://", "https://")):
            continue

        # Skip javascript and anchor-only links
        if absolute_url.startswith("javascript:") or href.startswith("#"):
            continue

        link = Link(absolute_url, text, current_depth + 1)
        links.append(link)

    logger.debug(f"Extracted {len(links)} links from page")
    return links


def filter_links(
    links: list[Link],
    seed_url: Optional[str] = None,
    same_domain_only: bool = False,
    allow_external_links: bool = True,
    max_depth: int = 5,
) -> list[Link]:
    """
    Filter links based on constraints.

    Args:
        links: List of links to filter
        seed_url: Original seed URL for domain comparison
        same_domain_only: Only follow links on same domain as seed_url
        allow_external_links: Allow external links (requires seed_url)
        max_depth: Maximum depth to follow

    Returns:
        Filtered list of links
    """
    if not links:
        return []

    filtered = []
    seed_domain = _get_domain(seed_url) if seed_url else None

    for link in links:
        # Check depth limit
        if link.depth > max_depth:
            continue

        link_domain = _get_domain(link.url)

        # Check domain constraints
        if same_domain_only and seed_domain and link_domain != seed_domain:
            continue

        if not allow_external_links and seed_domain and link_domain != seed_domain:
            continue

        # Skip common non-content pages
        if _is_excluded_url(link.url):
            continue

        filtered.append(link)

    logger.debug(
        f"Filtered {len(links)} → {len(filtered)} links "
        f"(same_domain={same_domain_only}, allow_external={allow_external_links})"
    )
    return filtered


def _get_domain(url: Optional[str]) -> Optional[str]:
    """Extract domain from URL."""
    if not url:
        return None
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None


def _is_excluded_url(url: str) -> bool:
    """Check if URL should be excluded from following."""
    excluded_patterns = [
        r"(?:login|signin|signup|register|logout)",
        r"(?:terms|privacy|copyright|disclaimer)",
        r"(?:contact|feedback|support|help)",
        r"(?:admin|dashboard|account|settings)",
        r"(?:advertisement|ads|tracking)",
        r"\.pdf$",
        r"\.zip$",
        r"\.exe$",
    ]

    url_lower = url.lower()
    for pattern in excluded_patterns:
        if re.search(pattern, url_lower):
            return True

    return False


class LinkTracker:
    """Track visited links and manage crawl frontier."""

    def __init__(self):
        self.visited: set[str] = set()
        self.frontier: list[Link] = []
        self.discovered: int = 0

    def add_link(self, link: Link) -> bool:
        """
        Add link to frontier if not already visited.

        Args:
            link: Link to add

        Returns:
            True if added, False if already visited
        """
        normalized = _normalize_url(link.url)
        if normalized in self.visited:
            return False

        self.visited.add(normalized)
        self.frontier.append(link)
        self.discovered += 1
        return True

    def next_link(self) -> Optional[Link]:
        """Get next link to visit (FIFO)."""
        if self.frontier:
            return self.frontier.pop(0)
        return None

    def reset(self) -> None:
        """Reset tracker state."""
        self.visited.clear()
        self.frontier.clear()
        self.discovered = 0
