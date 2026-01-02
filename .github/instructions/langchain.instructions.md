--- 
applyTo: ./langchain/**/*.py
description: This file describes the post-change validation steps for LangChain Python files.
---
# LangChain - Post-Change Validation Instructions

**Scope**: This applies to all Python files in `./langchain/**/*.py`

After making any changes or additions to Python files in the langchain directory, you **MUST** run the following validation steps in order:

## 0. Verify Dependencies First (CRITICAL)

**Before validating LangChain changes**, check if any changes were made to dependent projects:

### If FastMCP was modified:
LangChain depends on FastMCP (calls FastMCP tools via MCP protocol). If FastMCP files were changed, you **MUST** first execute all steps in `.github/instructions/fastmcp.instructions.md` to ensure FastMCP is working correctly before proceeding with LangChain validation.

### Dependency Chain:
```
FastMCP (MCP tools) → LangChain (orchestration) → Backend (API) → Frontend
```

Always validate dependencies from left to right before validating the current project.

---

## 1. Navigate to LangChain Directory

```bash
cd ./langchain
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

Run integration tests to validate MCP client and service integration:

```bash
poetry run pytest tests/integration/ -v
```

Fix any failing tests before proceeding.

## 6. Run E2E Tests

Run all end-to-end tests to validate the complete orchestration workflow:

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

Return to the project root and rebuild only the langchain service in debug mode:

```bash
cd ..
./start.ps1 -Rebuild -Debug -Services langchain
```

This will:
- Rebuild only the langchain Docker image
- Start langchain service in debug mode with debugpy port 5672 exposed
- Validate that the langchain service starts correctly and integrates with other services

## 9. Verify Service Health

After the stack is running, verify the langchain service is healthy:

```bash
docker logs ws-langchain
```

Check for any startup errors or warnings.

## Quick Command Reference

For rapid validation during development:

```bash
# Full validation in one go (from langchain directory)
cd ./langchain && \
  poetry run ruff check --fix . && \
  poetry run ruff format . && \
  poetry run pytest -v && \
  cd .. && \
  ./start.ps1 -Rebuild -Debug -Services langchain
```

## Critical Reminders

- **Verify dependencies first**: If FastMCP was changed, validate it before validating LangChain
- **Never skip tests**: All tests must pass before considering the change complete
- **Fix linting first**: Code style issues should be resolved before running tests
- **E2E tests are mandatory**: They validate the orchestration workflow and MCP protocol integration
- **Docker rebuild validates integration**: Always rebuild to ensure changes work in the containerized environment
- **Check debug output**: Review logs to ensure no warnings or errors during startup

## Common Issues and Solutions

### Ruff Errors
- Import order issues: Let ruff auto-fix with `--fix`
- Line length: Consider refactoring long lines for readability
- Unused imports: Remove them or use `# noqa: F401` if intentional

### Test Failures
- MCP connection: Ensure FastMCP service is running and accessible
- Async issues: Verify all async functions are properly awaited
- LLM timeout: Check Ollama service is running and model is loaded
- Agent errors: Review agent initialization and tool registration
- Callback issues: Ensure WebSocket callbacks are non-blocking (use `asyncio.create_task`)

### Docker Build Failures
- Dependency conflicts: Check pyproject.toml for version constraints
- Port conflicts: Ensure port 8001, 5672 are available
- Network issues: Verify external-services-network exists
- MCP client connection: Ensure FastMCP container is running and healthy

## Integration Points

LangChain depends on and is depended upon by:

- **FastMCP** (DEPENDENCY): Calls FastMCP tools via MCP protocol for browser operations
- **Ollama** (DEPENDENCY): Uses Ollama for LLM function calling and reasoning
- **Backend** (DEPENDENT): Backend calls LangChain orchestrator via HTTP/WebSocket
- **Config files**: LLM settings, agent config from `../config/` and root `.env`

### Critical Integration Flow:
1. **Frontend** sends task → **Backend** → **LangChain** → **FastMCP** → **Playwright**
2. Results flow back with streaming callbacks for real-time updates

Always test the complete integration flow, not just isolated components.

## LangChain-Specific Validation

### Agent Behavior
- Verify agent correctly selects tools based on task
- Check reasoning steps are logged appropriately
- Ensure tool results are properly parsed and used

### Streaming Callbacks
- Confirm WebSocket events are emitted for all stages (thinking, tool_call, tool_result, complete, error)
- Verify callbacks are non-blocking (use `asyncio.create_task`)
- Check error recovery and structured error responses

### Memory and State
- Test conversation memory if implemented
- Verify task context is maintained throughout execution
- Check cleanup of resources after task completion

### Tool Integration
- Validate all MCP tools are properly registered
- Test tool error handling and recovery
- Ensure tool parameters are correctly formatted and validated
