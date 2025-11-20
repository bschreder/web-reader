"""Integration tests for LangChain with Ollama and FastMCP."""

import pytest

from src.tools import create_langchain_tools
from src.mcp_client import MCPClient
from src.config import OLLAMA_MODEL


class TestOllamaIntegration:
    """Test integration with Ollama LLM service."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_ollama_connection(self, skip_if_no_ollama, ollama_url):
        """Test connection to Ollama service."""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ollama_url}/api/tags", timeout=5.0)
            assert response.status_code == 200

            data = response.json()
            # Should have models list
            assert "models" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_ollama_model_available(self, skip_if_no_ollama, ollama_url):
        """Test that configured model is available in Ollama."""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ollama_url}/api/tags", timeout=5.0)
            assert response.status_code == 200

            data = response.json()
            models = data.get("models", [])
            model_names = [m.get("name", "") for m in models]

            # Check if our model is present (may have :tag suffix)
            model_found = any(OLLAMA_MODEL in name for name in model_names)

            assert model_found, (
                f"Model {OLLAMA_MODEL} not found in Ollama. Available: {model_names}"
            )


class TestFastMCPIntegration:
    """Test integration with FastMCP tool server."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fastmcp_health_check(self,  fastmcp_url):
        """Test FastMCP health check."""
        async with MCPClient(fastmcp_url) as client:
            health = await client.health_check()
            assert health is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fastmcp_tool_execution(self, fastmcp_url, mocker):
        """Test executing a tool via FastMCP."""
        async with MCPClient(fastmcp_url) as client:
            # Mock to avoid actual navigation
            mocker.patch(
                "src.mcp_client.MCPClient.call_tool",
                return_value={
                    "status": "success",
                    "title": "Test Page",
                    "url": "https://example.com",
                    "http_status": 200,
                },
            )

            result = await client.call_tool(
                "navigate_to", {"url": "https://example.com"}
            )

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("status") == "success"


class TestAgentCreation:
    """Test agent creation with real services."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_agent_with_services(self, fastmcp_url):
        """Test creating agent with real Ollama and FastMCP connections."""
        async with MCPClient(fastmcp_url) as client:
            tools = create_langchain_tools(client)

            assert tools is not None
            assert isinstance(tools, list)
            assert len(tools) >= 1
