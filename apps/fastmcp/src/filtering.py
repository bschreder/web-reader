"""
Domain filtering module.
Handles allow/deny lists for URL navigation.
"""

import fnmatch
from pathlib import Path
from urllib.parse import urlparse

from loguru import logger

# ============================================================================
# Global State
# ============================================================================

_allowed_domains: list[str] = []
_disallowed_domains: list[str] = []

# ============================================================================
# Domain List Loading
# ============================================================================


def load_domain_list(filepath: str) -> list[str]:
    """Load domain list from configuration file."""
    try:
        path = Path(filepath)
        if not path.exists():
            logger.warning(f"Domain list file not found: {filepath}")
            return []

        with open(path) as f:
            domains = [
                line.strip() for line in f if line.strip() and not line.strip().startswith("#")
            ]
        logger.info(f"Loaded {len(domains)} domains from {filepath}")
        return domains
    except Exception as e:
        logger.error(f"Error loading domain list from {filepath}: {e}")
        return []


def load_allowed_domains(filepath: str = "config/allowed-domains.txt"):
    """Load allowed domains list."""
    global _allowed_domains
    _allowed_domains = load_domain_list(filepath)


def load_disallowed_domains(filepath: str = "config/disallowed-domains.txt"):
    """Load disallowed domains list."""
    global _disallowed_domains
    _disallowed_domains = load_domain_list(filepath)


# ============================================================================
# Domain Filtering
# ============================================================================


def is_domain_allowed(url: str) -> bool:
    """
    Check if domain is allowed by allow/deny lists.

    Args:
        url: URL to check

    Returns:
        True if domain is allowed, False otherwise
    """
    domain = urlparse(url).netloc.lower()

    # Check disallow list first
    for pattern in _disallowed_domains:
        # Treat wildcard patterns as including the apex domain too
        if pattern.startswith("*."):
            apex = pattern[2:]
            if domain == apex:
                logger.warning(f"Domain blocked by deny list: {domain}")
                return False
        if fnmatch.fnmatch(domain, pattern):
            logger.warning(f"Domain blocked by deny list: {domain}")
            return False

    # If allow list exists and is not empty, domain must be in it
    if _allowed_domains:
        for pattern in _allowed_domains:
            if pattern.startswith("*."):
                apex = pattern[2:]
                if domain == apex:
                    return True
            if fnmatch.fnmatch(domain, pattern):
                return True
        logger.warning(f"Domain not in allow list: {domain}")
        return False

    return True
