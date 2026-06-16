"""
LangChain agent implementation.
Creates and executes ReAct agent with Ollama LLM and MCP tools.
"""

import asyncio
import time
from collections.abc import Mapping
from typing import Any, Optional

from langchain_core.callbacks import AsyncCallbackHandler, BaseCallbackHandler
from langchain_core.outputs import LLMResult
from loguru import logger

from .collector import get_collector, reset_collector
from .config import (
    AGENT_TEMPERATURE,
    AGENT_VERBOSE,
    DEBUG_AGENT_HEARTBEAT_SECONDS,
    DEBUG_AGENT_TRACE,
    MAX_EXECUTION_TIME,
    MAX_ITERATIONS,
    OLLAMA_BASE_URL,
    OLLAMA_DISABLE_STREAMING,
    OLLAMA_HTTP_TIMEOUT_SECONDS,
    OLLAMA_MODEL,
    OLLAMA_NUM_PREDICT,
    OLLAMA_REASONING,
)
from .mcp_client import MCPClient
from .tools import create_langchain_tools

# ============================================================================
# ReAct Prompt Template
# ============================================================================

REACT_PROMPT = """You are a web research assistant that helps users find information online.

You have access to powerful web search and browser automation tools.

RESEARCH WORKFLOW:
For questions about current events, facts, or specific topics:
1. Start with search_for_question to find relevant websites using keywords from the QUESTION
2. Review search results and identify promising URLs
3. Use navigate_to to visit the most relevant pages
4. Use get_page_content to extract information
5. If evidence is thin, use get_page_content_chunk to read deeper sections deterministically
6. Use extract_links_from_page to find related pages for deeper research
7. Use take_screenshot to capture visual evidence when needed

CRITICAL SEARCH GUIDELINES:
- ALWAYS use keywords directly from the QUESTION when calling search_for_question
- Do NOT deviate from the original question topic during search
- Extract key terms and search entities from the QUESTION before searching
- If given a seed_url, navigate there first instead of searching
- Never search for topics unrelated to the QUESTION provided
- Verify search queries contain words or entities from the original QUESTION

EXAMPLE:
If QUESTION is "What is the PE ratio of CCL?", search for "CCL PE ratio" or "Carnival Corporation price earnings ratio"
If QUESTION is "How can I prevent resizing using Tailwind?", search for "tailwind resize none" or "tailwindcss disable resize textarea"

IMPORTANT GUIDELINES:
1. If given a seed_url, navigate there first and explore linked content instead of searching
2. Always maintain focus on the original QUESTION throughout the research
3. Verify information by checking multiple sources when possible
4. Extract links from pages to follow research trails efficiently
5. Respect rate limits - add delays between requests to the same domain
6. Cite all sources by including the URLs you visited
7. Be thorough but efficient - stop when you have reliable answers

TOOLS:
{tools}

TOOL NAMES: {tool_names}

QUESTION: {input}

THOUGHT PROCESS:
{agent_scratchpad}

Remember: Focus on the QUESTION, use question keywords for searches, navigate to sources, extract information, and provide comprehensive answers with citations.
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
    if isinstance(res, Mapping):
        res_dict = dict(res)
        for key in ("output", "text", "answer", "result"):
            if key in res_dict and res_dict[key]:
                return str(res_dict[key])

        # Handle message-based responses (list of message objects or dicts)
        msgs = (
            res_dict.get("messages")
            or res_dict.get("message")
            or res_dict.get("choices")
        )
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
                return "No answer generated"
            except Exception:
                # Fall through to final fallback
                pass

    # Fallback to string conversion for other result shapes
    try:
        return str(res)
    except Exception:
        return "No answer generated"


async def _invoke_with_timeout(
    agent_executor: Any,
    agent_input: dict[str, Any],
    timeout_seconds: int,
    run_config: Optional[dict[str, Any]] = None,
) -> Any:
    """Invoke the agent with an explicit timeout guard.

    We keep this timeout in-process so long-running model calls terminate
    predictably instead of hanging until the outer API timeout.
    """
    async with asyncio.timeout(timeout_seconds):
        if run_config:
            return await agent_executor.ainvoke(agent_input, config=run_config)
        return await agent_executor.ainvoke(agent_input)


class _DebugTraceCallback(AsyncCallbackHandler):
    """DEBUG: Emits stage-level callbacks for LLM and tool boundaries."""

    async def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        logger.warning(
            "DEBUG: callback llm_start prompts={} run_id={}",
            len(prompts),
            kwargs.get("run_id"),
        )

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        logger.warning("DEBUG: callback llm_end run_id={}", kwargs.get("run_id"))

    async def on_tool_start(
        self, serialized: dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        logger.warning(
            "DEBUG: callback tool_start tool={} run_id={}",
            serialized.get("name", "unknown"),
            kwargs.get("run_id"),
        )

    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        logger.warning("DEBUG: callback tool_end run_id={}", kwargs.get("run_id"))

    async def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        logger.warning(
            "DEBUG: callback tool_error run_id={} error={}",
            kwargs.get("run_id"),
            str(error),
        )


async def _debug_heartbeat(label: str) -> None:
    """DEBUG: Periodically log that an awaited operation is still in progress."""
    while True:
        logger.warning(
            "DEBUG: agent heartbeat - {} still running after {}s interval",
            label,
            DEBUG_AGENT_HEARTBEAT_SECONDS,
        )
        await asyncio.sleep(DEBUG_AGENT_HEARTBEAT_SECONDS)


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
    request_timeout_seconds: float | None = None,
    include_search_and_links: bool = True,
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

    llm_callbacks = list(callbacks or [])
    if DEBUG_AGENT_TRACE:
        llm_callbacks.append(_DebugTraceCallback())

    http_timeout_seconds = float(
        request_timeout_seconds
        if request_timeout_seconds is not None
        else OLLAMA_HTTP_TIMEOUT_SECONDS
    )

    llm = ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=temperature,
        verbose=verbose,
        callbacks=llm_callbacks,
        disable_streaming=OLLAMA_DISABLE_STREAMING,
        num_predict=OLLAMA_NUM_PREDICT,
        reasoning=OLLAMA_REASONING,
        client_kwargs={"timeout": http_timeout_seconds},
        sync_client_kwargs={"timeout": http_timeout_seconds},
        async_client_kwargs={"timeout": http_timeout_seconds},
    )

    if DEBUG_AGENT_TRACE:
        logger.warning(
            "DEBUG: ChatOllama configured model={} http_timeout={}s disable_streaming={} num_predict={} reasoning={}",
            OLLAMA_MODEL,
            http_timeout_seconds,
            OLLAMA_DISABLE_STREAMING,
            OLLAMA_NUM_PREDICT,
            OLLAMA_REASONING,
        )

    # Create tools and prompt
    # Include search and link tools for full UC support
    tools = create_langchain_tools(
        mcp_client, include_search_and_links=include_search_and_links
    )
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

        effective_timeout = int(
            agent_kwargs.get("max_execution_time", MAX_EXECUTION_TIME)
        )
        if kwargs.get("time_budget"):
            try:
                effective_timeout = min(effective_timeout, int(kwargs["time_budget"]))
            except (TypeError, ValueError):
                pass

        # Apply agent timeout policy bounds (30s minimum, MAX_EXECUTION_TIME cap).
        effective_timeout = max(30, min(MAX_EXECUTION_TIME, effective_timeout))
        requested_max_iterations = int(
            agent_kwargs.get("max_iterations", MAX_ITERATIONS)
        )
        # Keep iteration bounds sane to avoid long runaway loops.
        requested_max_iterations = max(1, min(50, requested_max_iterations))
        # Budget-aware cap: observed LLM+tool loop is often ~45s.
        budget_iteration_cap = max(3, effective_timeout // 45)
        effective_max_iterations = min(requested_max_iterations, budget_iteration_cap)

        # Create agent
        create_started = time.perf_counter()
        if DEBUG_AGENT_TRACE:
            logger.warning(
                "DEBUG: creating research agent (timeout={}s, seed_url={})",
                effective_timeout,
                bool(seed_url),
            )

        agent_executor = create_research_agent(
            mcp_client,
            callbacks=callbacks,
            request_timeout_seconds=float(effective_timeout),
            include_search_and_links=not bool(seed_url),
            **agent_kwargs,
        )

        if DEBUG_AGENT_TRACE:
            logger.warning(
                "DEBUG: agent created in {:.2f}s",
                time.perf_counter() - create_started,
            )

        # Prepare input and embed constraints to guide the agent's tool usage
        agent_input = {"input": question}
        constraints: list[str] = []
        if seed_url:
            constraints.append(f"Seed URL: {seed_url}")

        # UC-02/UC-03 constraints forwarded from API
        for key in (
            "same_domain_only",
            "allow_external_links",
            "max_depth",
            "max_pages",
            "time_budget",
            "search_engine",
            "max_results",
            "safe_mode",
        ):
            if key in kwargs and kwargs[key] is not None:
                constraints.append(f"{key}={kwargs[key]}")

        if constraints:
            agent_input["input"] = f"{question}\n\nCONSTRAINTS:\n" + "\n".join(
                constraints
            )

        if seed_url:
            # Make the first action explicit so the agent does not drift into repeated generic searches.
            agent_input["input"] += (
                "\n\nMANDATORY FIRST ACTION:\n"
                "Call navigate_to with the Seed URL before using search_for_question."
            )

        logger.info(f"Executing research task: {question[:100]}...")
        if seed_url:
            logger.debug(f"Seed URL provided: {seed_url}")
        if constraints:
            logger.debug(f"Applied constraints: {constraints}")

        # Execute agent with an in-process timeout.
        heartbeat_task: asyncio.Task | None = None
        invoke_started = time.perf_counter()
        invoke_config: dict[str, Any] = {
            # LangGraph execution bound used by create_agent().
            "recursion_limit": effective_max_iterations,
        }
        if DEBUG_AGENT_TRACE:
            logger.warning(
                "DEBUG: invoking agent (timeout={}s, max_iterations={}, input_len={})",
                effective_timeout,
                effective_max_iterations,
                len(agent_input.get("input", "")),
            )
            logger.warning(
                "DEBUG: agent input payload: {}", agent_input.get("input", "")
            )
            heartbeat_task = asyncio.create_task(_debug_heartbeat("agent.ainvoke"))
            invoke_config["callbacks"] = [_DebugTraceCallback()]

        try:
            raw_result = await _invoke_with_timeout(
                agent_executor,
                agent_input,
                timeout_seconds=effective_timeout,
                run_config=invoke_config,
            )
        except TimeoutError as e:
            if DEBUG_AGENT_TRACE:
                logger.warning(
                    "DEBUG: agent invoke timed out after {:.2f}s",
                    time.perf_counter() - invoke_started,
                )
            raise TimeoutError(
                f"Agent execution exceeded timeout ({effective_timeout}s)"
            ) from e
        finally:
            if heartbeat_task is not None:
                heartbeat_task.cancel()

        if DEBUG_AGENT_TRACE:
            logger.warning(
                "DEBUG: agent invoke returned in {:.2f}s",
                time.perf_counter() - invoke_started,
            )

        result = raw_result if isinstance(raw_result, dict) else {"output": raw_result}
        answer = _extract_answer(result)

        # Log intermediate steps if verbose
        if AGENT_VERBOSE and "intermediate_steps" in result:
            for i, step in enumerate(result.get("intermediate_steps", [])):
                logger.debug(f"Step {i + 1}: {step}")

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
        error_message = str(e).strip() or f"{type(e).__name__}: {e!r}"
        logger.error(f"Research task failed: {error_message}", exc_info=True)
        return {
            "status": "error",
            "error": error_message,
            "answer": None,
            "citations": [],
            "screenshots": [],
            "metadata": {},
        }
