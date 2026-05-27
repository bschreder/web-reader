"""
Execution artifact collector for the LangChain orchestrator.

This module provides a simple, in-memory collector to accumulate
citations (URLs) and screenshots (base64-encoded images) produced
by tool wrappers during a single agent run.

Usage:
- Tool wrappers call add_citation/add_screenshot on success
- The agent reads and returns collected artifacts at the end
- Always reset between runs to avoid cross-test/task leakage
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Citation:
    url: str
    title: Optional[str] = None
    source: Optional[str] = None  # tool name, e.g., "navigate_to"
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionCollector:
    """Holds execution artifacts for a single agent run."""

    citations: List[Citation] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)  # base64 images

    def add_citation(
        self,
        url: str,
        title: Optional[str] = None,
        source: Optional[str] = None,
        **extra: Any,
    ) -> None:
        # Deduplicate by URL + title
        key = (url, title or "")
        existing = {(c.url, c.title or "") for c in self.citations}
        if key not in existing:
            self.citations.append(
                Citation(url=url, title=title, source=source, extra=extra)
            )

    def add_screenshot(self, image_b64: str) -> None:
        if image_b64 and image_b64 not in self.screenshots:
            self.screenshots.append(image_b64)


# Module-level singleton for simplicity. In the future this can be replaced
# with a per-task context if concurrency across tasks is required.
_collector = ExecutionCollector()


def reset_collector() -> None:
    """Reset the global collector state."""
    global _collector
    _collector = ExecutionCollector()


def get_collector() -> ExecutionCollector:
    """Get the current global collector instance."""
    return _collector
