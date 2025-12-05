# Web Reader - Project Implementation Plan (v2)

This document outlines the phased implementation plan for building the Web Reader system. Each phase has clear deliverables and dependencies. This version has:

- Multistage Dockerfile requirements (base/dev/prod) for all application services
- Development vs production compose definitions (`docker/docker-compose.yml` + `docker/docker-compose.dev.yml` layering)
- Hot reload strategy (watchfiles for Python, Vite HMR for frontend)
- Unified testing strategy (>80% coverage) runnable either inside service containers or directly in the devcontainer shell
- Standardized test directory layout (`tests/unit`, `tests/integration`, `tests/e2e`)
- Volume mount strategy (dev: source mounted, prod: code copied)
- Cross-service end-to-end and performance testing plan

## Phase 0: Project Setup and Infrastructure (Week 1)

### Goals

- Establish development environment
- Create base Docker infrastructure
- Set up project repositories

### Tasks

#### Docker & Compose Infrastructure

- [ ] Create production compose file: `docker/docker-compose.yml`
- [ ] Create development compose overlay: `docker/docker-compose.dev.yml`
  - [ ] Use `build.target: dev` for each service in dev mode
  - [ ] Add source & test volume mounts (e.g. `../backend/src:/app/src:rw`)
  - [ ] Add debug ports (backend 5671, langchain 5672, fastmcp 5673, frontend 9229 optional)
  - [ ] Add watcher/HMR commands overrides (watchfiles / uvicorn --reload / npm run dev)
- [ ] Configure bridge network for inter-container communication
- [ ] Set up volume mounts for data persistence (both modes):
  - [ ] Ollama models (`ollama-data`)
  - [ ] Configuration files (`./config`)
  - [ ] Task artifacts (`./data`)
- [ ] Add health checks for all containers
- [ ] Single shared environment file at repo root (`.env`) used by all services
- [ ] Provide `.env.example` with all required variables
- [ ] Document dev vs prod volume strategy:
  - **Dev**: Source + tests mounted (fast iteration, hot reload)
  - **Prod**: Code copied into image (immutable, smaller surface)
- [ ] Test stack: `docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d`

#### Multistage Dockerfile Requirements

For each project (`frontend`, `backend`, `langchain`, `fastmcp`):

- [ ] Stage `base`: runtime (Python 3.13 slim / Node 24 alpine), system deps, non-root user
- [ ] Stage `dev`: install dev dependencies (pytest, pytest-cov, watchfiles, debugpy / vite, vitest, playwright) via Poetry for Python services and npm for frontend, set env (`ENVIRONMENT=development`), expose debug ports, entrypoint uses watcher/HMR
- [ ] Stage `prod`: install production deps only (Poetry groups `main`/`test`/`debug` as appropriate for Python services), copy source, drop build caches, non-root execution, healthcheck friendly CMD
- [ ] Verify images build with: `docker build --target dev` and `docker build --target prod`

#### Project Structure

- [ ] Initialize monorepo structure:
  ```
  web-reader/
  ├── .github/
  │   ├── requirements.md
  │   ├── use-case.md
  │   ├── implementation.md
  │   ├── project-plan.md
  │   └── copilot-instructions.md
  ├── frontend/          # TanStack Start
  ├── backend/           # FastAPI
  ├── langchain/         # Orchestrator
  ├── fastmcp/           # MCP server
  ├── config/            # Domain lists, settings
  ├── container/         # External docker resource
  │   └── docker-compose.yml
  ├── docker/            # Application specific docker resource
  │   └── docker-compose.yml
  ├── .devcontainer/
  │   ├── devcontainer.json
  │   └── Dockerfile
  └── README.md
  ```
- [ ] Initialize Git repository with `.gitignore`
- [ ] Create `README.md` with quick start instructions

#### Dev Environment (No local Node/Python)

