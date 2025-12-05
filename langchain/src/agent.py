"""
LangChain agent implementation.
Creates and executes ReAct agent with Ollama LLM and MCP tools.
"""

from typing import Any, Optional

from langchain_core.callbacks import BaseCallbackHandler
from loguru import logger

from .collector import get_collector, reset_collector
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


# Private: robust answer extraction across various LangChain/LLM result shapes
def _extract_answer(res: Any) -> str:
    """Return the best-effort text answer from a model/agent result.

    Handles several common result shapes produced by different LangChain
    wrappers and LLM integrations: dicts with `output`/`text` keys,
    chat `messages` lists (objects with `.content` or dicts with `content`),
    `choices`, or arbitrary objects.
    """
    if not res:
        return "No answer generated"

    # If result is dict-like, check common keys first
    if isinstance(res, dict):
        for key in ("output", "text", "answer", "result"):
            if key in res and res[key]:
                return str(res[key])

        # Handle message-based responses (list of message objects or dicts)
        msgs = res.get("messages") or res.get("message") or res.get("choices")
        if msgs:
            try:
                if isinstance(msgs, dict):
                    msgs = [msgs]
                parts: list[str] = []
                for m in msgs:
                    # Prefer attribute-style content (e.g., AIMessage.content)
                    content = getattr(m, "content", None)
                    if content is not None:
                        parts.append(str(content))
                        continue
                    # Support dict-style message objects
                    if isinstance(m, dict) and "content" in m and m["content"]:
                        parts.append(str(m["content"]))
                        continue
                    # Fallback to stringifying the item
                    parts.append(str(m))
                text = "\n".join([p for p in parts if p]).strip()
                if text:
                    return text
            except Exception:
                # Fall through to final fallback
                pass

    # Fallback to string conversion for other result shapes
    try:
        return str(res)
    except Exception:
        return "No answer generated"


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
) -> Any:
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
    # Build the chat model instance (ChatOllama) with callbacks
    try:
        from langchain_ollama import ChatOllama  # type: ignore
    except Exception:
        try:
            from langchain_ollama.chat_models import ChatOllama  # type: ignore
        except Exception:
            raise ImportError(
                "ChatOllama integration not found. Install `langchain-ollama` or a compatible package."
            )

    llm = ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=temperature,
        verbose=verbose,
        callbacks=callbacks,
    )

    # Create tools and prompt
    tools = create_langchain_tools(mcp_client)
    # Prompt template is defined in `REACT_PROMPT` and will be provided
    # as the `system_prompt` to `create_agent` below.

    # LangChain v1: use create_agent (no fallbacks); this repo targets v1.
    try:
        from langchain.agents import create_agent  # type: ignore

        agent_executor = create_agent(
            model=llm, tools=tools, system_prompt=REACT_PROMPT
        )
        logger.info(f"Created research agent via create_agent (model={OLLAMA_MODEL})")
        return agent_executor
    except Exception as exc:
        raise ImportError(
            "LangChain v1 `create_agent` API is required. Install langchain>=1.0.0."
        ) from exc


# ============================================================================
# Agent Execution
# ============================================================================


async def execute_research_task(
    question: str,
    mcp_client: MCPClient,
    callbacks: Optional[list[BaseCallbackHandler]] = None,
    seed_url: Optional[str] = None,
    # Additional configuration options forwarded from the API layer.
    # Some (like max_depth, max_pages, time_budget) are not used by the
    # LangChain agent directly but are accepted here for interface
    # compatibility. Unknown options are ignored.
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

        # Extract agent-related kwargs we actually support; ignore the rest
        agent_kwargs: dict[str, Any] = {}
        for key in ("temperature", "max_iterations", "max_execution_time", "verbose"):
            if key in kwargs:
                agent_kwargs[key] = kwargs[key]

        # Create agent
        agent_executor = create_research_agent(
            mcp_client,
            callbacks=callbacks,
            **agent_kwargs,
        )

        # Prepare input
        agent_input = {"input": question}
        if seed_url:
            agent_input["input"] = f"{question}\n\nStart your research at: {seed_url}"

        logger.info(f"Executing research task: {question[:100]}...")

        # Execute agent
        result = await agent_executor.ainvoke(agent_input)
        answer = _extract_answer(result)

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
