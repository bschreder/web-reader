"""
Web Reader Backend API
======================
FastAPI application providing REST and WebSocket endpoints for research tasks.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Query,
    Request,
)
from starlette.websockets import WebSocketState
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from loguru import logger

from src.artifacts import (
    delete_task_artifacts,
    get_artifact_stats,
    get_screenshot_path,
    save_sources,
    save_task_result,
)
from src.config import (
    API_HOST,
    API_PORT,
    ARTIFACT_DIR,
    CORS_ORIGINS,
    configure_logging,
)
from src.langchain import close_langchain_client, get_langchain_client
from src.models import (
    Citation,
    CompleteEvent,
    ErrorEvent,
    ErrorResponse,
    HealthResponse,
    TaskCancel,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    ThinkingEvent,
)
from src.tasks import (
    create_task,
    delete_task,
    execute_task,
    get_active_task_count,
    get_task,
    get_total_task_count,
    list_tasks,
)

# ============================================================================
# Application Lifecycle
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    configure_logging()
    logger.info("Backend API starting...")

    # Initialize LangChain client
    await get_langchain_client()

    # Ensure artifact directory exists
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"Backend API ready on {API_HOST}:{API_PORT}")
    yield

    # Shutdown
    logger.info("Backend API shutting down...")
    await close_langchain_client()
    logger.info("Backend API stopped")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Web Reader Backend API",
    description="Backend service for autonomous web research tasks",
    version="0.1.0",
    lifespan=lifespan,
    json_schema_extra={
        "openapi": {
            "info": {
                "x-logo": {
                    "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
                }
            }
        }
    },
)

# Configure JSON encoder to use Pydantic's by_alias for camelCase output


def custom_json_encoder(obj):
    """Custom JSON encoder that handles Pydantic models with by_alias."""
    if isinstance(obj, BaseModel):
        return obj.model_dump(by_alias=True, exclude_none=False, mode="json")
    return jsonable_encoder(obj)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for artifacts
app.mount("/artifacts", StaticFiles(directory=str(ARTIFACT_DIR)), name="artifacts")

# ============================================================================
# Global Exception Handlers
# ============================================================================


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return structured error response for validation errors."""
    err = ErrorResponse(
        error="Validation error",
        error_code="validation_error",
        details={"errors": exc.errors()},
    )
    return JSONResponse(content=custom_json_encoder(err), status_code=422)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return structured error response for HTTP exceptions."""
    err = ErrorResponse(
        error=str(exc.detail) if exc.detail else "HTTP error",
        error_code="http_error",
        details={"status_code": exc.status_code},
    )
    return JSONResponse(content=custom_json_encoder(err), status_code=exc.status_code)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return structured error response for unexpected exceptions."""
    logger.exception("Unhandled server error")
    err = ErrorResponse(
        error="Internal server error",
        error_code="internal_error",
        details={"message": str(exc)},
    )
    return JSONResponse(content=custom_json_encoder(err), status_code=500)


# ============================================================================
# Health Endpoint
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    langchain_client = await get_langchain_client()
    langchain_connected = await langchain_client.health_check()

    return HealthResponse(
        status="healthy" if langchain_connected else "degraded",
        langchain_connected=langchain_connected,
        active_tasks=await get_active_task_count(),
        total_tasks=await get_total_task_count(),
    )


# ============================================================================
# Task Management Endpoints
# ============================================================================


@app.post("/api/tasks", response_model=TaskResponse, status_code=201)
async def create_new_task(task_data: TaskCreate):
    """
    Create a new research task.

    Args:
        task_data: Task creation parameters

    Returns:
        Created task details
    """
    try:
        # Create task
        task = await create_task(
            question=task_data.question,
            seed_url=task_data.seed_url,
            max_depth=task_data.max_depth,
            max_pages=task_data.max_pages,
            time_budget=task_data.time_budget,
            search_engine=task_data.search_engine,
            max_results=task_data.max_results,
            safe_mode=task_data.safe_mode,
            same_domain_only=task_data.same_domain_only,
            allow_external_links=task_data.allow_external_links,
        )

        # Start task execution in background
        async def task_executor(t):
            """Execute task via LangChain."""
            langchain_client = await get_langchain_client()
            result = await langchain_client.execute_task(t)

            if result.get("status") == "error":
                raise RuntimeError(result.get("error", "LangChain returned error status"))

            answer = result.get("answer")
            citations = result.get("citations", [])
            if not answer and not citations:
                raise RuntimeError(
                    "LangChain returned empty result (no answer and no citations)"
                )

            # Update task with results
            t.answer = answer
            t.citations = [
                Citation.from_dict(c) if isinstance(c, dict) else c
                for c in citations
            ]
            t.screenshots = result.get("screenshots", [])
            t.metadata = result.get("metadata", {})

            # Save artifacts
            await save_task_result(t.task_id, t.to_dict())
            if t.citations:
                # Convert Citation models to dicts for JSON serialization
                await save_sources(t.task_id, [c.model_dump() for c in t.citations])

        # Execute task asynchronously
        asyncio.create_task(execute_task(task, task_executor))

        logger.info(f"Created and queued task {task.task_id}")
        return TaskResponse(**task.to_dict())

    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """
    Get task status and results.

    Args:
        task_id: Task ID

    Returns:
        Task details

    Raises:
        HTTPException: If task not found
    """
    task = await get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return TaskResponse(**task.to_dict())