- [ ] Add VS Code Dev Container configuration (`.devcontainer`)
- [ ] Base image with Python 3.13 and Node.js 24 preinstalled
- [ ] Enable Docker-outside-of-Docker feature to manage external containers (Playwright, Ollama)
- [ ] Verify devcontainer can run `docker compose` against `container/docker-compose.yml`

#### Configuration & Environment Files

- [ ] Create `config/allowed-domains.txt` (initially empty)
- [ ] Create `config/disallowed-domains.txt` with common blocklists
- [ ] Create `.env.example` with all required environment variables
- [ ] Document configuration options in README

#### Testing Infrastructure (Foundational Definitions Only)

- [ ] Adopt test layout per project: `tests/unit`, `tests/integration`, `tests/e2e`
- [ ] Document test execution via devcontainer shell
- [ ] Add coverage tooling (pytest-cov / vitest + c8) to dev stage dependencies
- [ ] Minimum coverage thresholds documented (>80% statement, branch, and function)

### Deliverables

✅ Dev & prod compose files created  
✅ Multistage Dockerfile templates added to all services  
✅ Hot reload strategy documented  
✅ Project structure established  
✅ Coverage & test execution strategy documented  
✅ Shared `.env` & `.env.example` present

---

## Phase 1: FastMCP Server and Browser Tools (Week 2)

### Goals

- Implement MCP protocol server
- Create core browser automation tools
- Establish connection to Playwright container

### Tasks

#### FastMCP Server Setup

- [ ] Initialize Python project with `pyproject.toml`
- [ ] Install dependencies: `fastmcp`, `playwright`, `asyncio`
- [ ] Create server entry point (`server.py`)
- [ ] Implement browser instance management (singleton pattern)
- [ ] Add rate limiting infrastructure (per-domain tracking)
- [ ] Implement domain filtering (load from config files)
- [ ] Configure logging via Loguru using `.env` (`LOG_LEVEL`, `LOG_TARGET`, `LOG_FILE`)

#### Core Browser Tools

- [ ] `navigate_to(url, wait_until)` - with error handling for 404, 403, 429
- [ ] `get_page_content()` - extract title, text, links, metadata
  - [ ] Return clean, truncated text (≤10k chars) and disclosure flag when truncated
- [ ] `extract_structured_data(schema)` - basic schema-based extraction
- [ ] `take_screenshot(full_page)` - capture and return base64 image
- [ ] `get_page_structure()` - return DOM structure for LLM understanding

#### Rate Limiting and Bot Protection

- [ ] Implement 5 requests per 90 seconds per domain
- [ ] Add randomized 10-20 second delays between requests
- [ ] Handle 429 responses with exponential backoff
- [ ] Rotate user agents from pool (10+ variants)
- [ ] Randomize viewport dimensions

#### Domain Filtering

- [ ] Load allow/deny lists from config files at startup
- [ ] Implement wildcard matching (`*.example.com`)
- [ ] Check domain before each navigation
- [ ] robots.txt parsing and compliance (optional feature)

#### Testing (FastMCP)

Directory layout: `fastmcp/tests/{unit,integration,e2e}`

- [ ] Unit tests for rate limiting logic
- [ ] Unit tests for domain filtering
- [ ] Integration tests with live Playwright container
- [ ] Test error handling (404, timeout, network errors)
- [ ] Verify logging to console and file (based on `.env`)

Unit (>80% coverage):

- [ ] `tests/unit/test_rate_limiting.py`
- [ ] `tests/unit/test_domain_filtering.py`
- [ ] `tests/unit/test_browser_management.py`
- [ ] `tests/unit/test_tools.py`

Integration (mock external pieces except Playwright container):

- [ ] `tests/integration/test_playwright_integration.py`
- [ ] `tests/integration/test_tool_execution.py`

E2E (live Playwright + real navigation):

- [ ] `tests/e2e/test_full_workflow.py`

Devcontainer (preferred):

```
cd fastmcp
poetry install --with dev
poetry run pytest tests/unit --cov=src --cov-branch --cov-report=term-missing
poetry run pytest tests/integration -v
poetry run pytest tests/e2e -v --maxfail=1
```

