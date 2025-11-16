# Backend API - FastAPI Service

# ============================================================================

Python backend service providing REST API and WebSocket endpoints for task management.

## Features

- **REST API**: Create, retrieve, and delete research tasks
- **WebSocket Streaming**: Real-time updates during task execution
- **Task Queue**: Manages concurrent tasks with rate limiting
- **Artifact Storage**: Persists task results, logs, and screenshots
- **LangChain Integration**: Coordinates with LangChain orchestrator

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build image
docker build -t web-reader-backend .

# Run container
docker run -p 8000:8000 web-reader-backend
```

## API Endpoints

### Tasks

- `POST /api/tasks` - Create new research task
- `GET /api/tasks/{task_id}` - Get task status and results
- `DELETE /api/tasks/{task_id}` - Cancel/delete task
- `GET /api/tasks` - List all tasks
- `WS /api/tasks/{task_id}/stream` - WebSocket for real-time updates

### Health

- `GET /health` - Health check endpoint

## Environment Variables

```bash
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# LangChain Orchestrator
LANGCHAIN_HOST=langchain
LANGCHAIN_PORT=8001

# Task Management
MAX_CONCURRENT_TASKS=3
TASK_TIMEOUT=300
ARTIFACT_DIR=artifacts/

# Logging
LOG_LEVEL=info
LOG_TARGET=console
LOG_FILE=logs/backend.log
```

## Development

### Project Structure

```
backend/
├── server.py           # FastAPI application entry point
├── src/
│   ├── __init__.py
│   ├── config.py       # Configuration loading
│   ├── models.py       # Pydantic models
│   ├── tasks.py        # Task queue management
│   ├── artifacts.py    # Artifact persistence
│   └── langchain.py    # LangChain client
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_tasks.py
│   └── test_artifacts.py
├── requirements.txt
├── requirements-test.txt
├── Dockerfile
└── README.md
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_api.py -v
```

## Task Lifecycle

1. **Created**: Task submitted via POST /api/tasks
2. **Queued**: Task added to processing queue
3. **Running**: LangChain agent executing task
4. **Completed**: Task finished successfully with answer
5. **Failed**: Task failed with error message
6. **Cancelled**: Task cancelled by user

## WebSocket Events

The WebSocket endpoint streams real-time events:

- `agent:thinking` - Agent is reasoning about next step
- `agent:tool_call` - Agent is calling a tool (e.g., navigate_to)
- `agent:tool_result` - Tool execution result
- `agent:screenshot` - Screenshot captured
- `agent:complete` - Task completed with final answer
- `agent:error` - Error occurred during execution

## Artifacts

Each task creates an artifact directory:

```
artifacts/{task_id}/
├── task.json          # Task metadata and results
├── logs.txt           # Execution logs
├── screenshots/       # Captured screenshots
│   ├── step_1.png
│   ├── step_2.png
│   └── ...
└── sources.json       # Visited URLs and citations
```

## Error Handling

The API uses consistent error response format:

```json
{
  "status": "error",
  "error": "Human-readable error message",
  "error_code": "TASK_NOT_FOUND",
  "details": {}
}
```

## Rate Limiting

- Max 3 concurrent tasks (configurable)
- Task timeout: 300 seconds (5 minutes)
- WebSocket connection timeout: 600 seconds

## Security

- CORS configured for specified origins
- Input validation via Pydantic models
- Task isolation (no shared state between tasks)
- Artifact path traversal prevention

## Monitoring

- Structured JSON logging
- Health check endpoint
- Task metrics (duration, success rate)
- LangChain integration status

## License

Part of the Web Reader project. See root LICENSE file.
