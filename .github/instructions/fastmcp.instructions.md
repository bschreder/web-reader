--- 
applyTo: ./fastmcp/**/*.py
description: This file describes the post-change validation steps for FastMCP Python files.
---
# FastMCP - Post-Change Validation Instructions

**Scope**: This applies to all Python files in `./fastmcp/**/*.py`

After making any changes or additions to Python files in the fastmcp directory, you **MUST** run the following validation steps in order:

## 1. Navigate to FastMCP Directory

```bash
cd ./fastmcp
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

Run integration tests if they exist:

```bash
poetry run pytest tests/integration/ -v
```

Fix any failing tests before proceeding.

## 6. Run E2E Tests

Run all end-to-end tests to validate the complete system:

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

Return to the project root and rebuild only the fastmcp service in debug mode:

```bash
cd ..
./start.ps1 -Rebuild -Debug -Services fastmcp
```

This will:
- Rebuild only the fastmcp Docker image
- Start fastmcp service in debug mode with debugpy port 5673 exposed
- Validate that the fastmcp service starts correctly and integrates with other services

## 9. Verify Service Health

After the stack is running, verify the fastmcp service is healthy:

```bash
docker logs ws-fastmcp
```

Check for any startup errors or warnings.

## Quick Command Reference

For rapid validation during development:

```bash
# Full validation in one go (from fastmcp directory)
cd ./fastmcp && \
  poetry run ruff check --fix . && \
  poetry run ruff format . && \
  poetry run pytest -v && \
  cd .. && \
  ./start.ps1 -Rebuild -Debug -Services fastmcp
```

## Critical Reminders

- **Never skip tests**: All tests must pass before considering the change complete
- **Fix linting first**: Code style issues should be resolved before running tests
- **E2E tests are mandatory**: They validate the MCP protocol integration and browser interactions
- **Docker rebuild validates integration**: Always rebuild to ensure changes work in the containerized environment
- **Check debug output**: Review logs to ensure no warnings or errors during startup

## Common Issues and Solutions

### Ruff Errors
- Import order issues: Let ruff auto-fix with `--fix`
- Line length: Consider refactoring long lines for readability
- Unused imports: Remove them or use `# noqa: F401` if intentional

### Test Failures
- Browser timeout: Check rate limiting and delays in config
- MCP connection: Ensure fastmcp server starts before tests run
- Async issues: Verify all async functions are properly awaited

### Docker Build Failures
- Dependency conflicts: Check pyproject.toml for version constraints
- Port conflicts: Ensure ports 3000, 5673 are available
- Network issues: Verify external-services-network exists

## Integration Points

FastMCP depends on and is depended upon by:

- **Playwright**: Browser automation (must be running)
- **LangChain**: Calls FastMCP tools via MCP protocol
- **Backend**: May indirectly trigger FastMCP operations
- **Config files**: Domain filters, rate limits from `../config/` and root `.env`

Always test the complete integration flow, not just isolated components.