Optional inside container:

```
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec fastmcp poetry run pytest tests/unit --cov=src --cov-branch --cov-report=term-missing
```

### Deliverables

✅ FastMCP server running and exposing tools  
✅ Core browser automation tools functional  
✅ Rate limiting and bot protection working  
✅ Domain filtering operational  
✅ Test suite passing (>80% coverage)

---

## Phase 2: Backend API and Task Management (Week 3)

### Goals

- Create REST API for task management
- Implement WebSocket streaming
- Build task queue and concurrency management

### Tasks

#### FastAPI Server Setup

- [ ] Initialize FastAPI project with `pyproject.toml`
- [ ] Install dependencies: `fastapi`, `uvicorn`, `websockets`, `pydantic`
- [ ] Create API router structure
- [ ] Configure permissive CORS for local development (tighten in production phase)
- [ ] Add request validation with Pydantic models
- [ ] Configure logging via Loguru using `.env`

#### REST API Endpoints

- [ ] POST `/api/tasks` - Create new research task
  - [ ] Validate question (max 1000 chars)
  - [ ] Validate seed URL format (if provided)
  - [ ] Generate unique task ID (UUID)
  - [ ] Add to task queue
- [ ] GET `/api/tasks/{id}` - Get task status and results
- [ ] DELETE `/api/tasks/{id}` - Cancel running task
- [ ] GET `/api/history` - List all tasks with filters

#### WebSocket Streaming

- [ ] WebSocket endpoint: `/api/tasks/{id}/stream`
- [ ] Accept connections and validate task ID
- [ ] Stream agent events in real-time
- [ ] Handle disconnections gracefully
- [ ] Implement reconnection logic

#### Task Queue Management

- [ ] In-memory task storage (dict-based, replace with DB later)
- [ ] Task lifecycle states: queued → running → completed/failed/cancelled
- [ ] Concurrency limit enforcement (max 5 simultaneous tasks)
- [ ] Fair scheduling (FIFO queue)
- [ ] Task timeout enforcement (default 120 seconds)

#### Task Artifacts

- [ ] Store full conversation history
- [ ] Save navigation timeline (URLs, timestamps, HTTP statuses)
- [ ] Persist screenshots (filesystem)
- [ ] Record final answer with citations
- [ ] Log errors and recovery attempts

#### Persistence Strategy (MVP)

- [ ] Filesystem-based artifact store (JSON and images per task directory)
- [ ] No database required in MVP; add DB integration in future phase

#### Testing (Backend)

Directory layout: `backend/tests/{unit,integration,e2e}`

- [ ] Unit tests for API endpoints
- [ ] Integration tests for WebSocket streaming
- [ ] Load testing for concurrent task handling
- [ ] Test timeout and cancellation logic

Unit (>80% coverage): models, task queue, artifacts
Integration: REST + WebSocket with mocked LangChain / FastMCP
E2E: full task lifecycle with live orchestrator & tool server

Devcontainer:

```
cd backend
poetry install --with test
poetry run pytest tests/unit --cov=src --cov-branch --cov-report=term
poetry run pytest tests/integration -v
poetry run pytest tests/e2e -v
```

Optional container:

```
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec backend poetry run pytest tests/unit
```

### Deliverables

✅ Backend API running and accepting requests  
✅ WebSocket streaming functional  
✅ Task queue managing concurrency  
✅ Task artifacts persisted  
✅ API tests passing

---

## Phase 3: LangChain Orchestrator (Week 4)

### Goals

- Implement agentic research workflow
- Integrate LangChain with FastMCP tools
- Add conversation memory and callbacks

### Tasks

#### LangChain Setup

- [ ] Initialize Python project with LangChain dependencies
- [ ] Install: `langchain`, `langchain-community`, `langchain-ollama`
- [ ] Configure ChatOllama client (connect to Ollama container)
- [ ] Set model parameters (qwen3:8b, temperature=0.1)
- [ ] Read all config from `.env` (Ollama host/port/model, limits)

