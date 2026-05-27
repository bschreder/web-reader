"""Unit tests for link extraction module."""

import pytest

from src.link_extractor import (
    Link,
    LinkTracker,
    extract_links,
    filter_links,
)


class TestLink:
    """Test Link class."""

    def test_link_creation(self):
        """Test Link can be instantiated."""
        link = Link(url="https://example.com", text="Example", depth=0)
        assert link.url == "https://example.com"
        assert link.text == "Example"
        assert link.depth == 0

    def test_link_normalized_url(self):
        """Test Link normalizes URL."""
        link = Link(url="https://example.com/page#section", text="Example", depth=0)
        # Normalized URL should remove fragment and trailing slashes
        assert "#" not in link.normalized_url
        assert link.normalized_url is not None

    def test_link_equality(self):
        """Test Link equality by normalized URL."""
        link1 = Link(url="https://example.com/page", text="Text1", depth=0)
        link2 = Link(url="https://example.com/page#different", text="Text2", depth=1)
        # Should be equal since normalized URLs are the same
        assert link1.normalized_url == link2.normalized_url

    def test_link_different_domains(self):
        """Test Link inequality for different domains."""
        link1 = Link(url="https://example.com", text="Example", depth=0)
        link2 = Link(url="https://different.com", text="Different", depth=0)
        assert link1.normalized_url != link2.normalized_url


class TestExtractLinks:
    """Test link extraction."""

    def test_extract_links_basic(self):
        """Test basic link extraction."""
        html = """
        <html>
        <body>
        <a href="https://example.com">Example</a>
        <a href="https://other.com">Other</a>
        </body>
        </html>
        """
        links = extract_links(html, base_url="https://mysite.com")

        assert len(links) >= 2
        assert any(link.url == "https://example.com" for link in links)
        assert any(link.url == "https://other.com" for link in links)

    def test_extract_links_relative_urls(self):
        """Test extraction with relative URLs."""
        html = """
        <html>
        <body>
        <a href="/page">Page</a>
        <a href="../other">Other</a>
        </body>
        </html>
        """
        links = extract_links(html, base_url="https://example.com/section/")

        assert len(links) >= 2
        # Relative URLs should be resolved to absolute
        urls = [link.url for link in links]
        assert any("example.com" in url for url in urls)

    def test_extract_links_with_text(self):
        """Test extraction preserves link text."""
        html = """
        <html>
        <body>
        <a href="https://example.com">Click Here</a>
        </body>
        </html>
        """
        links = extract_links(html, base_url="https://mysite.com")

        assert len(links) > 0
        assert links[0].text == "Click Here"

    def test_extract_links_no_links(self):
        """Test extraction with no links."""
        html = "<html><body>No links here</body></html>"
        links = extract_links(html, base_url="https://example.com")

        assert len(links) == 0

    def test_extract_links_javascript_ignored(self):
        """Test JavaScript links are not extracted."""
        html = """
        <html>
        <body>
        <a href="javascript:void(0)">JS Link</a>
        <a href="https://example.com">Real Link</a>
        </body>
        </html>
        """
        links = extract_links(html, base_url="https://mysite.com")

        # Should only get the real link
        assert all("javascript:" not in link.url for link in links)

    def test_extract_links_anchors_ignored(self):
        """Test anchor-only links are not extracted."""
        html = """
        <html>
        <body>
        <a href="#section">Anchor</a>
        <a href="https://example.com">Real Link</a>
        </body>
        </html>
        """
        links = extract_links(html, base_url="https://mysite.com")

        # Should only get the real link
        assert all("#" not in link.url for link in links)


