"""
LangChain orchestrator client.
Communicates with the LangChain service for task execution.
"""

import asyncio
from typing import Any, Optional

import httpx
from loguru import logger

from .config import LANGCHAIN_URL
from .models import WebSocketEvent
from .tasks import Task

# ============================================================================
# LangChain Client
# ============================================================================


class LangChainClient:
    """Client for communicating with LangChain orchestrator service."""

    def __init__(self, base_url: str = LANGCHAIN_URL):
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def health_check(self) -> bool:
        """
        Check if LangChain orchestrator is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            if not self._client:
                async with httpx.AsyncClient(
                    base_url=self.base_url, timeout=5.0
                ) as client:
                    response = await client.get("/health")
                    return response.status_code == 200
            else:
                response = await self._client.get("/health")
                return response.status_code == 200

        except Exception as e:
            logger.warning(f"LangChain health check failed: {e}")
            return False

    async def execute_task(
        self, task: Task, event_callback: Optional[callable] = None
    ) -> dict[str, Any]:
        """
        Execute a task via LangChain orchestrator.

        Args:
            task: Task to execute
            event_callback: Optional callback for streaming events

        Returns:
            Task execution result

        Raises:
            httpx.HTTPError: If request fails
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            # Prepare request payload
            payload = {
                "task_id": task.task_id,
                "question": task.question,
                "seed_url": task.seed_url,
                "max_depth": task.max_depth,
                "max_pages": task.max_pages,
                "time_budget": task.time_budget,
            }

            # TODO: Implement streaming via SSE or WebSocket
            # For now, use synchronous execution
            logger.info(f"Sending task {task.task_id} to LangChain orchestrator")

            response = await self._client.post(
                "/execute",
                json=payload,
                timeout=task.time_budget + 30.0,  # Add buffer
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"Task {task.task_id} execution completed")
            return result

        except httpx.TimeoutException:
            logger.error(f"Task {task.task_id} timed out")
            raise

        except httpx.HTTPError as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error executing task {task.task_id}: {e}")
            raise


# ============================================================================
# Global Client Instance
# ============================================================================

_langchain_client: Optional[LangChainClient] = None


async def get_langchain_client() -> LangChainClient:
    """Get or create global LangChain client."""
    global _langchain_client

    if _langchain_client is None:
        _langchain_client = LangChainClient()
        await _langchain_client.__aenter__()

    return _langchain_client


async def close_langchain_client():
    """Close global LangChain client."""
    global _langchain_client

    if _langchain_client:
        await _langchain_client.__aexit__(None, None, None)
        _langchain_client = None