#### MCP Tool Integration

- [ ] Create MCP client wrapper for FastMCP server
- [ ] Wrap MCP tools as LangChain `StructuredTool` instances
- [ ] Define tool schemas with Pydantic
- [ ] Add tool descriptions for LLM understanding

#### Agent Configuration

- [ ] Implement ReAct agent pattern
- [ ] Configure ConversationBufferMemory
- [ ] Set max iterations (15)
- [ ] Add early stopping logic
- [ ] Create system prompt for research tasks
  - [ ] Include link prioritization guidance (authority domains, relevant anchors, max N links/page)

#### Callback Handler

- [ ] Implement custom WebSocket callback handler
- [ ] Stream events: thinking, tool_call, tool_result, complete, error
- [ ] Add timing information to events
- [ ] Handle callback errors gracefully

#### Prompt Engineering

- [ ] System prompt defining research guidelines
- [ ] Few-shot examples for common scenarios:
- [ ] Web search workflow
- [ ] Seed URL navigation
- [ ] Multi-page synthesis
- [ ] Error recovery instructions
- [ ] State awareness guidelines

#### Error Handling

- [ ] Retry logic with exponential backoff
- [ ] Graceful degradation to partial results
- [ ] Structured error reporting
- [ ] Recovery suggestions for common errors

#### Testing (LangChain)

Directory layout: `langchain/tests/{unit,integration,e2e}`

- [ ] Unit tests for tool wrappers
- [ ] Integration tests with mock MCP server
- [ ] End-to-end tests with live Ollama
- [ ] Test error recovery scenarios

Unit: tool wrappers, MCP client, agent config, callbacks
Integration: agent execution with mocked LLM / simulated MCP
E2E: research workflow w/ live Ollama + FastMCP

Devcontainer:

```
cd langchain
poetry install --with test
poetry run pytest tests/unit --cov=src --cov-branch --cov-report=term
poetry run pytest tests/integration -v
poetry run pytest tests/e2e -v
```

Optional container:

```
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec langchain poetry run pytest tests/unit
```

### Deliverables

✅ LangChain agent executing research tasks  
✅ Tools integrated via MCP protocol  
✅ WebSocket callbacks streaming to backend  
✅ Error handling and recovery working  
✅ System prompts optimized

---

## Phase 4: Frontend Development (Week 5-6)

### Goals

- Build user-facing web application
- Implement real-time task monitoring
- Create task history and management UI

### Tasks

#### TanStack Start Setup

- [ ] Initialize TanStack Start project with TypeScript
- [ ] Install dependencies: `@tanstack/start`, `@tanstack/react-router`, `@tanstack/react-query`
- [ ] Configure build and development scripts
- [ ] Set up Tailwind CSS or preferred styling solution
- [ ] Configure logging via Pino with Pretty in dev and file output when enabled in `.env`

#### Core Components

- [ ] `TaskForm` - Question input and options
  - [ ] Question textarea (required)
  - [ ] Seed URL input (optional)
  - [ ] Advanced options accordion (depth, pages, time budget)
  - [ ] Submit button with loading state
- [ ] `TaskDetail` - Live task monitoring
  - [ ] Activity log with auto-scroll
  - [ ] Live screenshot display
  - [ ] Progress indicators
  - [ ] Cancel button
- [ ] `AnswerDisplay` - Show results with citations
  - [ ] Answer text with formatting
  - [ ] Citation list with links
  - [ ] Confidence score display
  - [ ] Export button (markdown/JSON)
- [ ] `TaskHistory` - List past tasks
  - [ ] Table with filters (status, date)
  - [ ] Search by question text
  - [ ] Link to task details
  - [ ] Delete button

#### API Client

- [ ] TypeScript API client with type safety
- [ ] REST methods: createTask, getTask, cancelTask, listTasks
- [ ] WebSocket connection manager with reconnection
- [ ] Event type definitions

#### Real-time Updates

