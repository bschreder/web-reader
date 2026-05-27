"""FastMCP browser tools package for the Web Reader project.

Exports the browser cleanup helper plus metadata useful for discovery.
"""

__version__ = "0.1.0"

__all__ = ["cleanup_task_context"]

from .browser import cleanup_task_context

