"""Tests for URL normalization functionality."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.browser import normalize_url


class TestUrlNormalization:
    """Test URL normalization logic."""

    def test_adds_https_to_protocol_less_url(self):
        """Test that https:// is added to URLs without protocol."""
        assert normalize_url("example.com") == "https://example.com"
        assert normalize_url("www.example.com") == "https://www.example.com"
        assert normalize_url("sub.example.com/path") == "https://sub.example.com/path"

    def test_converts_http_to_https(self):
        """Test that http:// is converted to https://."""
        assert normalize_url("http://example.com") == "https://example.com"
        assert normalize_url("http://www.example.com/path") == "https://www.example.com/path"
        assert normalize_url("http://example.com:8080") == "https://example.com:8080"

    def test_preserves_https_urls(self):
        """Test that https:// URLs are unchanged."""
        assert normalize_url("https://example.com") == "https://example.com"
        assert (
            normalize_url("https://www.example.com/path?q=1") == "https://www.example.com/path?q=1"
        )

    def test_handles_urls_with_paths(self):
        """Test URLs with paths are normalized correctly."""
        assert normalize_url("example.com/path/to/page") == "https://example.com/path/to/page"
        assert normalize_url("http://example.com/path") == "https://example.com/path"

    def test_handles_urls_with_query_params(self):
        """Test URLs with query parameters are normalized correctly."""
        assert normalize_url("example.com?query=value") == "https://example.com?query=value"
        assert normalize_url("http://example.com?q=1&p=2") == "https://example.com?q=1&p=2"

    def test_handles_urls_with_fragments(self):
        """Test URLs with fragments are normalized correctly."""
        assert normalize_url("example.com#section") == "https://example.com#section"
        assert normalize_url("http://example.com/page#top") == "https://example.com/page#top"

    def test_handles_urls_with_ports(self):
        """Test URLs with custom ports are normalized correctly."""
        assert normalize_url("example.com:8080") == "https://example.com:8080"
        assert normalize_url("http://example.com:3000") == "https://example.com:3000"

    def test_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        assert normalize_url("  example.com  ") == "https://example.com"
        assert normalize_url("\nhttp://example.com\t") == "https://example.com"

    def test_only_replaces_first_http(self):
        """Test that only the protocol http:// is replaced, not other occurrences."""
        # URL with http in path
        result = normalize_url("http://example.com/http://redirect")
        assert result == "https://example.com/http://redirect"

    def test_complex_urls(self):
        """Test complex real-world URLs."""
        assert (
            normalize_url("http://example.com:8080/path?q=1#section")
            == "https://example.com:8080/path?q=1#section"
        )

        assert (
            normalize_url("subdomain.example.com:3000/api/v1/resource?filter=active")
            == "https://subdomain.example.com:3000/api/v1/resource?filter=active"
        )
