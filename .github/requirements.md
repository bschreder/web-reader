# Web Reader - System Requirements

## Project Overview

### Purpose

Enable users to ask natural language questions and receive well-researched, cited answers by leveraging an AI agent that can autonomously browse the web in a privacy-preserving, deidentified manner.

### Vision

A production-ready system that combines the reasoning capabilities of large language models with automated web browsing to provide accurate, traceable answers to user queries—eliminating the need for manual web research while maintaining privacy, security, and ethical web scraping practices.

### Core Value Proposition

- **Time Savings**: Automated multi-page research that would take humans 10-30 minutes
- **Accuracy**: Grounded answers with verifiable citations and source attribution
- **Privacy**: Deidentified browsing with no tracking or PII exposure
- **Transparency**: Complete audit trail of pages visited and reasoning steps
- **Scalability**: Containerized architecture supporting concurrent research tasks

## Business Requirements

### BR-01: Natural Language Question Answering

**Need**: Users must be able to ask questions in natural language and receive comprehensive, researched answers.

**Criteria**:

- Accept questions via web UI in natural language
- Return answers with confidence scores
- Provide citations (URLs) for all factual claims
- Include relevant snippets from source pages
- Support follow-up questions within the same context

**Why**: Reduces friction for users who need quick, researched answers without manual browsing.

### BR-02: Web Search Integration

**Need**: System must perform web searches to discover relevant content.

**Criteria**:

- Default to DuckDuckGo for privacy-first searching
- Support alternative search engines (Bing, Google, custom)
- Parse search engine result pages (SERPs) for titles, snippets, URLs
- Rank and prioritize results for relevance
- Handle search engine-specific formatting and pagination

**Why**: Automated discovery of relevant web pages is essential for comprehensive answers.

### BR-03: Intelligent Link Following

**Need**: System must navigate from search results or seed URLs to gather evidence.

**Criteria**:

- Follow links up to configurable depth (default: 3 levels)
- Prioritize same-domain links when specified
- Detect and avoid circular link loops
- Support both search-driven and seed URL-driven workflows
- Respect user-specified domain allow/deny lists

**Why**: Many answers require synthesizing information from multiple related pages.

### BR-04: Privacy and Deidentification

**Need**: Browsing must be privacy-preserving with no persistent tracking.

**Criteria**:

- Fresh browser context per task (no cookies, storage, or history)
- Randomized user agents and browser fingerprints
- No PII in requests, logs, or stored artifacts
- Optional egress proxy support
- Tracking prevention enabled by default

**Why**: Protects user privacy and prevents personalization/tracking of automated browsing.

### BR-05: Bot Detection Avoidance

**Need**: System must operate reliably without being blocked as a bot.

**Criteria**:

- Randomized delays between requests (10-20 seconds)
- Rate limiting: max 5 requests per 90 seconds
- Human-like interaction patterns (scrolling, mouse movements)
- Rotating user agents across requests
- Handle 429 (Too Many Requests) responses gracefully
- Support for CAPTCHA escalation to manual review

**Why**: Ensures system reliability and respectful usage of web resources.

### BR-06: Ethical Web Scraping

**Need**: System must respect website policies and ethical scraping guidelines.

**Criteria**:

- robots.txt compliance (enabled by default)
- Configurable domain allow/deny lists (persisted to files)
- Transparent user agent identification
- Respect for rate limits and 429 responses
- No circumvention of paywalls or authentication unless explicitly authorized

**Why**: Maintains ethical standards and reduces legal/reputational risk.

### BR-07: Real-time Progress Visibility

**Need**: Users must see live progress of research tasks.

**Criteria**:

- WebSocket streaming of agent thoughts and actions
- Live display of pages being visited
- Real-time screenshots of browser state
- Progress indicators (pages visited, time elapsed, depth level)
- Ability to cancel in-flight tasks

**Why**: Builds trust and provides transparency into automated research process.

### BR-08: Source Attribution and Traceability

