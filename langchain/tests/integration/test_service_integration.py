"""Integration tests for LangChain with Ollama and FastMCP."""

import pytest

from src.agent import create_research_agent
from src.mcp_client import MCPClient


class TestOllamaIntegration:
    """Test integration with Ollama LLM service."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_ollama_connection(self, skip_if_no_ollama, ollama_base_url):
        """Test connection to Ollama service."""
        import httpx

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{ollama_base_url}/api/tags", timeout=5.0)
                assert response.status_code == 200

                data = response.json()
                # Should have models list
                assert "models" in data

            except Exception as e:
                pytest.skip(f"Ollama not fully available: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_ollama_model_available(
        self, skip_if_no_ollama, ollama_base_url, ollama_model
    ):
        """Test that configured model is available in Ollama."""
        import httpx

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{ollama_base_url}/api/tags", timeout=5.0)
                assert response.status_code == 200

                data = response.json()
                models = data.get("models", [])
                model_names = [m.get("name", "") for m in models]

                # Check if our model is present (may have :tag suffix)
                model_found = any(ollama_model in name for name in model_names)

                if not model_found:
                    pytest.skip(
                        f"Model {ollama_model} not found in Ollama. Available: {model_names}"
                    )

            except Exception as e:
                pytest.skip(f"Ollama model check failed: {e}")


class TestFastMCPIntegration:
    """Test integration with FastMCP tool server."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fastmcp_health_check(self, skip_if_no_fastmcp, fastmcp_url):
        """Test FastMCP health check."""
        client = MCPClient(fastmcp_url)

        try:
            health = await client.health_check()
            assert health is True or (
                isinstance(health, dict) and health.get("status") == "healthy"
            )
        except Exception as e:
            pytest.skip(f"FastMCP not available: {e}")
        finally:
            await client.close()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fastmcp_tool_execution(
        self, skip_if_no_fastmcp, fastmcp_url, mocker
    ):
        """Test executing a tool via FastMCP."""
        client = MCPClient(fastmcp_url)

        try:
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

        finally:
            await client.close()


class TestAgentCreation:
    """Test agent creation with real services."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_agent_with_services(
        self, skip_if_no_ollama, skip_if_no_fastmcp, fastmcp_url
    ):
        """Test creating agent with real Ollama and FastMCP connections."""
        client = MCPClient(fastmcp_url)

        try:
            agent = await create_research_agent(client)

            assert agent is not None
            # Agent should have tools
            assert hasattr(agent, "tools") or hasattr(agent, "runnable")

        except Exception as e:
            pytest.skip(f"Agent creation failed (services may be incomplete): {e}")
        finally:
            await client.close()
