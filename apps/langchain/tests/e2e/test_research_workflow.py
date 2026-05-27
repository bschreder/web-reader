"""End-to-end tests for LangChain research workflows."""

import pytest

from src.agent import execute_research_task
from src.callbacks import WebSocketCallbackHandler
from src.mcp_client import MCPClient

from recorder_websocket import RecorderWebSocket


@pytest.mark.timeout(300)
class TestResearchWorkflow:
    """Test complete research workflows."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_simple_research_task(
        self,
        fastmcp_url,
        test_question_simple,
    ):
        """Test executing a simple research task end-to-end."""
        try:
            async with MCPClient(fastmcp_url) as client:
                # Create recorder WebSocket for callbacks (captures events)
                recorder = RecorderWebSocket()
                callback = WebSocketCallbackHandler(recorder)
            # Execute research task
            result = await execute_research_task(
                question=test_question_simple,
                mcp_client=client,
                callbacks=[callback],
                max_depth=1,
                max_pages=2,
                time_budget=30,
            )

            # Should get some result
            assert result is not None
            assert isinstance(result, dict)

            # Check for expected fields
            assert "status" in result or "answer" in result or "output" in result

            # Ensure the task did not finish with an error status
            assert result.get("status") != "error", (
                f"Research task returned error status: {result.get('error') or result}"
            )

            # Ensure at least one websocket event was emitted
            assert len(recorder.messages) > 0, "No websocket events were recorded"
            # At minimum expect an agent lifecycle event such as thinking/tool_call/finish
            types = {m.get("type") for m in recorder.messages}
            assert types & {
                "agent:thinking",
                "agent:tool_call",
                "agent:finish",
                "agent:thought",
                "agent:tool_result",
            }, f"Unexpected event types: {types}"
        except Exception as e:
            pytest.fail(f"Test failed with exception: {e}")

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_research_with_seed_url(
        self,
        fastmcp_url,
        test_question_with_url,
    ):
        """Test research task with seed URL provided."""
        async with MCPClient(fastmcp_url) as client:
            recorder = RecorderWebSocket()
            callback = WebSocketCallbackHandler(recorder)

            result = await execute_research_task(
                question=test_question_with_url,
                seed_url="https://example.com",
                mcp_client=client,
                callbacks=[callback],
                max_depth=1,
                max_pages=1,
                time_budget=20,
            )

            assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_research_artifacts_collected(
        self,
        fastmcp_url,
        test_question_simple,
    ):
        """Test that research artifacts are collected during execution."""
        from src.collector import get_collector, reset_collector

        # Reset collector before test
        reset_collector()

        async with MCPClient(fastmcp_url) as client:
            recorder = RecorderWebSocket()
            callback = WebSocketCallbackHandler(recorder)

            await execute_research_task(
                question=test_question_simple,
                mcp_client=client,
                callbacks=[callback],
                max_depth=1,
                max_pages=2,
                time_budget=25,
            )

            # Check if artifacts were collected
            collector = get_collector()

            # Should have some citations from page visits
            assert collector.citations is not None
            assert isinstance(collector.citations, list)

        # Reset after test
        reset_collector()

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_error_handling_invalid_url(
        self,
        fastmcp_url,
    ):
        """Test error handling when given invalid URL."""
        async with MCPClient(fastmcp_url) as client:
            recorder = RecorderWebSocket()
            callback = WebSocketCallbackHandler(recorder)
            result = await execute_research_task(
                question="What is this website about?",
                seed_url="https://this-domain-definitely-does-not-exist-12345.com",
                mcp_client=client,
                callbacks=[callback],
                max_depth=1,
                max_pages=1,
                time_budget=15,
            )

            # Should handle error gracefully
            assert result is not None
            # May contain error message or partial result