**Need**: All answers must be traceable to specific sources.

**Criteria**:

- Every claim linked to source URL
- Page titles and snippets included with citations
- Optional screenshots for visual grounding
- Timestamps of when pages were accessed
- Full audit trail of navigation history

**Why**: Enables verification of accuracy and builds confidence in results.

### BR-09: Error Handling and Partial Results

**Need**: System must gracefully handle failures and provide partial results.

**Criteria**:

- Continue with partial results on timeout or rate limits
- Clear error messages for failed navigations (404, 403, network errors)
- Retry logic with exponential backoff for transient failures
- Fallback strategies (HTML-only extraction for JS-heavy sites)
- User notification of degraded quality or incomplete results

**Why**: Real-world web browsing is unpredictable; graceful degradation ensures usability.

### BR-10: Multi-user Concurrency

**Need**: System must support multiple simultaneous research tasks.

**Criteria**:

- Isolated browser contexts per task
- Task queue with configurable concurrency limits (default: 5)
- Resource limits per task (pages, time, depth)
- Fair scheduling and priority management

**Why**: Enables multi-user deployment and improved utilization of resources.

## User Requirements

### UR-01: Simple Question Submission

**User Story**: As a user, I want to type a question and get an answer without configuring complex parameters.

**Acceptance**:

- Single text input for question
- Reasonable defaults (search engine, depth, time limits)
- "Ask" button submits task
- Advanced options available but not required

### UR-02: Seed URL Support

**User Story**: As a user, I want to provide a starting URL when I know where to look.

**Acceptance**:

- Optional seed URL field
- System starts from provided URL instead of searching
- Same link-following behavior applies
- Clear indication when seed URL fails (404, etc.)

### UR-03: Live Progress Monitoring

**User Story**: As a user, I want to see what the agent is doing in real-time.

**Acceptance**:

- Live log of agent thoughts ("Searching for...", "Reading page...")
- List of visited URLs with timestamps
- Current browser viewport screenshot updates
- Progress bar or percentage indicator

### UR-04: Answer with Citations

**User Story**: As a user, I want to verify answer accuracy by checking sources.

**Acceptance**:

- Answer text clearly separated from citations
- Clickable citation links to original pages
- Snippets showing relevant portions of source pages
- Indication of confidence level or uncertainty

### UR-05: Task History

**User Story**: As a user, I want to review past questions and answers.

**Acceptance**:

- Persistent history of completed tasks
- Search and filter by date, question text, or status
- Ability to re-run previous questions
- Export results as markdown or JSON

### UR-06: Controllable Depth and Scope

**User Story**: As a power user, I want to control how deeply the agent researches.

**Acceptance**:

- Adjustable max link depth (0 = unlimited)
- Max pages limit
- Time budget setting
- Domain filtering (allow/deny lists)

## System Architecture

The system follows a layered architecture with clear separation of concerns:

### Layer 1: User Interface

- **Technology**: TanStack Start (React SPA/SSR with TypeScript)
- **Purpose**: User-facing web application for task submission and monitoring
- **Responsibilities**: Form inputs, real-time WebSocket updates, result visualization, task history
- **Container**: Node.js 24 alpine

### Layer 2: Backend API

- **Technology**: FastAPI (Python)
- **Purpose**: REST API and WebSocket server for client-server communication
- **Responsibilities**: Request validation, authentication, WebSocket streaming, task queue management
- **Container**: Python 3.13 slim

### Layer 3: Orchestration

- **Technology**: LangChain Python with ReAct agent pattern
- **Purpose**: Agentic workflow coordination and decision-making
- **Responsibilities**: Tool selection, conversation memory, error recovery, prompt engineering, callback streaming
- **Container**: Python 3.13 slim
- **Why Required**: Provides proven agent patterns, memory management, and callback infrastructure essential for complex multi-step workflows. Not optional—core to the agentic research capability.

### Layer 4: Tool Server

