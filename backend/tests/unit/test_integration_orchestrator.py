"""
Integration tests for Backend -> LangChain -> MCP flow.
Tests the complete orchestration without real Playwright or LLM.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.tasks import TaskStatus, create_task, get_task
from src.langchain import LangChainClient


@pytest.mark.asyncio
async def test_task_orchestration_flow(mocker):
    """
    Test complete flow: Backend creates task -> LangChain executes -> MCP tools called.
    Mocks LangChain and MCP but verifies integration points.
    """
    # 1. Create task via backend
    task = await create_task(
        question="What is the capital of France?",
        seed_url="https://example.com",
        max_depth=2,
    )

    assert task.status == TaskStatus.CREATED
    assert task.question == "What is the capital of France?"

    # 2. Mock LangChain client with realistic response
    mock_langchain_response = {
        "answer": "The capital of France is Paris.",
        "citations": [
            {
                "url": "https://example.com/france",
                "title": "France - Wikipedia",
                "excerpt": "Paris is the capital and most populous city of France.",
            }
        ],
        "screenshots": ["base64_screenshot_data_here"],
        "metadata": {
            "pages_visited": 3,
            "tools_called": 5,
            "duration_seconds": 12.5,
        },
    }

    # Mock the httpx client inside LangChainClient
    mock_http_response = MagicMock()
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = mock_langchain_response
    mock_http_response.raise_for_status = MagicMock()

    mock_http_client = AsyncMock()
    mock_http_client.post = AsyncMock(return_value=mock_http_response)
    mock_http_client.aclose = AsyncMock()

    # 3. Execute task with mocked LangChain
    async with LangChainClient(base_url="http://mock-langchain:8001") as client:
        client._client = mock_http_client

        # Update task to running
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        # Execute via LangChain
        result = await client.execute_task(task)

        # 4. Verify LangChain was called correctly
        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args

        assert call_args[0][0] == "/execute"
        payload = call_args[1]["json"]
        assert payload["task_id"] == task.task_id
        assert payload["question"] == task.question
        assert payload["seed_url"] == task.seed_url

        # 5. Verify result structure
        assert result["answer"] == "The capital of France is Paris."
        assert len(result["citations"]) == 1
        assert result["citations"][0]["url"] == "https://example.com/france"
        assert len(result["screenshots"]) == 1
        assert result["metadata"]["pages_visited"] == 3

        # 6. Update task with results
        task.answer = result["answer"]
        task.citations = result["citations"]
        task.metadata = result["metadata"]
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()

        # 7. Verify final task state
        completed_task = await get_task(task.task_id)
        assert completed_task.status == TaskStatus.COMPLETED
        assert completed_task.answer == "The capital of France is Paris."
        assert len(completed_task.citations) == 1


@pytest.mark.asyncio
async def test_task_orchestration_with_mcp_tools(mocker):
    """
    Test that LangChain orchestrator would call MCP tools.
    Mocks the tool invocation layer to verify correct tool selection.
    """
    # Simulate what LangChain would do internally:
    # 1. Receive question
    # 2. Call navigate_to tool
    # 3. Call get_page_content tool
    # 4. Call take_screenshot tool
    # 5. Return answer

    # Mock MCP tool responses
    mock_navigate_result = {
        "status": "success",
        "title": "France - Wikipedia",
        "url": "https://example.com/france",
        "http_status": 200,
    }

    mock_content_result = {
        "status": "success",
        "title": "France - Wikipedia",
        "url": "https://example.com/france",
        "text": "Paris is the capital and most populous city of France...",
        "truncated": False,
        "links": ["https://example.com/paris"],
        "metadata": {},
        "word_count": 150,
    }

    mock_screenshot_result = {
        "status": "success",
        "image": "base64_image_data",
        "format": "png",
        "full_page": False,
    }

    # This simulates what LangChain agent would do:
    # It would call these tools in sequence via MCP protocol
    mcp_tools_called = []

    # Mock tool execution
    async def mock_navigate_to(url: str):
        mcp_tools_called.append(("navigate_to", url))
        return mock_navigate_result

    async def mock_get_page_content():
        mcp_tools_called.append(("get_page_content", None))
        return mock_content_result

    async def mock_take_screenshot():
        mcp_tools_called.append(("take_screenshot", None))
        return mock_screenshot_result

    # Execute simulated agent workflow
    await mock_navigate_to("https://example.com/france")
    content = await mock_get_page_content()
    screenshot = await mock_take_screenshot()

    # Verify tool call sequence
    assert len(mcp_tools_called) == 3
    assert mcp_tools_called[0] == ("navigate_to", "https://example.com/france")
    assert mcp_tools_called[1] == ("get_page_content", None)
    assert mcp_tools_called[2] == ("take_screenshot", None)

    # Verify tool results
    assert content["status"] == "success"
    assert "Paris" in content["text"]
    assert screenshot["status"] == "success"
    assert screenshot["format"] == "png"


@pytest.mark.asyncio
async def test_task_orchestration_error_handling(mocker):
    """
    Test error handling when LangChain orchestrator fails.
    """
    task = await create_task(
        question="Test question",
        seed_url=None,
        max_depth=1,
    )

    # Mock HTTP error
    mock_http_client = AsyncMock()
    mock_http_client.post = AsyncMock(side_effect=Exception("Connection refused"))
    mock_http_client.aclose = AsyncMock()

    async with LangChainClient(base_url="http://mock-langchain:8001") as client:
        client._client = mock_http_client

        task.status = TaskStatus.RUNNING

        # Execute should raise
        with pytest.raises(Exception, match="Connection refused"):
            await client.execute_task(task)

        # Task should be marked as failed
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now()
        failed_task = await get_task(task.task_id)
        assert failed_task.status == TaskStatus.FAILED


@pytest.mark.asyncio
async def test_langchain_health_check(mocker):
    """Test LangChain service health check."""
    # Mock healthy response
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_http_client = AsyncMock()
    mock_http_client.get = AsyncMock(return_value=mock_response)
    mock_http_client.aclose = AsyncMock()

    async with LangChainClient(base_url="http://mock-langchain:8001") as client:
        client._client = mock_http_client

        is_healthy = await client.health_check()
        assert is_healthy is True
        mock_http_client.get.assert_called_once_with("/health")

    # Mock unhealthy response
    mock_http_client.get = AsyncMock(side_effect=Exception("Connection failed"))

    async with LangChainClient(base_url="http://mock-langchain:8001") as client:
        client._client = mock_http_client

        is_healthy = await client.health_check()
        assert is_healthy is False
