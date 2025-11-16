"""
LangChain agent implementation.
Creates and executes ReAct agent with Ollama LLM and MCP tools.
"""

from typing import Any, Optional

from langchain_core.callbacks import BaseCallbackHandler
from loguru import logger

from .config import (
    AGENT_TEMPERATURE,
    AGENT_VERBOSE,
    MAX_EXECUTION_TIME,
    MAX_ITERATIONS,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)
from .mcp_client import MCPClient
from .tools import create_langchain_tools
from .collector import get_collector, reset_collector


# ============================================================================
# ReAct Prompt Template
# ============================================================================

REACT_PROMPT = """You are a web research assistant that helps users find information online.

You have access to browser automation tools to navigate websites, extract content, and capture screenshots.

IMPORTANT GUIDELINES:
1. Always start by navigating to a relevant website (use navigate_to)
2. After navigation, extract the page content (use get_page_content)
3. Read the content carefully and determine if it answers the question
4. If you need more information, navigate to another page
5. Capture screenshots when visual evidence would be helpful
6. Be thorough but efficient - respect rate limits
7. Cite your sources by providing the URLs you visited

TOOLS:
{tools}

TOOL NAMES: {tool_names}

QUESTION: {input}

THOUGHT PROCESS:
{agent_scratchpad}

Remember: Think step-by-step and explain your reasoning. When you have enough information to answer the question, provide a comprehensive answer with citations.
"""


# ============================================================================
# Agent Creation
# ============================================================================


def create_research_agent(
    mcp_client: MCPClient,
    callbacks: Optional[list[BaseCallbackHandler]] = None,
    temperature: float = AGENT_TEMPERATURE,
    max_iterations: int = MAX_ITERATIONS,
    max_execution_time: int = MAX_EXECUTION_TIME,
    verbose: bool = AGENT_VERBOSE,
) -> any:
    """
    Create a ReAct agent for web research.

    Args:
        mcp_client: MCP client for browser automation
        callbacks: Optional callback handlers for streaming
        temperature: LLM temperature (0.0 = deterministic)
        max_iterations: Maximum agent iterations
        max_execution_time: Maximum execution time in seconds
        verbose: Enable verbose logging

    Returns:
        Configured AgentExecutor
    """
    # Create LLM (import locally to reduce import-time coupling)
    from langchain_community.chat_models import ChatOllama  # type: ignore

    llm = ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=temperature,
        verbose=verbose,
    )

    # Create tools
    tools = create_langchain_tools(mcp_client)

    # Create prompt (import locally to support multiple LC versions)
    try:
        from langchain.prompts import PromptTemplate  # type: ignore
    except Exception:
        from langchain_core.prompts import PromptTemplate  # type: ignore

    prompt = PromptTemplate.from_template(REACT_PROMPT)

    # Create agent (import locally for compatibility across LC versions)
    try:
        from langchain.agents import create_react_agent  # type: ignore
    except Exception:  # Fallback for older/newer versions
        from langchain.agents.react.base import create_react_agent  # type: ignore

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    # Create executor
    # Construct an AgentExecutor without importing the class directly (API varies by version)
    agent_executor = type("AgentExecutorShim", (), {})()
    # Use factory function to build a real executor via the public API
    # Newer LangChain exposes AgentExecutor in langchain.agents, but to support a wider
    # range of versions we import only the factory and build via its return type.
    try:
        from langchain.agents import AgentExecutor as _AgentExecutor  # type: ignore
    except Exception:
        # In some versions, AgentExecutor lives under different paths; attempt a fallback
        from langchain.agents.agent import AgentExecutor as _AgentExecutor  # type: ignore

    agent_executor = _AgentExecutor(
        agent=agent,
        tools=tools,
        callbacks=callbacks,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        verbose=verbose,
        handle_parsing_errors=True,  # Automatic retry on parsing errors
        early_stopping_method="generate",  # Generate final answer on max iterations
        return_intermediate_steps=True,
    )

    logger.info(
        f"Created research agent (model={OLLAMA_MODEL}, max_iterations={max_iterations})"
    )

    return agent_executor


# ============================================================================
# Agent Execution
# ============================================================================


async def execute_research_task(
    question: str,
    mcp_client: MCPClient,
    callbacks: Optional[list[BaseCallbackHandler]] = None,
    seed_url: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """
    Execute a research task using the agent.

    Args:
        question: Research question
        mcp_client: MCP client for browser automation
        callbacks: Optional callback handlers
        seed_url: Optional starting URL
        **kwargs: Additional agent configuration

    Returns:
        Dict with answer, citations, and metadata
    """
    try:
        # Reset collector for this run
        reset_collector()

        # Create agent
        agent_executor = create_research_agent(
            mcp_client, callbacks=callbacks, **kwargs
        )

        # Prepare input
        agent_input = {"input": question}
        if seed_url:
            agent_input["input"] = f"{question}\n\nStart your research at: {seed_url}"

        logger.info(f"Executing research task: {question[:100]}...")

        # Execute agent
        result = await agent_executor.ainvoke(agent_input)

        # Extract answer
        answer = result.get("output", "No answer generated")

        # Gather artifacts
        collector = get_collector()
        citations = [
            {"url": c.url, "title": c.title, "source": c.source, **(c.extra or {})}
            for c in collector.citations
        ]
        screenshots = list(collector.screenshots)

        logger.info(
            f"Research task completed: {len(answer)} chars, {len(citations)} citations, {len(screenshots)} screenshots"
        )

        return {
            "status": "success",
            "answer": answer,
            "citations": citations,
            "screenshots": screenshots,
            "metadata": {
                "iterations": len(result.get("intermediate_steps", [])),
                "question": question,
            },
        }

    except Exception as e:
        logger.error(f"Research task failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "answer": None,
            "citations": [],
            "screenshots": [],
            "metadata": {},
        }