- [ ] WebSocket connection per task
- [ ] Event handler for agent events
- [ ] Automatic reconnection on disconnect
- [ ] Message buffering during reconnection

#### Routing

- [ ] Home page (`/`) - Task submission form
- [ ] Task detail page (`/tasks/:id`) - Live monitoring
- [ ] History page (`/history`) - Past tasks

#### Testing (Frontend)

Directory layout: `frontend/tests/{unit,integration,e2e,browser}`

- [ ] Component unit tests (Vitest)
- [ ] E2E tests with Playwright
- [ ] Test WebSocket reconnection logic
- [ ] Test form validation

Unit: API client, WebSocket logic
Browser (Vitest browser mode): interactive components
Integration: task submission flow (mock backend/WebSocket)
E2E: full user journey with running stack

Devcontainer:

```
cd frontend
npm run test:unit
npm run test:browser
npx playwright test tests/e2e
```

Optional container:

```
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec frontend npm run test:unit
```

#### Docker Image

- [ ] Create `Dockerfile` for production build
- [ ] Multi-stage build (build + serve)
- [ ] Optimize image size (alpine base)
- [ ] Configure for Docker Compose

### Deliverables

✅ Functional web UI for task submission  
✅ Real-time task monitoring with WebSocket  
✅ Answer display with citations  
✅ Task history and management  
✅ Frontend tests passing  
✅ Dockerized frontend

---

## Phase 5: Cross-Service Integration & End-to-End (Week 7)

### Goals

- Integrate all components
- Comprehensive E2E testing
- Performance optimization

### Tasks

#### System Integration

- [ ] Launch dev stack: `docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d`
- [ ] Validate health endpoints & debug ports reachable
- [ ] Confirm hot reload triggers (edit a file in each service)
- [ ] Environment variables configured
- [ ] Health checks endpoints passing for all containers

#### Cross-Service End-to-End Testing

- [ ] Test UC-01: Question → Web Search → Answer
  - [ ] DuckDuckGo search working
  - [ ] SERP parsing correct
  - [ ] Link following functional
  - [ ] Answer synthesis accurate
  - [ ] Citations provided
- [ ] Test UC-02: Question → Seed URL → Linked Reading
  - [ ] Navigate to seed URL
  - [ ] Extract content
  - [ ] Follow relevant links
  - [ ] Synthesize answer
- [ ] Test UC-03: Rate Limiting and Guardrails
  - [ ] 5 requests per 90 seconds enforced
  - [ ] 10-20 second delays working
  - [ ] 429 handling functional
  - [ ] Domain filtering operational
- [ ] Test UC-04: Error Handling
  - [ ] 404 errors handled gracefully
  - [ ] Timeout recovery working
  - [ ] Network errors retried
  - [ ] Partial results returned

#### Performance & Load Testing

- [ ] Load testing with multiple concurrent tasks
- [ ] Measure average response times
- [ ] Check memory usage under load
- [ ] Test container resource limits

#### Observability

- [ ] Structured logging working across all services (Pino/Loguru)
- [ ] Trace IDs propagating correctly
- [ ] Health check endpoints responding
- [ ] Error logs captured and formatted

#### Documentation

- [ ] Update README with:
  - [ ] Quick start guide (3 steps)
  - [ ] Configuration options
  - [ ] Troubleshooting tips
- [ ] Create user guide with examples
- [ ] Document API endpoints (OpenAPI/Swagger)
- [ ] Write developer setup guide

### Deliverables

✅ Full stack integrated (dev mode & prod build)  
✅ All use case scenarios pass E2E tests  
✅ Coverage reports >80% each project  
✅ Performance targets validated (60s for 95% of queries)
✅ Observability confirmed  
✅ Documentation (README + testing guide) updated

---

## Phase 5.5: CI/CD Pipeline with GitHub Actions (Week 7.5)

### Goals

- Implement automated build and test pipeline
- Detect changed projects and build only what's needed
- Create production-ready Docker images
- Block PRs with failing tests or insufficient coverage