- **Technology**: FastMCP Python with MCP protocol
- **Purpose**: MCP protocol server exposing browser automation primitives
- **Responsibilities**: Tool definitions, browser command execution, result formatting, state management
- **Container**: Python 3.13 slim

### Layer 5: Browser Execution

- **Technology**: Microsoft Playwright (containerized)
- **Purpose**: Headless browser for actual web interactions
- **Responsibilities**: Page rendering, JavaScript execution, screenshot capture, network interception
- **Container**: `mcr.microsoft.com/playwright:v1.56.1-noble`

### Layer 6: LLM Inference

- **Technology**: Ollama with function-calling models
- **Purpose**: Large language model for reasoning and text generation
- **Responsibilities**: Query understanding, tool selection, answer synthesis, confidence scoring
- **Container**: `ollama/ollama:latest`
- **Models**: llama3.2, qwen2.5, mistral (function-calling capable)

### Optional Layer 7: Vector Database (Future)

- **Technology**: ChromaDB or Qdrant
- **Purpose**: Semantic search and caching of previously visited content
- **Responsibilities**: Content storage, embedding generation, similarity search, RAG support
- **Status**: Deferred to future enhancement phase

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  TanStack Start Frontend                     │
│                    (User Interface)                          │
│                                                              │
│  - React SPA/SSR application                                 │
│  - Real-time updates (WebSocket/SSE)                         │
│  - Task submission and monitoring                            │
│  - Browser session visualization                             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Backend API Layer                          │
│                       (FastAPI)                              │
│                                                              │
│  - REST API endpoints                                        │
│  - WebSocket for streaming responses                         │
│  - Authentication & authorization                            │
│  - Request/response validation                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              LangChain Orchestration Layer                   │
│                  (Agentic Workflow)                          │
│                                                              │
│  - Agent executor with ReAct pattern                         │
│  - Conversation memory & history                             │
│  - Tool selection logic                                      │
│  - Error recovery & retry strategies                         │
│  - Prompt templates & few-shot examples                      │
│  - Callback handlers for streaming                           │
└──────┬───────────────────────────────────────┬──────────────┘
       │ MCP Protocol                          │ LLM API
       │                                       │
┌──────▼──────────────────────┐    ┌──────────▼──────────────┐
│     FastMCP Server          │    │   Ollama Container      │
│  (Tool Provider)            │    │   ollama/ollama         │
│                             │    │                         │
│  Browser Tools:             │    │  - LLM inference        │
│  - navigate(url)            │    │  - Tool calling         │
│  - click(selector)          │    │  - Model: qwen3:8b      │
│  - type(selector, text)     │    │  - Structured output    │
│  - screenshot()             │    └─────────────────────────┘
│  - get_page_content()       │
│  - extract_data(schema)     │
└──────┬──────────────────────┘
       │ Playwright API
       │
