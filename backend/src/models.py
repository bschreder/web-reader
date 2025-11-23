"""
Web Reader Backend - Data Models
=================================
Pydantic models for API requests/responses and internal task management.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Annotated

from pydantic import BaseModel, Field


# ==================================================================
# Enums
# ==================================================================


class TaskStatus(str, Enum):
    """Task execution status."""

    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(str, Enum):
    """WebSocket event types."""

    THINKING = "agent:thinking"
    TOOL_CALL = "agent:tool_call"
    TOOL_RESULT = "agent:tool_result"
    SCREENSHOT = "agent:screenshot"
    COMPLETE = "agent:complete"
    ERROR = "agent:error"


# ==================================================================
# Request Models
# ==================================================================


class TaskCreate(BaseModel):
    """Request model for creating a new task."""

    question: str = Field(
        ..., min_length=1, max_length=1000, description="Research question"
    )
    seed_url: Annotated[Optional[str], Field(None, description="Optional starting URL")] = None
    max_depth: int = Field(3, ge=1, le=5, description="Maximum link depth to follow")
    max_pages: int = Field(20, ge=1, le=50, description="Maximum pages to visit")
    time_budget: int = Field(120, ge=30, le=600, description="Time budget in seconds")


class TaskCancel(BaseModel):
    """Request model for cancelling a task."""

    reason: Optional[str] = Field(
        None, max_length=200, description="Cancellation reason"
    )


# ==================================================================
# Response Models
# ==================================================================


class Citation(BaseModel):
    """Source citation."""

    url: str
    title: str
    excerpt: Optional[str] = None


class TaskResponse(BaseModel):
    """Response model for task status and results."""

    task_id: str
    status: TaskStatus
    question: str
    seed_url: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None  # seconds
    answer: Optional[str] = None
    citations: list[Citation] = []
    screenshots: list[str] = []  # URLs to screenshots
    error: Optional[str] = None
    metadata: dict[str, Any] = {}


class TaskListResponse(BaseModel):
    """Response model for listing tasks."""

    tasks: list[TaskResponse]
    total: int
    offset: int
    limit: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str = "0.1.0"
    langchain_connected: bool
    active_tasks: int
    total_tasks: int


class ErrorResponse(BaseModel):
    """Error response model."""

    status: str = "error"
    error: str
    error_code: Optional[str] = None
    details: dict[str, Any] = {}


class WebSocketEvent(BaseModel):
    """Base model for WebSocket events."""

    type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    task_id: str


class ThinkingEvent(WebSocketEvent):
    """Agent is thinking/reasoning."""

    type: EventType = EventType.THINKING
    content: str


class ToolCallEvent(WebSocketEvent):
    """Agent is calling a tool."""

    type: EventType = EventType.TOOL_CALL
    tool: str
    args: dict[str, Any]


class ToolResultEvent(WebSocketEvent):
    """Tool execution result."""

    type: EventType = EventType.TOOL_RESULT
    tool: str
    result: dict[str, Any]
    success: bool


class ScreenshotEvent(WebSocketEvent):
    """Screenshot captured."""

    type: EventType = EventType.SCREENSHOT
    image_url: str
    full_page: bool


class CompleteEvent(WebSocketEvent):
    """Task completed."""

    type: EventType = EventType.COMPLETE
    answer: str
    citations: list[Citation]
    duration: float


class ErrorEvent(WebSocketEvent):
    """Error occurred."""

    type: EventType = EventType.ERROR
    error: str
    recoverable: bool