### Tasks

#### GitHub Actions Workflow Design

- [ ] Create `.github/workflows/pr-validation.yml` workflow
- [ ] Trigger on pull requests to `main` branch
- [ ] Detect changed files and determine affected projects
- [ ] Run jobs conditionally based on changed projects

#### Change Detection Strategy

- [ ] Use `tj-actions/changed-files` or similar action
- [ ] Define file patterns for each project:
  - `frontend/**` → Frontend project changed
  - `backend/**` → Backend project changed
  - `langchain/**` → LangChain project changed
  - `fastmcp/**` → FastMCP project changed
  - `docker/**` or `.env.example` → All projects may be affected
- [ ] Output matrix of changed projects for parallel job execution

#### Build Jobs (Per Project)

Each project job should:

- [ ] Check out repository code
- [ ] Set up Docker Buildx for multi-stage builds
- [ ] Build dev stage Docker image (includes test dependencies)
- [ ] Cache Docker layers for faster builds

**Frontend Build:**

- [ ] Set up Node.js 24 environment
- [ ] Install dependencies with caching
- [ ] Run linting (`npm run lint`)
- [ ] Run type checking (`tsc --noEmit`)
- [ ] Build production assets (`npm run build`)
- [ ] Build production Docker image (target: `prod`)

**Backend Build:**

- [ ] Set up Python 3.13 environment
- [ ] Install dependencies with pip cache
- [ ] Run linting (`ruff check` or `flake8`)
- [ ] Run type checking (`mypy`)
- [ ] Build production Docker image (target: `prod`)

**LangChain Build:**

- [ ] Set up Python 3.13 environment
- [ ] Install dependencies with pip cache
- [ ] Run linting and type checking
- [ ] Build production Docker image (target: `prod`)

**FastMCP Build:**

- [ ] Set up Python 3.13 environment
- [ ] Install dependencies with pip cache
- [ ] Run linting and type checking
- [ ] Build production Docker image (target: `prod`)

#### Test Jobs (Per Project)

**Frontend Tests:**

- [ ] Run unit tests (`npm run test:unit`)
- [ ] Run browser component tests (`npm run test:browser`)
- [ ] Generate coverage report
- [ ] Enforce >80% coverage threshold
- [ ] Upload coverage artifact

**Backend Tests:**

- [ ] Start required infrastructure (Ollama, Playwright) via Docker Compose
- [ ] Run unit tests (`poetry run pytest tests/unit --cov=src --cov-branch`)
- [ ] Run integration tests (`poetry run pytest tests/integration`)
- [ ] Run E2E tests (`poetry run pytest tests/e2e`)
- [ ] Enforce >80% coverage threshold
- [ ] Upload coverage artifact
- [ ] Cleanup infrastructure containers

**LangChain Tests:**

- [ ] Start required infrastructure (Ollama, FastMCP) via Docker Compose
- [ ] Run unit tests with coverage
- [ ] Run integration tests
- [ ] Run E2E tests
- [ ] Enforce >80% coverage threshold
- [ ] Upload coverage artifact
- [ ] Cleanup infrastructure

**FastMCP Tests:**

- [ ] Start Playwright container via Docker Compose
- [ ] Run unit tests with coverage
- [ ] Run integration tests
- [ ] Run E2E tests
- [ ] Enforce >80% coverage threshold
- [ ] Upload coverage artifact
- [ ] Cleanup Playwright container

#### Image Creation

- [ ] Build production Docker images (target: `prod`) for changed projects
- [ ] Tag images with PR number or commit SHA
- [ ] Save images as artifacts (optional, for review)
- [ ] Do NOT push images to registry (only build and validate)
- [ ] Display image size and layers in job summary

#### Quality Gates

- [ ] All linting must pass (exit code 0)
- [ ] All type checks must pass
- [ ] All tests must pass (zero failures)
- [ ] Coverage must meet >80% threshold per project
- [ ] Docker builds must succeed for prod target
- [ ] Block PR merge if any gate fails