┌──────▼────────────────────────────────────────────────────┐
│              Playwright Container                          │
│         mcr.microsoft.com/playwright:v1.56.1-noble        │
│                                                            │
│  - Chromium/Firefox/WebKit browsers                        │
│  - Browser contexts and sessions                           │
│  - CDP (Chrome DevTools Protocol) support                  │
└────────────────────────────────────────────────────────────┘
```

### Network Architecture

**Docker Network Configuration**:

- **Network Mode**: Bridge network with DNS-based service discovery
- **Inter-container Communication**:
  - Frontend ↔ Backend API: HTTP/WebSocket
  - Backend API ↔ LangChain: Internal function calls (same container or IPC)
  - LangChain ↔ FastMCP: MCP over stdio/HTTP
  - LangChain ↔ Ollama: HTTP API (port 11434)
  - FastMCP ↔ Playwright: HTTP/WebSocket (port 3002)
- **External Access**:
  - Frontend: Port 3000 (exposed to host)
  - Backend API: Port 8000 (optional, for direct API access)
  - All other services: Internal only

**Why**: Minimizes attack surface while enabling seamless inter-container communication.

## Technical Requirements

### Developer Environment

**Requirement**: Provide a VS Code Dev Container for local development without installing Node.js or Python on the host.

**Details**:

- Base image includes Python 3.13 and Node.js 24
- Docker-outside-of-Docker enabled so the devcontainer can control external containers
- The devcontainer must be able to run and interact with the existing compose stack under `container/` (e.g., Playwright, Ollama)
- Shared root `.env` is mounted/available inside the devcontainer

**Why**: Streamlines onboarding, ensures consistent toolchains, and allows interaction with external containers from within the dev environment.

### TR-01: Container Infrastructure

**Requirement**: All services must run in isolated Docker containers with health checks and resource limits.

**Containers Required**:

1. **Frontend** (Node.js 24 alpine) - TanStack Start application
2. **Backend API** (Python 3.13 slim, FastAPI) - REST/WebSocket server
3. **LangChain Orchestrator** (Python 3.13 slim) - Agent execution environment
4. **FastMCP Server** (Python 3.13 slim) - MCP protocol tool server
5. **Playwright** (`mcr.microsoft.com/playwright:v1.56.1-noble`) - Browser environment
6. **Ollama** (`ollama/ollama:latest`) - LLM inference engine

**Why**: Containerization ensures reproducibility, isolation, and simplified deployment across environments.

### TR-01A: Multistage Dockerfiles (Dev & Prod)

All application services (`frontend`, `backend`, `langchain`, `fastmcp`) use a three-stage Dockerfile:

1. `base`: runtime + system packages, non-root user.
2. `dev`: adds test & debug dependencies (pytest/coverage, watchfiles, debugpy or vite/vitest/playwright), hot reload entrypoint, debug ports.
3. `prod`: production dependencies only, source copied, minimal CMD, healthcheck support.

Dev stage specifics:

- Python hot reload via `watchfiles` or `uvicorn --reload`.
- Frontend hot reload via Vite HMR (`npm run dev -- --host 0.0.0.0`).
- Debug ports exposed (backend 5671, langchain 5672, fastmcp 5673, frontend 9229 optional).

Prod stage specifics:

- No dev/test tooling.
- Non-root execution mandatory.
- Image minimized (clean build layers, no cache).

### TR-01B: Compose Layering

Two compose files layer configurations:

- `docker/docker-compose.yml` (baseline prod semantics)
- `docker/docker-compose.dev.yml` (overlay selecting `target: dev`, mounting source/tests, overriding commands, exposing debug ports)

Dev stack launch:

```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d --build
```

### TR-01C: Volume Mount Strategy

| Mode | Source Code | Tests      | Dependencies   | Data (artifacts/models) |
| ---- | ----------- | ---------- | -------------- | ----------------------- |
| Dev  | Mounted rw  | Mounted rw | In image (dev) | Named volumes           |
| Prod | Copied ro   | Copied ro  | Prod only      | Named volumes           |

### TR-01D: Flexible Test Execution

Builds and tests may run either (a) inside the devcontainer shell (Python 3.13 & Node 24 preinstalled) or (b) inside service dev-stage containers via `docker compose exec`. Both paths must yield equivalent results (same coverage, pass/fail). Host itself still requires only Docker & VS Code.

### TR-01E: Async & Streaming Interfaces

Public I/O or long-running operations are async (Python) or promise-based (TypeScript). Progress, tool calls, and partial results are streamed over WebSockets.

**Notes**:

- Default LLM model: `qwen3:8b` (CPU-only to start; GPU acceleration is a future enhancement)
- Windows development is supported via Docker Desktop with WSL2 backend

### Environment Configuration

**Requirement**: A single `.env` file at the repository root must define configuration used by all services (Docker Compose and application processes).

**Details**:

- Shared `.env` keys include service endpoints, rate limits, and logging options
- Each service reads from environment variables; no hardcoded configuration
- Example keys: `LOG_LEVEL`, `LOG_TARGET`, `LOG_FILE`, `API_PORT`, `VITE_API_URL`, `OLLAMA_HOST`, etc.

### TR-02: Browser Automation Tools (MCP Protocol)

**Requirement**: FastMCP must expose atomic, reliable browser automation tools via MCP protocol.

**Core Tool Categories**:

**Navigation Tools**:

- `navigate_to(url, wait_until="networkidle")` → NavigationResult
- `go_back()`, `go_forward()`, `reload()` → NavigationResult

**Interaction Tools**:

- `click(selector, button="left")` → ActionResult
- `type_text(selector, text, delay_ms=0)` → ActionResult
- `fill(selector, value)` → ActionResult
- `press_key(key)` → ActionResult

**Content Extraction Tools**:

- `get_page_content()` → PageContent (HTML, text, metadata)
- `get_element_text(selector)` → str
- `extract_structured_data(schema)` → dict
- `get_page_structure()` → StructuredDOM

**Visual Tools**:

- `take_screenshot(full_page=False)` → base64 image
- `highlight_element(selector)` → base64 image

**Session Management Tools**:

- `create_browser_context(options)` → context_id
- `close_browser_context(context_id)` → bool
- `get_cookies()`, `set_cookies(cookies)` → List[Cookie]

**Tool Design Principles**:

1. **Atomic Operations**: Each tool does one thing well
2. **Structured Errors**: Return error objects, not exceptions
3. **Observability**: Return enough context for LLM understanding
4. **Idempotency**: Safe to retry on failure where possible
5. **Explicit Timeouts**: All operations have reasonable timeouts
6. **State Transparency**: Clear indication of browser state after each action

**Why**: Clean tool definitions enable reliable LLM-driven automation with clear success/failure indicators.

### TR-03: LangChain Agent Configuration

**Requirement**: LangChain must orchestrate the agentic research workflow with memory, callbacks, and error recovery.

**Agent Configuration**:

- **Pattern**: ReAct (Reasoning + Acting) for step-by-step problem solving
- **Memory**: ConversationBufferMemory for context retention across tool calls
- **Max Iterations**: 15 (prevents infinite loops)
- **Tools**: MCP browser tools wrapped as LangChain StructuredTools
- **Callbacks**: Custom WebSocket callback handler for real-time streaming to frontend

**Prompt Engineering Requirements**:

- System prompt defining browser interaction best practices
- Few-shot examples of successful research workflows
- Error recovery guidelines
- State awareness instructions (include current page context)
- Goal decomposition strategy (break complex tasks into steps)
- Default search engine: DuckDuckGo. Design for pluggable search providers in future phases.

**Error Handling**:

- Automatic retry with exponential backoff on transient failures
- Graceful degradation to partial results when goals partially achieved
- Early stopping when goals fully achieved or hard limits reached
- Structured error reporting with recovery suggestions

**Why**: LangChain provides proven agent patterns, memory management, and callback infrastructure essential for complex multi-step workflows. This is not optional—it's core to the agentic capability.

### TR-04: Deidentified Browsing

**Requirement**: All browser sessions must be privacy-preserving and deidentified.

**Implementation Requirements**:

- Fresh Playwright browser context per task (no storage persistence)
- Randomized user agents from pool of recent browser versions (10+ variants)
- No cookies, local storage, or session storage carried over between tasks
- Tracking prevention enabled (block third-party cookies, fingerprinting scripts)
- No geolocation, notifications, or other permission requests
- PII redaction in logs (mask URLs with sensitive params, form inputs, auth tokens)
- Optional egress proxy support for additional anonymity
- Browser engine: Start with Chromium (Edge-compatible) by default; plan support for Chrome, Firefox, and WebKit in future phases.

**Why**: Protects user privacy and prevents tracking/personalization of automated browsing.

### TR-05: Rate Limiting and Bot Protection

**Requirement**: System must respect web resource constraints and avoid bot detection.

**Rate Limiting Implementation**:

- Max 5 HTTP requests per 90-second sliding window (per domain)
- Randomized delay between requests: 10-20 seconds (uniform distribution)
- Per-domain rate tracking (separate buckets per domain)
- 429 (Too Many Requests) handling:
  - Parse Retry-After header if present
  - Apply exponential backoff: 2x delay each retry (max 5 minutes)
  - Surface warning to user if repeated 429s occur
  - Fail gracefully after 3 consecutive 429s from same domain

**Bot Protection Measures**:

- Rotate user agents between requests (pool of 10+ recent versions)
- Randomize viewport dimensions (1280x720 to 1920x1080)
- Human-like scrolling (smooth scroll to elements before interaction, variable speed)
- Random mouse movements during page load (simulated cursor path)
- Variable typing speeds (50-150ms per character, randomized)
- Random pauses between actions (500-2000ms)

**Why**: Ensures ethical resource usage and maintains system reliability against anti-bot measures.

### TR-06: Domain Filtering

**Requirement**: Configurable allow/deny lists for domain access control, persisted to configuration files.

**Implementation Requirements**:

- Persistent configuration files:
  - `config/allowed-domains.txt` (one domain per line, optional)
  - `config/disallowed-domains.txt` (one domain per line)
- Pre-navigation checks:
  - Block if domain in deny list
  - If allow list exists and not empty, block if domain not in allow list
- Support for wildcards: `*.example.com`, `*.google.*`
- Runtime updates: changes written back to config files immediately
- robots.txt respect (optional, enabled by default): parse robots.txt and respect Disallow directives
- User agent declaration: Identify as automated research tool in robots.txt requests

**Why**: Enables organizational policies, compliance requirements, and protection against malicious sites.

### TR-07: Real-time Streaming

**Requirement**: Backend must stream agent thoughts and actions to frontend via WebSocket in real-time.

**WebSocket Event Types**:

```typescript
{
  type: "agent:thinking",    // LLM is reasoning about next step
  content: string            // Agent's thought process
}
{
  type: "agent:tool_call",   // Tool about to be executed
  tool: string,              // Tool name
  args: object               // Tool arguments
}
{
  type: "agent:tool_result", // Tool execution completed
  tool: string,              // Tool name
  result: object,            // Tool result
  status: "success" | "error"
}
{
  type: "agent:screenshot",  // New screenshot available
  image: string,             // base64 image data
  url: string                // Current page URL
}
{
  type: "agent:complete",    // Task finished
  answer: string,            // Final answer
  citations: Array<Citation>, // Source URLs with snippets
  confidence: number         // 0-1 confidence score
}
{
  type: "agent:error",       // Error occurred
  error: string,             // Error message
  recoverable: boolean       // Can task continue?
}
```

**Implementation**:

- LangChain custom callback handler captures agent events
- FastAPI WebSocket endpoint broadcasts to connected clients (one WebSocket per task)
- Client-side reconnection logic with exponential backoff (max 5 retries)
- Message buffering on disconnect (keep last 50 messages)

**Why**: Provides transparency and enables users to monitor progress and intervene if needed.

### TR-08: Task Management

**Requirement**: Backend must manage concurrent research tasks with queue, lifecycle control, and artifact persistence.

**Task Lifecycle States**:

1. **Queued**: Task created, waiting for execution slot
2. **Running**: Agent actively researching
3. **Completed**: Task finished successfully with answer
4. **Failed**: Task encountered unrecoverable error
5. **Cancelled**: User requested cancellation
6. **Timeout**: Task exceeded time budget

**Task Queue**:

- Configurable concurrency limit (default: 5 simultaneous tasks, max: 10)
- Fair scheduling (FIFO with optional priority levels: low, normal, high)
- Timeout enforcement (default: 120 seconds per task, configurable up to 600 seconds)
- Resource limits per task:
  - Max pages: 20 (configurable, 0 = unlimited)
  - Max depth: 3 (configurable, 0 = unlimited)
  - Max concurrent browser contexts: 1 per task

**Task Artifacts**:

- Full LangChain conversation history (messages, tool calls, results)
- Navigation timeline (URLs, timestamps, durations, HTTP status codes)
- Screenshots at key points (start, end, errors, user-requested)
- Final answer with citations and confidence score
- Error logs with stack traces and recovery attempts
- Metadata: start time, end time, duration, token count, page count

**Persistence (MVP)**: Filesystem-based artifact store without a database. Persist JSON (conversation, timeline, metadata) and images under a task-specific directory, with retention configured via `.env`.

**Persistence (Future)**: Pluggable database (PostgreSQL or SQLite) for querying, indexing, and retention policies. No functionality loss in MVP—database adds convenience and performance.

**Why**: Enables multi-user support, resource management, comprehensive debugging, and audit compliance.

### TR-09: Security

**Requirement**: System must prevent unauthorized access and limit exposure to malicious content.

**Security Measures**:

- **Authentication (Future)**: JWT-based API authentication (not required for MVP). For development, allow unauthenticated local access.
- **CORS (MVP → Future)**: Development-friendly CORS for local frontend; tighten to explicit allowlist and credentials policy in production phase.
- **Rate Limiting**: Per API key or IP address (100 requests/hour for unauthenticated, 1000/hour for authenticated)
- **Input Validation**:
  - URL format validation (valid schemes: http, https only)
  - SQL injection prevention (parameterized queries)
  - Maximum input lengths (question: 1000 chars, URL: 2048 chars)
- **Output Sanitization**: XSS prevention in scraped content (strip scripts, sanitize HTML)
- **Container Security**:
  - Non-root users in all containers
  - Read-only filesystems where possible
  - Resource limits (CPU, memory) per container
  - Network isolation (Playwright container has no outbound internet by default, only via proxy)
- **Sandboxed JavaScript**: Custom JS evaluation runs in isolated context with strict timeout and no network access

**Why**: Protects system integrity, prevents abuse, and limits exposure to malicious websites.

### TR-10: Observability

**Requirement**: System must provide comprehensive logging, monitoring, and debugging capabilities.

**Logging Requirements**:

- **Format**: Structured JSON logs with fields: timestamp, level, component, trace_id, message, metadata
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Components**: frontend, backend-api, langchain, fastmcp, playwright, ollama
- **PII Redaction**: Automatic redaction of sensitive data (auth tokens, email addresses, phone numbers) in logs
- **Trace IDs**: Unique ID per task, propagated across all components for correlation
- **Implementation**:
  - JavaScript/TypeScript: Pino logger with Pretty transport in development for readable console output; file logging via rotating file if `LOG_TARGET` includes `file`
  - Python: Loguru with colorized console output in development; file sink when `LOG_TARGET` includes `file`
  - Configuration via `.env`: `LOG_LEVEL` (debug|info|warn|error), `LOG_TARGET` (console|file|both), `LOG_FILE` (path)

**Monitoring Requirements**:

- **Health Checks**: HTTP endpoints for all containers (GET /health returns 200 OK)
- **Metrics** (Prometheus-compatible):
  - Request count (by endpoint, status code)
  - Request latency (p50, p95, p99)
  - Task success/failure rate
  - Tool call counts and latency
  - LLM token usage
  - Browser resource usage (CPU, memory)
- **Alerting**: Configurable alerts for high error rates, slow responses, resource exhaustion

**Debugging Capabilities**:

- **Tool Call Replay**: Ability to replay sequence of tool calls for debugging
- **Log Aggregation**: Centralized logging with search and filtering (optional ELK stack integration)

**Future Enhancements**:

- **HAR Export**: HTTP Archive (HAR) for network traces
- **Video Recording**: Browser session recording
- **DOM Snapshots**: Full page HTML saved on errors

These may be enabled in later phases due to performance and storage costs.

**Why**: Essential for troubleshooting, performance optimization, compliance auditing, and production operations.

## Non-Functional Requirements

### NFR-01: Performance

- **Target**: 95% of simple queries (single search, 1-3 pages) answered within 60 seconds
- **Target**: Average tool execution time < 5 seconds
- **Target**: Container startup < 30 seconds
- **Target**: WebSocket event latency < 200ms

### NFR-02: Reliability

- **Target**: 95% success rate for basic navigation and interaction under normal network conditions
- **Target**: Graceful degradation on network failures (partial results acceptable)
- **Target**: Automatic recovery from transient errors (max 3 retries with exponential backoff)
- **Target**: Zero data loss (all task artifacts persisted before completion)

### NFR-03: Scalability

- **Target**: Support 5+ concurrent research tasks per deployment instance
- **Target**: Handle 100+ requests per hour per instance
- **Target**: Horizontal scaling capability (future: stateless architecture with shared database)

### NFR-04: Usability

- **Target**: Single-click task submission with sensible defaults (no required configuration)
- **Target**: Real-time progress visible within 2 seconds of submission
- **Target**: Mobile-responsive UI for monitoring (desktop-optimized for task creation)
- **Target**: Keyboard navigation support for accessibility

### NFR-05: Maintainability

- **Target**: Unit test coverage >80% (statement, branch, function) per project
- **Target**: Integration tests cover major cross-module flows (no fixed % — qualitative assessment)
- **Target**: E2E tests exercise primary user workflows (UC-01..UC-04)
- **Target**: Clear separation of concerns (layered architecture with defined interfaces)
- **Target**: Self-documenting code (type hints, docstrings, inline comments for complex logic)
- **Target**: Automated deployment via Docker Compose (single command: `docker-compose up`)
- **Target**: Hot reload functioning across all dev targets

### NFR-07: Development Workflow

- Dev overlay compose provides hot reload & debug ports.
- Zero manual container restarts needed after code changes.
- Consistent multistage pattern across services.

### NFR-08: Test Execution Environment

- Tests runnable from devcontainer shell (preferred for speed) or dev stage containers (parity/isolation).
- Coverage artifacts stored under `<project>/coverage` regardless of execution path.
- Documentation provides both devcontainer and container exec command examples for unit/integration/e2e.

### NFR-09: Image Hygiene & Security

- Production images exclude dev/test tooling.
- Non-root user enforced and minimal file permissions.
- Regular vulnerability scanning planned (future automation).

### NFR-06: Compliance

- **Target**: GDPR-compliant data handling (no PII without explicit consent, right to deletion)
- **Target**: Complete audit trail for all automated actions (who, what, when, why)
- **Target**: Configurable data retention and automated deletion (default: 30 days)
- **Target**: robots.txt compliance enabled by default

## Success Criteria

### Functional Success

✅ User can ask a question and receive an accurate, cited answer  
✅ System successfully navigates multi-page workflows (search → read → follow links)  
✅ Real-time progress visible in UI with WebSocket streaming  
✅ Error handling provides actionable feedback and partial results when possible  
✅ Task history persists and can be reviewed, exported, and deleted

### Non-Functional Success

✅ 95% success rate for common queries under normal network conditions  
✅ Answers returned within 60 seconds for 95% of simple queries  
✅ System respects rate limits and avoids bot detection (< 1% CAPTCHA rate)  
✅ No privacy leaks (zero PII or tracking data in logs or artifacts)  
✅ Comprehensive logging enables debugging of 95% of issues without code changes

### Business Success

✅ Reduces manual research time by 80%+ for supported query types  
✅ Users trust answers due to clear source attribution and confidence scores  
✅ System operates within ethical and legal boundaries (robots.txt, rate limits, no paywall circumvention)  
✅ Deployment and maintenance costs remain predictable (< 10 hours/month operational overhead)

---

**Document Version**: 2.1  
**Last Updated**: November 14, 2025  
**Status**: Updated (flexible devcontainer or container test execution)
