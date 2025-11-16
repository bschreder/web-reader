"""Unit tests for agent module."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent import create_research_agent, execute_research_task


@pytest.fixture(autouse=True)
def stub_langchain_modules(monkeypatch):
    """Stub LangChain imports used inside create_research_agent to avoid heavy deps."""
    import types, sys

    # Stub ChatOllama
    chat_models = types.ModuleType("chat_models")

    class DummyChatOllama:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    chat_models.ChatOllama = DummyChatOllama
    langchain_community = types.ModuleType("langchain_community")
    langchain_community.chat_models = chat_models
    monkeypatch.setitem(sys.modules, "langchain_community", langchain_community)
    monkeypatch.setitem(sys.modules, "langchain_community.chat_models", chat_models)

    # Stub PromptTemplate
    prompts_mod = types.ModuleType("prompts")

    class DummyPromptTemplate:
        @classmethod
        def from_template(cls, template: str):
            return {"template": template}

    prompts_mod.PromptTemplate = DummyPromptTemplate
    langchain_pkg = types.ModuleType("langchain")
    langchain_pkg.prompts = prompts_mod
    monkeypatch.setitem(sys.modules, "langchain", langchain_pkg)
    monkeypatch.setitem(sys.modules, "langchain.prompts", prompts_mod)

    # Stub create_react_agent and AgentExecutor
    agents_mod = types.ModuleType("agents")

    def create_react_agent(llm, tools, prompt):
        return {"llm": llm, "tools": tools, "prompt": prompt}

    class AgentExecutor:
        def __init__(self, agent, tools, callbacks=None, **kwargs):
            self._agent = agent
            self._tools = tools
            self._callbacks = callbacks or []

        async def ainvoke(self, inputs):
            return {"output": "stub", "intermediate_steps": []}

    agents_mod.create_react_agent = create_react_agent
    agents_mod.AgentExecutor = AgentExecutor
    monkeypatch.setitem(sys.modules, "langchain.agents", agents_mod)


class TestCreateAgent:
    """Test agent creation and configuration."""

    def test_creates_agent_with_mcp_client(self, mock_mcp_client):
        """Test that agent is created with proper configuration."""
        agent = create_research_agent(mock_mcp_client)

        assert agent is not None
        # Agent should be AgentExecutor
        assert hasattr(agent, "ainvoke") or hasattr(agent, "invoke")

    def test_creates_agent_with_custom_params(self, mock_mcp_client):
        """Test agent creation with custom parameters."""
        agent = create_research_agent(
            mock_mcp_client,
            temperature=0.5,
            max_iterations=10,
            verbose=True,
        )

        # Should create agent with custom config
        assert agent is not None


class TestExecuteResearchTask:
    """Test research task execution."""

    @pytest.mark.asyncio
    async def test_execute_simple_task(self, mock_mcp_client, mocker):
        """Test executing a simple research task."""
        mock_agent_executor = MagicMock()
        mock_agent_executor.ainvoke = AsyncMock(
            return_value={
                "output": "Paris is the capital of France.",
                "intermediate_steps": [],
            }
        )

        mocker.patch(
            "src.agent.create_research_agent", return_value=mock_agent_executor
        )

        result = await execute_research_task(
            question="What is the capital of France?",
            mcp_client=mock_mcp_client,
        )

        assert result["status"] == "success"
        assert "answer" in result

    @pytest.mark.asyncio
    async def test_execute_task_with_seed_url(self, mock_mcp_client, mocker):
        """Test executing task with seed URL."""
        mock_agent_executor = MagicMock()
        mock_agent_executor.ainvoke = AsyncMock(
            return_value={
                "output": "Test answer",
                "intermediate_steps": [],
            }
        )

        mocker.patch(
            "src.agent.create_research_agent", return_value=mock_agent_executor
        )

        result = await execute_research_task(
            question="What is this page about?",
            mcp_client=mock_mcp_client,
            seed_url="https://example.com",
        )

        assert result["status"] == "success"
        assert "answer" in result

    @pytest.mark.asyncio
    async def test_execute_task_with_limits(self, mock_mcp_client, mocker):
        """Test executing task with depth and page limits."""
        mock_agent_executor = MagicMock()
        mock_agent_executor.ainvoke = AsyncMock(
            return_value={
                "output": "Test answer",
                "intermediate_steps": [],
            }
        )

        mocker.patch(
            "src.agent.create_research_agent", return_value=mock_agent_executor
        )

        result = await execute_research_task(
            question="Test question?",
            mcp_client=mock_mcp_client,
            max_depth=2,
            max_pages=5,
        )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_execute_task_handles_errors(self, mock_mcp_client, mocker):
        """Test error handling in task execution."""
        mock_agent_executor = MagicMock()
        mock_agent_executor.ainvoke = AsyncMock(side_effect=Exception("Test error"))

        mocker.patch(
            "src.agent.create_research_agent", return_value=mock_agent_executor
        )

        result = await execute_research_task(
            question="Test question?",
            mcp_client=mock_mcp_client,
        )

        assert result["status"] == "error"
        assert "error" in result