#### Workflow Optimization

- [ ] Use matrix strategy for parallel project builds/tests
- [ ] Cache Docker layers between builds
- [ ] Cache npm/pip dependencies
- [ ] Use `actions/cache@v3` for dependency caching
- [ ] Set reasonable timeouts (30min max per job)
- [ ] Fast-fail: cancel remaining jobs on first failure (optional)

#### Workflow Status Reporting

- [ ] Add job summary with build/test results
- [ ] Display coverage percentages
- [ ] List Docker image sizes
- [ ] Show which projects were built/tested
- [ ] Annotate PR with status check

#### Documentation

- [ ] Document GitHub Actions workflow in `README.md`
- [ ] Create `.github/workflows/README.md` explaining workflow logic
- [ ] Document required repository secrets (if any)
- [ ] Add badge to main README showing build status

### Example Workflow Structure

```yaml
name: PR Validation

on:
  pull_request:
    branches: [main]

jobs:
  detect-changes:
    # Detect which projects changed

  build-frontend:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    # Build and test frontend

  build-backend:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend == 'true'
    # Build and test backend

  build-langchain:
    needs: detect-changes
    if: needs.detect-changes.outputs.langchain == 'true'
    # Build and test langchain

  build-fastmcp:
    needs: detect-changes
    if: needs.detect-changes.outputs.fastmcp == 'true'
    # Build and test fastmcp
```

### Deliverables

✅ GitHub Actions workflow implemented  
✅ Automated build and test for all projects  
✅ Change detection working correctly  
✅ Production Docker images building successfully  
✅ Coverage enforcement blocking bad PRs  
✅ Workflow documentation complete  
✅ CI/CD pipeline operational

---

## Phase 6: Security Hardening and Production Prep (Week 8)

### Goals

- Implement security best practices
- Prepare for production deployment
- Final optimization and polish

### Tasks

#### Security Hardening

- [ ] Non-root users in all containers
- [ ] Read-only filesystems where possible
- [ ] Container resource limits (CPU, memory)
- [ ] Network isolation (Playwright no internet by default)
- [ ] Input validation and sanitization
- [ ] Output sanitization (XSS prevention)
- [ ] PII redaction in logs
- [ ] (Future) JWT authentication for API
- [ ] Tighten CORS to explicit allowlist for production

#### Production Configuration

- [ ] Production `docker-compose.yml` variant
- [ ] Environment-specific configs (dev, staging, prod)
- [ ] Secrets management (Docker secrets or external vault)
- [ ] SSL/TLS configuration (reverse proxy)
- [ ] Log aggregation setup (optional)
- [ ] Monitoring and alerting (optional)

#### Data Management

- [ ] Implement data retention policy (30 days default)
- [ ] Automated cleanup of old tasks
- [ ] Database integration and backups (if/when DB is added)
- [ ] Export API for task artifacts

#### Final Testing

- [ ] Security audit of all components
- [ ] Penetration testing (basic)
- [ ] Load testing at production scale
- [ ] Failover and recovery testing

#### Deployment Documentation

- [ ] Deployment guide for different platforms:
  - [ ] Docker Compose (single host)
  - [ ] Kubernetes (optional)
  - [ ] Cloud providers (AWS, GCP, Azure)
- [ ] Monitoring setup guide
- [ ] Backup and recovery procedures
- [ ] Upgrade/migration guide

### Deliverables

✅ Security hardened system  
✅ Production-ready configuration  
✅ Data management policies in place  
✅ Deployment documentation complete  
✅ System ready for production use

---

## Phase 7 (Optional): Advanced Features (Week 9+)

### Goals

- Implement vector database integration
- Add advanced caching
- Multi-modal capabilities

### Tasks

#### Vector Database Integration (UC-FUTURE-01)

- [ ] Add ChromaDB or Qdrant container to Docker Compose
- [ ] Configure embedding model (sentence-transformers)
- [ ] Create collections for scraped pages
- [ ] Implement storage after each page visit
- [ ] Add semantic search endpoint
- [ ] Integrate with LangChain as VectorStoreRetrieverMemory
- [ ] Implement cache checking logic before browsing

