--- 
applyTo: ./backend/**/*.py
description: This file describes the post-change validation steps for Backend Python files.
---
# Backend - Post-Change Validation Instructions

**Scope**: This applies to all Python files in `./backend/**/*.py`

After making any changes or additions to Python files in the backend directory, you **MUST** run the following validation steps in order:

## 0. Verify Dependencies First (CRITICAL)

**Before validating Backend changes**, check if any changes were made to dependent projects:

### If LangChain was modified:
Backend depends on LangChain (calls LangChain orchestrator via HTTP). If LangChain files were changed, you **MUST** first execute all steps in `.github/instructions/langchain.instructions.md` to ensure LangChain is working correctly before proceeding with Backend validation.

### If FastMCP was modified:
Backend indirectly depends on FastMCP (through LangChain). If FastMCP files were changed, you **MUST** first execute:
1. All steps in `.github/instructions/fastmcp.instructions.md`
2. Then all steps in `.github/instructions/langchain.instructions.md`

Then proceed with Backend validation.

### Dependency Chain:
```
FastMCP (MCP tools) → LangChain (orchestration) → Backend (API) → Frontend
```

Always validate dependencies from left to right before validating the current project.

---

## 1. Navigate to Backend Directory

```bash
cd ./backend
```

## 2. Run Ruff Linter

Run ruff to check for code style and quality issues:

```bash
poetry run ruff check .
```

If errors are found, attempt to auto-fix them:

```bash
poetry run ruff check --fix .
```

If there are remaining errors that cannot be auto-fixed, manually correct them before proceeding.

## 3. Run Format Check

Ensure code is properly formatted:

```bash
poetry run ruff format .
```

## 4. Run Unit Tests

Run all unit tests to ensure functionality is not broken:

```bash
poetry run pytest tests/unit/ -v
```

Fix any failing tests before proceeding.

## 5. Run Integration Tests

Run integration tests to validate LangChain integration and property mapping:

```bash
poetry run pytest tests/integration/ -v
```

Fix any failing tests before proceeding.

## 6. Run E2E Tests

Run all end-to-end tests to validate the complete API workflow:

```bash
poetry run pytest tests/e2e/ -v
```

Fix any failing E2E tests before proceeding.

## 7. Run Full Test Suite with Coverage

For comprehensive validation, run the complete test suite with coverage:

```bash
poetry run pytest --cov=src --cov-report=html --cov-report=json --cov-report=xml -v
```

Verify that code coverage meets the required thresholds. Fix any coverage gaps as necessary before proceeding.

## 8. Rebuild and Test in Docker

Return to the project root and rebuild only the backend service in debug mode:

```bash
cd ..
./start.ps1 -Rebuild -Debug -Services backend
```

This will:
- Rebuild only the backend Docker image
- Start backend service in debug mode with debugpy port 5671 exposed
- Validate that the backend service starts correctly and integrates with other services

## 9. Verify Service Health

After the stack is running, verify the backend service is healthy:

```bash
docker logs ws-backend
```

Check for any startup errors or warnings.

Verify the API is accessible:

```bash
curl http://localhost:8000/health
```

## Quick Command Reference

For rapid validation during development:

```bash
# Full validation in one go (from backend directory)
cd ./backend && \
  poetry run ruff check --fix . && \
  poetry run ruff format . && \
  poetry run pytest -v && \
  cd .. && \
  ./start.ps1 -Rebuild -Debug -Services backend
```

## Critical Reminders

- **Verify dependencies first**: If LangChain or FastMCP was changed, validate them before validating Backend
- **Never skip tests**: All tests must pass before considering the change complete
- **Fix linting first**: Code style issues should be resolved before running tests
- **E2E tests are mandatory**: They validate the complete API workflow including WebSocket communication
- **Docker rebuild validates integration**: Always rebuild to ensure changes work in the containerized environment
- **Check debug output**: Review logs to ensure no warnings or errors during startup
- **Test both HTTP and WebSocket**: Verify REST endpoints and WebSocket streaming work correctly

## Common Issues and Solutions

### Ruff Errors
- Import order issues: Let ruff auto-fix with `--fix`
- Line length: Consider refactoring long lines for readability
- Unused imports: Remove them or use `# noqa: F401` if intentional

### Test Failures
- LangChain connection: Ensure LangChain service is running and accessible at port 8001
- WebSocket issues: Check connection handling and message serialization
- Task management: Verify task creation, storage, and retrieval logic
- Artifact handling: Check file save/load operations in artifacts directory
- Property mapping: Ensure Zod validation schemas are correctly integrated
- Async issues: Verify all async functions are properly awaited

### Docker Build Failures
- Dependency conflicts: Check pyproject.toml for version constraints
- Port conflicts: Ensure ports 8000, 5671 are available
- Network issues: Verify external-services-network exists
- Volume mounts: Ensure artifacts directory is properly mounted
- LangChain connection: Ensure LangChain container is running and healthy

## Integration Points

Backend depends on and is depended upon by:

- **LangChain** (DEPENDENCY): Calls LangChain orchestrator to execute tasks
- **Frontend** (DEPENDENT): Frontend calls Backend API for task submission and results
- **Config files**: CORS settings, API config from `../config/` and root `.env`
- **Artifacts directory**: Stores task results, screenshots, and metadata

### Critical Integration Flow:
1. **Frontend** submits task via HTTP POST → **Backend** `/tasks/` endpoint
2. **Backend** streams progress via WebSocket to Frontend
3. **Backend** calls **LangChain** HTTP endpoint to execute task
4. **LangChain** orchestrates **FastMCP** tools via MCP protocol
5. Results and artifacts flow back through the chain

Always test the complete integration flow, not just isolated components.

## Backend-Specific Validation

### FastAPI Endpoints
- Test all REST endpoints (POST /tasks, GET /tasks, GET /tasks/{id})
- Verify request validation with Pydantic models
- Check response status codes and error handling
- Test CORS headers for allowed origins

### WebSocket Communication
- Verify WebSocket connection establishment
- Test streaming events (thinking, tool_call, tool_result, screenshot, complete, error)
- Check connection cleanup on task completion or error
- Validate message serialization/deserialization

### Task Management
- Test task creation with unique IDs
- Verify task storage and retrieval
- Check task status transitions (pending → running → complete/error)
- Validate task history and metadata storage

### Artifact Handling
- Test screenshot saving and retrieval
- Verify artifact directory structure
- Check file permissions and access
- Validate artifact metadata in task results

### Property Mapping (Pydantic Validation)
- Test TaskRequest validation against Pydantic models
- Verify TaskResponse property mapping
- Check error handling for invalid requests
- Validate request/response model consistency

### Error Handling
- Test structured error responses
- Verify error logging without sensitive data
- Check recoverable vs non-recoverable error handling
- Validate WebSocket error events