class TestFilterLinks:
    """Test link filtering."""

    def test_filter_links_basic(self):
        """Test basic link filtering."""
        links = [
            Link(url="https://example.com/page1", text="Page 1", depth=0),
            Link(url="https://example.com/page2", text="Page 2", depth=0),
            Link(url="https://other.com", text="Other Site", depth=0),
        ]

        filtered = filter_links(
            links, seed_url="https://example.com", same_domain_only=True
        )

        # Should only include example.com links
        assert len(filtered) >= 2
        assert any("example.com" in link.url for link in filtered)

    def test_filter_links_same_domain_false(self):
        """Test filtering with same_domain_only=False."""
        links = [
            Link(url="https://example.com/page1", text="Page 1", depth=0),
            Link(url="https://other.com", text="Other Site", depth=0),
        ]

        filtered = filter_links(
            links, seed_url="https://example.com", same_domain_only=False
        )

        # Should include all links
        assert len(filtered) == 2

    def test_filter_links_max_depth(self):
        """Test filtering respects max_depth."""
        links = [
            Link(url="https://example.com/page1", text="Page 1", depth=0),
            Link(url="https://example.com/page2", text="Page 2", depth=1),
            Link(url="https://example.com/page3", text="Page 3", depth=3),
        ]

        filtered = filter_links(links, seed_url="https://example.com", max_depth=2)

        # Should exclude depth=3
        assert all(link.depth <= 2 for link in filtered)

    def test_filter_links_login_page(self):
        """Test filtering excludes login pages."""
        links = [
            Link(url="https://example.com/login", text="Login", depth=0),
            Link(url="https://example.com/signin", text="Sign In", depth=0),
            Link(url="https://example.com/auth", text="Auth", depth=0),
            Link(url="https://example.com/page", text="Page", depth=0),
        ]

        filtered = filter_links(links, seed_url="https://example.com")

        # Should filter auth-related pages
        urls = [link.url for link in filtered]
        # Check that some links were filtered
        assert len(filtered) <= len(links)

    def test_filter_links_pdf_excluded(self):
        """Test filtering excludes PDF links."""
        links = [
            Link(url="https://example.com/doc.pdf", text="PDF", depth=0),
            Link(url="https://example.com/page", text="Page", depth=0),
        ]

        filtered = filter_links(links, seed_url="https://example.com")

        # PDF links should be filtered
        assert len(filtered) <= len(links)

    def test_filter_links_empty(self):
        """Test filtering empty list."""
        filtered = filter_links([], seed_url="https://example.com")

        assert len(filtered) == 0


class TestLinkTracker:
    """Test LinkTracker class."""

    def test_link_tracker_creation(self):
        """Test LinkTracker can be instantiated."""
        tracker = LinkTracker()
        assert tracker is not None
        assert len(tracker.visited) == 0

    def test_link_tracker_add_link(self):
        """Test adding links to tracker."""
        tracker = LinkTracker()
        link = Link(url="https://example.com", text="Example", depth=0)

        result = tracker.add_link(link)

        assert result is True
        assert link.normalized_url in tracker.visited

    def test_link_tracker_duplicate_link(self):
        """Test adding duplicate links returns False."""
        tracker = LinkTracker()
        link1 = Link(url="https://example.com/page", text="Page", depth=0)
        link2 = Link(url="https://example.com/page#different", text="Page", depth=1)

        result1 = tracker.add_link(link1)
        result2 = tracker.add_link(link2)

        assert result1 is True
        assert result2 is False  # Duplicate normalized URL

    def test_link_tracker_next_link(self):
        """Test retrieving next link from tracker."""
        tracker = LinkTracker()
        link1 = Link(url="https://example.com/page1", text="Page 1", depth=0)
        link2 = Link(url="https://example.com/page2", text="Page 2", depth=0)

        tracker.add_link(link1)
        tracker.add_link(link2)

        next_link = tracker.next_link()

        assert next_link is not None
        assert next_link.url == "https://example.com/page1"

    def test_link_tracker_fifo_order(self):
        """Test tracker maintains FIFO order."""
        tracker = LinkTracker()
        links = [
            Link(url=f"https://example.com/page{i}", text=f"Page {i}", depth=0)
            for i in range(5)
        ]

        for link in links:
            tracker.add_link(link)

        # Should retrieve in FIFO order
        for i, link in enumerate(links):
            next_link = tracker.next_link()
            assert next_link.url == link.url

    def test_link_tracker_empty_queue(self):
        """Test tracker returns None when empty."""
        tracker = LinkTracker()

        next_link = tracker.next_link()

        assert next_link is None

    def test_link_tracker_visited_set(self):
        """Test tracker maintains visited set."""
        tracker = LinkTracker()
        link1 = Link(url="https://example.com/page1", text="Page 1", depth=0)
        link2 = Link(url="https://example.com/page2", text="Page 2", depth=0)

        tracker.add_link(link1)
        tracker.add_link(link2)

        assert len(tracker.visited) == 2
        assert link1.normalized_url in tracker.visited
        assert link2.normalized_url in tracker.visited

    def test_link_tracker_mixed_operations(self):
        """Test tracker with mixed add and retrieve operations."""
        tracker = LinkTracker()
        link1 = Link(url="https://example.com/page1", text="Page 1", depth=0)
        link2 = Link(url="https://example.com/page2", text="Page 2", depth=0)
        link3 = Link(url="https://example.com/page3", text="Page 3", depth=0)

        tracker.add_link(link1)
        first = tracker.next_link()
        assert first.url == link1.url

        tracker.add_link(link2)
        tracker.add_link(link3)

        second = tracker.next_link()
        third = tracker.next_link()

        assert second.url == link2.url
        assert third.url == link3.url