#### Caching System (UC-FUTURE-02)

- [ ] Implement URL normalization
- [ ] Content hashing for deduplication
- [ ] TTL-based cache invalidation
- [ ] Cache hit/miss metrics
- [ ] Expose cache status in API responses

#### Multi-modal Support

- [ ] Vision model integration for screenshot analysis
- [ ] Image-based evidence in answers
- [ ] Screenshot comparison across pages
- [ ] Visual grounding in citations

#### Performance Optimizations

#### Observability Enhancements

- [ ] HAR export of network traces
- [ ] DOM snapshots on errors
- [ ] Optional video recording of sessions

- [ ] Parallel page loading (multiple contexts)
- [ ] Smart selector caching
- [ ] Browser session reuse (when safe)
- [ ] Response streaming optimization

### Deliverables

✅ Vector DB integrated for RAG  
✅ Intelligent caching reducing redundant browsing  
✅ Multi-modal capabilities (if implemented)  
✅ Performance improvements documented

---

## Success Metrics & Coverage Verification

### Phase Completion Criteria

Each phase must meet these criteria before moving to the next:

- [ ] All tasks completed
- [ ] Unit tests (>80% statement/branch/function) for code-focused phases
- [ ] Integration tests passing (where defined)
- [ ] E2E tests established by Phase 5
- [ ] Documentation updated (plan + implementation)
- [ ] Dev & prod images build successfully
- [ ] Hot reload verified (dev targets)
- [ ] Tests runnable from devcontainer shell
- [ ] Deliverables verified

### Overall Project Success

- ✅ Meets all functional requirements from requirements.md
- ✅ Passes all use cases from use-case.md
- ✅ Performance targets achieved (NFR-01)
- ✅ Security requirements met (TR-09, TR-11)
- ✅ Observability in place (TR-12)
- ✅ Documentation complete and accurate

---

## Risk Management

### High-Risk Items

1. **LLM Reliability**: Tool calling may be inconsistent
   - _Mitigation_: Extensive prompt engineering, fallback strategies
2. **Bot Detection**: Sites may block automated browsing
   - _Mitigation_: Robust rate limiting, human-like behaviors, graceful degradation
3. **Performance**: Research tasks may exceed time budgets

   - _Mitigation_: Timeouts, partial results, optimization

4. **Ollama Resource Usage**: LLM inference may be slow on CPU
   - _Mitigation_: GPU support, smaller models, caching

### Medium-Risk Items

- **Browser Compatibility**: Some sites may not work headlessly
- **Network Reliability**: Transient failures during browsing
- **Concurrency Limits**: Scaling beyond 5 concurrent tasks
- **Memory Leaks**: Long-running containers
- **CI/CD Infrastructure Costs**: GitHub Actions minutes and storage
  - _Mitigation_: Optimize workflows, use caching, conditional execution

---

## Timeline Summary

| Phase                  | Duration  | Key Deliverable           |
| ---------------------- | --------- | ------------------------- |
| 0: Setup               | Week 1    | Docker infrastructure     |
| 1: FastMCP             | Week 2    | Browser automation tools  |
| 2: Backend             | Week 3    | Task management API       |
| 3: LangChain           | Week 4    | Agentic orchestration     |
| 4: Frontend            | Weeks 5-6 | User interface            |
| 5: Integration         | Week 7    | Full system working       |
| 5.5: CI/CD Pipeline    | Week 7.5  | GitHub Actions automation |
| 6: Production          | Week 8    | Production-ready          |
| 7: Advanced (Optional) | Week 9+   | Vector DB, caching        |

**Total Time: 8 weeks to production, +optional enhancements**

---

**Document Version**: 2.2  
**Last Updated**: November 17, 2025  
**Status**: Updated (added Phase 5.5: CI/CD Pipeline with GitHub Actions)