@app.delete("/api/tasks/{task_id}", status_code=204)
async def delete_existing_task(task_id: str, cancel_data: Optional[TaskCancel] = None):
    """
    Cancel and delete a task.

    Args:
        task_id: Task ID
        cancel_data: Optional cancellation reason

    Raises:
        HTTPException: If task not found
    """
    # Get task first to cancel if running
    task = await get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Cancel if running
    reason = cancel_data.reason if cancel_data else None
    await task.cancel(reason)

    # Delete task and artifacts
    await delete_task(task_id)
    await delete_task_artifacts(task_id)

    logger.info(f"Deleted task {task_id}")


@app.get("/api/tasks", response_model=TaskListResponse)
async def list_all_tasks(
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max tasks to return"),
):
    """
    List all tasks with pagination.

    Args:
        offset: Number of tasks to skip
        limit: Maximum tasks to return

    Returns:
        List of tasks with pagination info
    """
    tasks, total = await list_tasks(offset=offset, limit=limit)

    return TaskListResponse(
        tasks=[TaskResponse(**t.to_dict()) for t in tasks],
        total=total,
        offset=offset,
        limit=limit,
    )


# ============================================================================
# WebSocket Endpoint
# ============================================================================


@app.websocket("/api/tasks/{task_id}/stream")
async def stream_task_events(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for streaming task execution events.

    Args:
        websocket: WebSocket connection
        task_id: Task ID to stream

    Connects to LangChain orchestrator's WebSocket and relays events to frontend.
    """
    await websocket.accept()

    def is_ws_connected() -> bool:
        return (
            websocket.client_state == WebSocketState.CONNECTED
            and websocket.application_state == WebSocketState.CONNECTED
        )

    async def safe_send_json(payload: dict) -> bool:
        """Send payload if socket is open; return False when disconnected."""
        if not is_ws_connected():
            return False
        try:
            await websocket.send_json(payload)
            return True
        except WebSocketDisconnect:
            return False
        except RuntimeError as send_error:
            # Starlette raises RuntimeError when sending after close frame.
            logger.info(f"WebSocket send skipped for task {task_id}: {send_error}")
            return False

    async def safe_close(code: int = 1000) -> None:
        if websocket.application_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close(code=code)
            except Exception:
                pass

    try:
        # Verify task exists
        task = await get_task(task_id)
        if not task:
            error_event = ErrorEvent(
                task_id=task_id,
                error=f"Task {task_id} not found",
                recoverable=False,
            )
            await safe_send_json(custom_json_encoder(error_event))
            await safe_close(code=1008)
            return

        logger.info(f"WebSocket connected for task {task_id}")

        # Send initial status via thinking event
        thinking_event = ThinkingEvent(
            task_id=task_id,
            content=f"Task {task.status.value}",
        )
        if not await safe_send_json(custom_json_encoder(thinking_event)):
            return

        # If task is already complete, send result and close
        if task.status.value in ("completed", "failed", "cancelled"):
            if task.status.value == "failed":
                error_event = ErrorEvent(
                    task_id=task_id,
                    error=task.error or "Task failed",
                    recoverable=False,
                )
                await safe_send_json(custom_json_encoder(error_event))
            else:
                complete_event = CompleteEvent(
                    task_id=task_id,
                    answer=task.answer or "",
                    citations=task.citations or [],
                    duration=task.duration or 0.0,
                )
                await safe_send_json(custom_json_encoder(complete_event))
            await safe_close()
            return

        # Stream is read-only from backend task state.
        # Do not invoke LangChain /stream here; task execution already runs via
        # the background /execute call started at task creation time.
        last_status: str | None = None
        while True:
            task = await get_task(task_id)
            if not task:
                break

            if task.status.value != last_status:
                status_event = ThinkingEvent(
                    task_id=task_id,
                    content=f"Status: {task.status.value}",
                )
                if not await safe_send_json(custom_json_encoder(status_event)):
                    return
                last_status = task.status.value

            if task.status.value in ("completed", "failed", "cancelled"):
                if task.status.value == "failed":
                    error_event = ErrorEvent(
                        task_id=task_id,
                        error=task.error or "Task failed",
                        recoverable=False,
                    )
                    await safe_send_json(custom_json_encoder(error_event))
                else:
                    complete_event = CompleteEvent(
                        task_id=task_id,
                        answer=task.answer or "",
                        citations=task.citations or [],
                        duration=task.duration or 0.0,
                    )
                    await safe_send_json(custom_json_encoder(complete_event))
                break

            await asyncio.sleep(1)

    except WebSocketDisconnect as e:
        logger.info(f"WebSocket disconnected for task {task_id}")
        logger.debug(
            f"WebSocket disconnect details - task_id={task_id}, code={getattr(e, 'code', 'N/A')}, reason={getattr(e, 'reason', 'N/A')}"
        )

    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
        try:
            error_event = ErrorEvent(
                task_id=task_id,
                error=str(e),
                recoverable=False,
            )
            await safe_send_json(custom_json_encoder(error_event))
        except Exception:
            pass


@app.get("/api/tasks/{task_id}/artifacts")
async def get_task_artifacts(task_id: str):
    """
    Get artifact statistics for a task.

    Args:
        task_id: Task ID

    Returns:
        Artifact statistics
    """
    stats = await get_artifact_stats(task_id)
    if not stats.get("exists"):
        raise HTTPException(
            status_code=404, detail=f"No artifacts found for task {task_id}"
        )

    return stats


@app.get("/api/tasks/{task_id}/screenshots/{filename}")
async def get_screenshot(task_id: str, filename: str):
    """
    Get a specific screenshot file.

    Args:
        task_id: Task ID
        filename: Screenshot filename

    Returns:
        PNG image file
    """
    filepath = get_screenshot_path(task_id, filename)
    if not filepath:
        raise HTTPException(
            status_code=404,
            detail=f"Screenshot {filename} not found for task {task_id}",
        )

    return FileResponse(filepath, media_type="image/png")


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info",
    )
