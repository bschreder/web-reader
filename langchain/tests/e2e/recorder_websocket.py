import asyncio
from typing import Any, Callable, Dict, List, Optional


class RecorderWebSocket:
    """Test helper that records `send_json` calls for assertions.

    - `messages` stores all received event dicts.
    - `wait_for` lets tests wait for an event matching a predicate.
    """

    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self._queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Async method matching FastAPI WebSocket's `send_json`.

        Records the message and makes it available to `wait_for`.
        """
        self.messages.append(data)
        await self._queue.put(data)

    async def wait_for(
        self,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
        timeout: float = 5.0,
    ) -> Dict[str, Any]:
        """Wait for the next message satisfying `predicate`.

        Raises `asyncio.TimeoutError` if the timeout is reached.
        """
        import time

        start = time.time()
        while True:
            remaining = max(0, timeout - (time.time() - start))
            if remaining <= 0:
                raise asyncio.TimeoutError("Timed out waiting for websocket event")
            msg = await asyncio.wait_for(self._queue.get(), timeout=remaining)
            if predicate is None or predicate(msg):
                return msg
