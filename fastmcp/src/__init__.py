"""
Web Reader FastMCP Server - Modular Package
============================================
MCP protocol server providing browser automation tools via Playwright.
"""

__version__ = "0.1.0"

__all__ = ["cleanup_task_context"]

from .browser import cleanup_task_context
