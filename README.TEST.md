# Web Reader - Testing Guide

This document provides comprehensive instructions for running and maintaining tests across all Web Reader services.

## Current Test Status ✅

All core services have passing tests with good coverage:

| Service       | Unit Tests | Integration Tests | E2E Tests         | Coverage | Status              |
| ------------- | ---------- | ----------------- | ----------------- | -------- | ------------------- |
| **FastMCP**   | 66 passing | ✅ Included       | ✅ Included       | **93%**  | ✅ All passing      |
| **LangChain** | 36 passing | 5 passing         | ⚠️ Requires stack | **85%**  | ✅ Unit+Integration |
| **Backend**   | 53 passing | 16 passing        | ⚠️ Requires stack | **89%**  | ✅ Unit+Integration |
| **Frontend**  | 16 passing | 4 browser tests   | ⚠️ Requires stack | **46%**  | ✅ All passing      |

**Note**: E2E tests requiring the full stack (Ollama, Playwright, all services) can be run when containers are started. Unit and integration tests run independently in the devcontainer.

## Table of Contents

- [Current Test Status](#current-test-status-)
- [Overview](#overview)
- [Test Organization](#test-organization)
- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
  - [From Devcontainer (Recommended)](#from-devcontainer-recommended)
  - [From Docker Containers](#from-docker-containers)
- [Test Types](#test-types)
- [Coverage Requirements](#coverage-requirements)
- [Service-Specific Testing](#service-specific-testing)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Overview

The Web Reader project follows a structured testing approach with three test levels:

1. **Unit Tests**: Isolated tests with mocked dependencies
2. **Integration Tests**: Tests that interact with real services (Playwright, Ollama, etc.)
3. **End-to-End (E2E) Tests**: Full workflow tests simulating real usage

All tests can be run from within the VS Code devcontainer (recommended) or from within running Docker containers.

## Test Organization

Each service follows a standardized directory structure:

```
<service>/
├── tests/
│   ├── unit/          # Isolated unit tests (>80% coverage required)
│   │   ├── conftest.py
│   │   └── test_*.py
│   ├── integration/   # Tests with real service dependencies
│   │   ├── conftest.py
│   │   └── test_*.py
│   └── e2e/           # Full workflow tests
│       ├── conftest.py
│       └── test_*.py
├── src/               # Source code
├── pytest.ini         # Pytest configuration (Python services)
├── vitest.config.ts   # Vitest configuration (Frontend)
└── Dockerfile         # Multistage: base → dev → prod
```

**Frontend Structure** (TypeScript/React):

```
frontend/
├── tests/
│   ├── unit/          # Unit tests (Vitest in Node environment)
│   ├── browser/       # Browser tests (Vitest + Playwright)
│   ├── integration/   # Integration tests
│   └── e2e/           # E2E tests (Playwright)
├── src/
├── vitest.config.ts   # Multi-project: unit + browser
└── package.json
```

## Quick Start

### Run All Tests (Devcontainer)

```bash
# Navigate to project root
cd /workspaces/web-reader

# Run all Python service tests with coverage
./scripts/test-all-python.sh

# Individual services
cd fastmcp && poetry run pytest --cov=src --cov-report=term
cd langchain && poetry run pytest tests/unit tests/integration --cov=src --cov-report=term
cd backend && poetry run pytest tests/unit tests/integration --cov=src --cov-report=term

# Frontend (both unit and browser tests)
cd frontend && npm run test:coverage
```

### View Coverage Reports

HTML coverage reports are generated in each service's `coverage/` directory:

```bash
# FastMCP
open fastmcp/coverage/html/index.html

# LangChain
open langchain/coverage/html/index.html

# Backend
open backend/coverage/html/index.html

# Frontend
open frontend/coverage/index.html
```

# Run all tests (unit + integration + e2e)

./scripts/test-all.sh all

Note: The script automatically installs each Python service's runtime and test dependencies in the devcontainer before running tests.

````

#### FastMCP Tests

```bash
cd /workspaces/web-reader/fastmcp

# Unit tests only (fast, no external dependencies)
pytest tests/unit --cov=src --cov-branch --cov-report=term-missing

# Integration tests (requires Playwright container running)
pytest tests/integration -v

# E2E tests (full workflows)
pytest tests/e2e -v --maxfail=1

# All tests
pytest tests/ --cov=src --cov-branch --cov-report=html
````

## Running Tests

### From Devcontainer (Recommended)

The devcontainer has Python 3.13 and Node.js 24 pre-installed. Poetry environments are isolated per service.

#### FastMCP Tests

```bash
cd /workspaces/web-reader/fastmcp

# Unit tests only (fast, no external dependencies)
poetry run pytest tests/unit/ -v

# Integration tests (requires Playwright container running)
poetry run pytest tests/integration/ -v

# E2E tests (full workflows)
poetry run pytest tests/e2e/ -v

# All tests with coverage
poetry run pytest --cov=src --cov-report=html --cov-report=term

# Quick validation after changes
poetry run ruff check --fix . && poetry run ruff format . && poetry run pytest -v
```

**Current Status**: ✅ 66 tests passing, 93% coverage

#### LangChain Tests

```bash
cd /workspaces/web-reader/langchain

# Unit tests only
poetry run pytest tests/unit/ -v

# Integration tests (requires Ollama + FastMCP running)
poetry run pytest tests/integration/ -v

# E2E tests (requires full stack)
poetry run pytest tests/e2e/ -v

# Unit + Integration with coverage
poetry run pytest tests/unit/ tests/integration/ --cov=src --cov-report=html --cov-report=term

# Quick validation after changes
poetry run ruff check --fix . && poetry run ruff format . && poetry run pytest tests/unit/ tests/integration/ -v
```

**Current Status**: ✅ 41 tests passing (unit+integration), 85% coverage  
**Note**: E2E tests require Ollama, FastMCP, and Playwright containers running

#### Backend Tests

```bash
cd /workspaces/web-reader/backend

# Unit tests only
poetry run pytest tests/unit/ -v

# Integration tests (mocked LangChain client)
poetry run pytest tests/integration/ -v

# E2E tests (requires LangChain service running)
poetry run pytest tests/e2e/ -v

# Unit + Integration with coverage
poetry run pytest tests/unit/ tests/integration/ --cov=src --cov-report=html --cov-report=term

# Quick validation after changes
poetry run ruff check --fix . && poetry run ruff format . && poetry run pytest tests/unit/ tests/integration/ -v
```

**Current Status**: ✅ 69 tests passing (unit+integration), 89% coverage  
**Note**: E2E tests require LangChain orchestrator running

#### Frontend Tests

```bash
cd /workspaces/web-reader/frontend

# Unit tests (Vitest)
npm run test:unit

# Browser tests (Vitest browser mode)
npm run test:browser

# All tests with combined coverage
npm run test:coverage

# E2E tests (Playwright, requires backend running)
npm run test:e2e

# Linting
npm run lint
npm run typecheck

# Quick validation after changes
npm run lint:fix && npm run typecheck && npm run test:coverage
```

**Current Status**: ✅ 20 tests passing (16 unit + 4 browser), 46% combined coverage  
**Frontend uses multi-project Vitest**: Unit and browser tests both contribute to coverage

### From Docker Containers

Tests can also be executed inside running dev containers for integration/e2e testing:

#### Prerequisites

Start the infrastructure (Ollama + Playwright):

```bash
cd /workspaces/web-reader/container
./start.sh
```

Start the dev stack (optional, for full e2e):

```bash
cd /workspaces/web-reader
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d
```

#### Run Tests in Containers

```bash
cd /workspaces/web-reader
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d
```

#### Running Tests in Containers

````bash
# FastMCP unit tests
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec fastmcp pytest tests/unit --cov=src --cov-branch

# Backend unit tests
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec backend pytest tests/unit --cov=src --cov-branch

# LangChain unit tests
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec langchain pytest tests/unit --cov=src --cov-branch

# Frontend unit tests
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec frontend npm run test:unit
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec frontend npm run test:browser
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec frontend npm run test:e2e

## End-to-End Workflow (Typical Use Case)

This E2E test navigates to a real page, extracts content, and takes a screenshot using FastMCP + Playwright.

### Prerequisites

```bash
# Start external infrastructure (Playwright, Ollama, etc.)
cd /workspaces/web-reader/container
docker compose up -d

# Start the application stack (dev overlay for hot reload)
cd /workspaces/web-reader
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d --build
````

### Run the E2E test

```bash
cd /workspaces/web-reader/fastmcp
pytest tests/e2e/test_full_workflow.py -v -m e2e -k navigate_and_extract_workflow --maxfail=1
```

Expected behavior:

- Navigate to `https://example.com`
- Extract page content (non-empty text)
- Capture a screenshot (non-empty base64 string)

If you hit rate-limiting or connectivity issues, re-run the test or mock rate limiting as shown in Troubleshooting.

````

## Test Types

### Unit Tests (`tests/unit/`)

**Purpose**: Test individual functions, classes, and modules in isolation.

**Characteristics**:

- All external dependencies mocked
- Fast execution (< 1 second per test)
- No network calls, no real databases
- > 80% code coverage required

**Example**:

```python
@pytest.mark.unit
async def test_rate_limiting_logic(mocker):
    """Test rate limiting enforces 5 req/90s limit."""
    mocker.patch("src.rate_limiting._rate_limits", {})
    mocker.patch("src.rate_limiting.REQUEST_DELAY_MIN", 0)

    domain = "example.com"
    for _ in range(5):
        await enforce_rate_limit(domain)

    # Verify 5 requests tracked
    assert len(_rate_limits[domain]) == 5
````

### Integration Tests (`tests/integration/`)

**Purpose**: Test interactions between components with real services.

**Characteristics**:

- Use real external services (Playwright, Ollama, etc.)
- Slower execution (1-10 seconds per test)
- May require infrastructure to be running
- Focus on API contracts and data flow

**Example**:

```python
@pytest.mark.integration
async def test_playwright_connection(skip_if_no_playwright):
    """Test connection to live Playwright container."""
    browser = await get_browser()
    assert browser is not None

    context = await create_context()
    assert context is not None
    await context.close()
```

### E2E Tests (`tests/e2e/`)

**Purpose**: Test complete user workflows from start to finish.

**Characteristics**:

- Simulate real user scenarios
- All services must be running
- Slowest execution (10-60 seconds per test)
- Use real websites (example.com, httpbin.org)
- Verify business requirements

**Example**:

```python
@pytest.mark.e2e
async def test_research_workflow(test_urls, mocker):
    """Test complete research workflow."""
    # Mock filtering for test speed
    mocker.patch("src.tools.is_domain_allowed", return_value=True)
    mocker.patch("src.tools.enforce_rate_limit", return_value=None)

    # Navigate
    nav_result = await navigate_to(test_urls["example"])
    assert nav_result["status"] == "success"

    # Extract
    content = await get_page_content()
    assert len(content["data"]["text"]) > 0

    # Screenshot
    screenshot = await take_screenshot()
    assert len(screenshot["data"]["image"]) > 0
```

## Coverage Requirements

All projects must meet these minimum coverage thresholds:

- **Statement Coverage**: >80%
- **Branch Coverage**: >80%
- **Function Coverage**: >80%

### Checking Coverage

```bash
# FastMCP coverage
cd /workspaces/web-reader/fastmcp
pytest tests/unit --cov=src --cov-branch --cov-report=term-missing --cov-report=html
open coverage/html/index.html  # View detailed coverage report

# Backend coverage
cd /workspaces/web-reader/backend
pytest tests/unit --cov=src --cov-branch --cov-report=html
python -m http.server 8080 --directory coverage/html  # View in browser

# LangChain coverage
cd /workspaces/web-reader/langchain
pytest tests/unit --cov=src --cov-branch --cov-report=html

# Frontend coverage
cd /workspaces/web-reader/frontend
npm test -- --coverage
open coverage/index.html
```

### Coverage Reports

Coverage reports are generated in multiple formats:

- **Terminal**: `--cov-report=term-missing` shows uncovered lines
- **HTML**: `--cov-report=html` generates interactive report in `coverage/html/`
- **XML**: `--cov-report=xml` for CI/CD integration
- **JSON**: `--cov-report=json` for programmatic access

## Service-Specific Testing

### FastMCP Service

**Focus**: Browser automation, rate limiting, domain filtering

**Key Test Areas**:

- Rate limiting enforcement (5 req/90s)
- Domain allow/deny list filtering
- Browser context management (deidentified, fresh per task)
- Navigation error handling (404, timeout, network errors)
- Content extraction (text, links, metadata)
- Screenshot capture

**Dependencies for Integration Tests**:

- Playwright container must be running at `ws://playwright:3002`

### Backend Service

**Focus**: REST API, WebSocket streaming, task management

**Key Test Areas**:

- Task creation and validation
- WebSocket connection and event streaming
- Concurrent task limit enforcement
- Task cancellation and timeout handling
- Artifact storage and retrieval
- Error responses and status codes

**Dependencies for Integration Tests**:

- LangChain orchestrator must be running

### LangChain Service

**Focus**: Agent orchestration, LLM interaction, MCP tool integration

**Key Test Areas**:

- Agent initialization and configuration
- MCP client connection to FastMCP
- Tool execution and error handling
- Conversation memory management
- WebSocket callback streaming
- Prompt engineering validation

**Dependencies for Integration Tests**:

- Ollama container running with model pulled
- FastMCP server running

### Frontend Service

**Focus**: UI components, API client, WebSocket handling

**Key Test Areas**:

- Component rendering (unit)
- User interactions (browser tests)
- API client methods
- WebSocket connection management
- Form validation
- E2E user workflows

**Dependencies for E2E Tests**:

- Full stack running (frontend + backend + langchain + fastmcp + infrastructure)

## Continuous Integration

### Running Tests in CI/CD

Example GitHub Actions workflow:

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: |
          docker compose -f docker/docker-compose.yml build
          docker compose -f docker/docker-compose.yml run fastmcp pytest tests/unit --cov=src --cov-branch
          docker compose -f docker/docker-compose.yml run backend pytest tests/unit --cov=src --cov-branch
          docker compose -f docker/docker-compose.yml run langchain pytest tests/unit --cov=src --cov-branch

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3
      - name: Start infrastructure
        run: docker compose -f container/docker-compose.yml up -d
      - name: Run integration tests
        run: |
          docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d
          docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec -T fastmcp pytest tests/integration -v
```

## Troubleshooting

### Common Issues

#### "Playwright not available"

**Symptom**: Integration tests fail with "Connection refused" to Playwright

**Solution**:

```bash
# Ensure Playwright container is running
cd /workspaces/web-reader/container
docker compose up -d playwright

# Verify connection
curl -v ws://localhost:3002
```

#### "Module not found" errors

**Symptom**: Import errors when running tests

**Solution**:

```bash
# From devcontainer, ensure you're in the right directory
cd /workspaces/web-reader/<service>

# Python services: Check that src/ is in PYTHONPATH
export PYTHONPATH=/workspaces/web-reader/<service>:$PYTHONPATH

# Or use pytest's path insertion (already in conftest.py)
```

#### Low coverage warnings

**Symptom**: Tests pass but coverage < 80%

**Solution**:

```bash
# Identify uncovered code
pytest tests/unit --cov=src --cov-branch --cov-report=term-missing

# Look for "Missing" lines, add tests for those functions/branches
```

#### Tests hang or timeout

**Symptom**: Tests don't complete, hang indefinitely

**Solution**:

```bash
# Check for infinite loops or missing mocks
pytest tests/ -v --timeout=30  # Add timeout per test

# Verify async/await usage
# Check that all async fixtures are awaited properly
```

#### E2E tests fail with rate limiting

**Symptom**: E2E tests timeout waiting for rate limit window

**Solution**:

```python
# Mock rate limiting in E2E tests for speed
@pytest.mark.e2e
async def test_something(mocker):
    mocker.patch("src.tools.enforce_rate_limit", return_value=None)
    mocker.patch("src.tools.REQUEST_DELAY_MIN", 0)
    mocker.patch("src.tools.REQUEST_DELAY_MAX", 0)
    # ... rest of test
```

### Test Markers

Use markers to selectively run tests:

```bash
# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration

# Run only E2E tests
pytest tests/ -m e2e

# Skip slow tests
pytest tests/ -m "not slow"

# Run unit and integration, skip E2E
pytest tests/ -m "unit or integration"
```

### Debugging Tests

```bash
# Verbose output
pytest tests/ -vv

# Show print statements
pytest tests/ -s

# Stop on first failure
pytest tests/ -x

# Run specific test
pytest tests/unit/test_rate_limiting.py::TestRateLimiting::test_allows_requests_under_limit

# Run with debugger on failure
pytest tests/ --pdb

# Run with logging
pytest tests/ --log-cli-level=DEBUG
```

## Best Practices

1. **Write unit tests first**: Aim for >80% coverage before integration tests
2. **Mock external dependencies in unit tests**: Keep them fast and isolated
3. **Use integration tests sparingly**: Focus on critical paths and API contracts
4. **E2E tests should match user stories**: Each E2E test should validate a business requirement
5. **Keep tests independent**: Each test should work in isolation
6. **Use fixtures for common setup**: Avoid code duplication across tests
7. **Test error conditions**: Don't just test the happy path
8. **Keep tests maintainable**: Clear naming, good structure, minimal duplication
9. **Run tests locally before commit**: Use pre-commit hooks if needed
10. **Update tests with code changes**: Tests should evolve with the codebase

## References

- **Pytest Documentation**: https://docs.pytest.org/
- **Vitest Documentation**: https://vitest.dev/
- **Playwright Test Documentation**: https://playwright.dev/
- **Project Requirements**: `.github/requirements.md`
- **Implementation Guide**: `.github/implementation.md`
- **Project Plan**: `.github/project-plan.md`

---

**Last Updated**: November 15, 2025  
**Version**: 2.0
