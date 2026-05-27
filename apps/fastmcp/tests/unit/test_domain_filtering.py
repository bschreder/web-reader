"""Tests for domain filtering functionality."""

import sys
from pathlib import Path

from pytest_mock import MockerFixture

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.filtering import is_domain_allowed, load_domain_list


class TestLoadDomainList:
    """Test domain list loading."""

    def test_load_existing_file(self, tmp_path: Path):
        """Test loading domains from existing file."""
        domain_file = tmp_path / "domains.txt"
        domain_file.write_text("# Comment\nexample.com\n*.wildcard.com\n\n")

        domains = load_domain_list(str(domain_file))

        assert len(domains) == 2
        assert "example.com" in domains
        assert "*.wildcard.com" in domains

    def test_load_nonexistent_file(self):
        """Test loading non-existent file returns empty list."""
        domains = load_domain_list("/nonexistent/file.txt")
        assert domains == []

    def test_skip_empty_lines_and_comments(self, tmp_path: Path):
        """Test that empty lines and comments are skipped."""
        domain_file = tmp_path / "domains.txt"
        domain_file.write_text("""
# This is a comment
example.com

# Another comment
test.com
""")

        domains = load_domain_list(str(domain_file))

        assert len(domains) == 2
        assert "example.com" in domains
        assert "test.com" in domains


class TestIsDomainAllowed:
    """Test domain filtering logic."""

    def test_allow_all_when_no_lists(self, mocker: MockerFixture):
        """Test that all domains allowed when no filters configured."""
        mocker.patch("src.filtering._allowed_domains", [])
        mocker.patch("src.filtering._disallowed_domains", [])
        assert is_domain_allowed("https://example.com") is True
        assert is_domain_allowed("https://any-site.com") is True

    def test_block_disallowed_exact_match(self, mocker: MockerFixture):
        """Test blocking exact domain match in deny list."""
        mocker.patch("src.filtering._allowed_domains", [])
        mocker.patch("src.filtering._disallowed_domains", ["blocked.com"])
        assert is_domain_allowed("https://blocked.com") is False
        assert is_domain_allowed("https://allowed.com") is True

    def test_block_disallowed_wildcard(self, mocker: MockerFixture):
        """Test blocking with wildcard patterns."""
        mocker.patch("src.filtering._allowed_domains", [])
        mocker.patch("src.filtering._disallowed_domains", ["*.blocked.com"])
        assert is_domain_allowed("https://sub.blocked.com") is False
        assert is_domain_allowed("https://another.blocked.com") is False
        assert is_domain_allowed("https://blocked.com") is False
        assert is_domain_allowed("https://notblocked.com") is True

    def test_allow_list_with_exact_match(self, mocker: MockerFixture):
        """Test allow list with exact domain match."""
        mocker.patch("src.filtering._allowed_domains", ["example.com", "test.com"])
        mocker.patch("src.filtering._disallowed_domains", [])
        assert is_domain_allowed("https://example.com") is True
        assert is_domain_allowed("https://test.com") is True
        assert is_domain_allowed("https://other.com") is False

    def test_allow_list_with_wildcard(self, mocker: MockerFixture):
        """Test allow list with wildcard patterns."""
        mocker.patch("src.filtering._allowed_domains", ["*.allowed.com"])
        mocker.patch("src.filtering._disallowed_domains", [])
        assert is_domain_allowed("https://sub.allowed.com") is True
        assert is_domain_allowed("https://another.allowed.com") is True
        assert is_domain_allowed("https://allowed.com") is True
        assert is_domain_allowed("https://notallowed.com") is False

    def test_deny_list_overrides_allow_list(self, mocker: MockerFixture):
        """Test that deny list takes precedence over allow list."""
        mocker.patch("src.filtering._allowed_domains", ["*.example.com"])
        mocker.patch("src.filtering._disallowed_domains", ["bad.example.com"])
        assert is_domain_allowed("https://good.example.com") is True
        assert is_domain_allowed("https://bad.example.com") is False

    def test_case_insensitive_matching(self, mocker: MockerFixture):
        """Test that domain matching is case-insensitive."""
        mocker.patch("src.filtering._allowed_domains", [])
        mocker.patch("src.filtering._disallowed_domains", ["blocked.com"])
        assert is_domain_allowed("https://BLOCKED.COM") is False
        assert is_domain_allowed("https://Blocked.Com") is False

    def test_url_with_path_and_query(self, mocker: MockerFixture):
        """Test that path and query params don't affect domain filtering."""
        mocker.patch("src.filtering._allowed_domains", ["example.com"])
        mocker.patch("src.filtering._disallowed_domains", [])
        assert is_domain_allowed("https://example.com/path/to/page?query=1") is True
        assert is_domain_allowed("https://other.com/path") is False
