"""
LangChain orchestrator service entry point.
FastAPI server that executes research tasks using LangChain agent.
"""

import sys
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field

from src.agent import execute_research_task
from src.callbacks import WebSocketCallbackHandler
from src.config import LOG_FILE, LOG_LEVEL, LOG_TARGET, SERVICE_HOST, SERVICE_PORT
from src.mcp_client import close_mcp_client, get_mcp_client

# ============================================================================
# Logging Configuration
# ============================================================================

# Remove default logger
logger.remove()

# Add console handler
if LOG_TARGET in ("console", "both"):
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

# Add file handler
if LOG_TARGET in ("file", "both"):
    logger.add(
        LOG_FILE,
        level=LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="100 MB",
        retention="7 days",
    )

# ============================================================================
# Request/Response Models
# ============================================================================


class ExecuteTaskRequest(BaseModel):
    """Request model for task execution."""

    task_id: str = Field(..., description="Unique task identifier")
    question: str = Field(..., description="Research question")
    seed_url: str | None = Field(None, description="Optional starting URL")
    max_depth: int = Field(3, description="Maximum link depth")
    max_pages: int = Field(20, description="Maximum pages to visit")
    time_budget: int = Field(120, description="Time budget in seconds")


class ExecuteTaskResponse(BaseModel):
    """Response model for task execution."""

    status: str = Field(..., description="Execution status")
    answer: str | None = Field(None, description="Research answer")
    citations: list[dict[str, Any]] = Field(
        default_factory=list, description="Citation sources"
    )
    screenshots: list[str] = Field(default_factory=list, description="Screenshot data")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Execution metadata"
    )
    error: str | None = Field(None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    mcp_connected: bool
    ollama_model: str


# ============================================================================
# Application Lifecycle
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting LangChain orchestrator service")

    # Initialize MCP client
    mcp_client = await get_mcp_client()
    mcp_healthy = await mcp_client.health_check()

    if mcp_healthy:
        logger.info("FastMCP connection established")
    else:
        logger.warning("FastMCP connection failed - service may not work correctly")

    yield

    # Cleanup
    logger.info("Shutting down LangChain orchestrator service")
    await close_mcp_client()


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="LangChain Orchestrator",
    description="Research task orchestration using LangChain agents",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Endpoints
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from src.config import OLLAMA_MODEL

    mcp_client = await get_mcp_client()
    mcp_healthy = await mcp_client.health_check()

    return HealthResponse(
        status="healthy" if mcp_healthy else "degraded",
        service="langchain-orchestrator",
        mcp_connected=mcp_healthy,
        ollama_model=OLLAMA_MODEL,
    )


@app.get("/live")
async def liveness():
    """Kubernetes-style liveness probe."""
    return {"status": "alive", "service": "langchain-orchestrator"}


@app.get("/ready")
async def readiness():
    """Kubernetes-style readiness probe: depends on MCP connectivity."""
    mcp_client = await get_mcp_client()
    mcp_healthy = await mcp_client.health_check()
    return {"status": "ready" if mcp_healthy else "not-ready", "mcp": mcp_healthy}


@app.post("/execute", response_model=ExecuteTaskResponse)
async def execute_task(request: ExecuteTaskRequest):
    """
    Execute a research task using LangChain agent.

    Args:
        request: Task execution request

    Returns:
        Task execution result with answer and citations
    """
    try:
        logger.info(f"Received task {request.task_id}: {request.question[:100]}...")

        # Get MCP client
        mcp_client = await get_mcp_client()

        # Execute research task
        result = await execute_research_task(
            question=request.question,
            mcp_client=mcp_client,
            seed_url=request.seed_url,
            max_iterations=min(15, request.max_pages),  # Limit iterations
            max_execution_time=request.time_budget,
        )

        logger.info(f"Task {request.task_id} completed: {result.get('status')}")

        return ExecuteTaskResponse(
            status=result.get("status", "error"),
            answer=result.get("answer"),
            citations=result.get("citations", []),
            screenshots=result.get("screenshots", []),
            metadata=result.get("metadata", {}),
            error=result.get("error"),
        )

    except Exception as e:
        logger.error(f"Task {request.task_id} failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/stream/{task_id}")
async def stream_task(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for streaming task execution events.

    Args:
        websocket: WebSocket connection
        task_id: Task identifier for logging

    Streams:
        Real-time agent events (thinking, tool_call, tool_result, complete, error)
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for task {task_id}")

    try:
        # Wait for task request
        data = await websocket.receive_json()
        question = data.get("question", "")
        seed_url = data.get("seed_url")
        max_iterations = min(15, data.get("max_pages", 20))
        max_execution_time = data.get("time_budget", 120)

        if not question:
            await websocket.send_json(
                {"type": "error", "error": "Missing required field: question"}
            )
            await websocket.close()
            return

        logger.info(f"Starting streamed task {task_id}: {question[:100]}...")

        # Get MCP client
        mcp_client = await get_mcp_client()

        # Create WebSocket callback handler
        callback_handler = WebSocketCallbackHandler(websocket)

        # Execute research task with streaming
        result = await execute_research_task(
            question=question,
            mcp_client=mcp_client,
            callbacks=[callback_handler],
            seed_url=seed_url,
            max_iterations=max_iterations,
            max_execution_time=max_execution_time,
        )

        # Send final result
        await websocket.send_json(
            {
                "type": "agent:complete",
                "status": result.get("status", "error"),
                "answer": result.get("answer"),
                "citations": result.get("citations", []),
                "screenshots": result.get("screenshots", []),
                "metadata": result.get("metadata", {}),
                "error": result.get("error"),
            }
        )

        logger.info(f"Task {task_id} streaming completed")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for task {task_id}")
    except Exception as e:
        logger.error(f"Task {task_id} streaming failed: {e}", exc_info=True)
        try:
            await websocket.send_json(
                {
                    "type": "agent:error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )
        except Exception:
            pass  # Client already disconnected
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host=SERVICE_HOST,
        port=SERVICE_PORT,
        log_level=LOG_LEVEL.lower(),
        reload=False,
    )
