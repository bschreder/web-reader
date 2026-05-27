"""Tests for agent execution and artifact aggregation."""

import pytest

from src.collector import reset_collector, get_collector


class FakeAgentExecutor:
    def __init__(self, output: str = "Final answer", steps: int = 2):
        self.output = output
        self.steps = steps

    async def ainvoke(self, _input):
        # Simulate minimal AgentExecutor result shape
        return {
            "output": self.output,
            "intermediate_steps": [None] * self.steps,
        }


@pytest.mark.asyncio
async def test_execute_research_task_aggregates_artifacts(monkeypatch, mock_mcp_client):
    from src import agent as agent_mod

    # Patch create_research_agent to return a fake executor
    monkeypatch.setattr(
        agent_mod,
        "create_research_agent",
        lambda *a, **k: FakeAgentExecutor("Answer", 3),
    )
    # Prevent execute_research_task from clearing our seeded artifacts
    monkeypatch.setattr(agent_mod, "reset_collector", lambda: None)

    # Seed collector with artifacts to simulate tool effects
    reset_collector()
    coll = get_collector()
    coll.add_citation(
        "https://example.com", title="Example Domain", source="navigate_to"
    )
    coll.add_screenshot("base64_img")

    result = await agent_mod.execute_research_task(
        question="What is Example Domain?",
        mcp_client=mock_mcp_client,
    )

    assert result["status"] == "success"
    assert result["answer"] == "Answer"
    assert result["metadata"]["iterations"] == 3
    assert any(c.get("url") == "https://example.com" for c in result["citations"])
    assert "base64_img" in result["screenshots"]
