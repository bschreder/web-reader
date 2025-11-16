# Web Reader - AI Assistant Instructions

This document provides context and guidelines for AI coding assistants (like GitHub Copilot) working on the Web Reader project.

## Technology Stack Summary

### Frontend Layer

- **Framework**: TanStack Start (React-based SPA/SSR)
- **Routing**: TanStack Router (file-based)
- **Data Fetching**: TanStack Query
- **Real-time**: WebSocket client
- **Styling**: Tailwind CSS / shadcn/ui (recommended)
- **Type Safety**: TypeScript
- **Container**: Node.js 24 alpine

### Backend Layer

- **API Framework**: FastAPI (Python)
- **WebSocket**: FastAPI WebSockets or Socket.io
- **Validation**: Pydantic (Python) or Zod (TypeScript)
- **Task Queue**: Python asyncio or BullMQ (Node.js)
- **Container**: Python 3.13 slim or Node.js 24

### Orchestration Layer

- **Framework**: LangChain (Python) - **REQUIRED, NOT OPTIONAL**
- **Agent Pattern**: ReAct or Plan-and-Execute
- **Memory**: ConversationBufferMemory + VectorStoreMemory (future)
- **Callbacks**: Custom WebSocket callback handlers
- **Container**: Python 3.13 slim
- **Why**: Provides agent patterns, memory, callbacks, and error recovery infrastructure

### Tool Server Layer

- **Framework**: FastMCP (Python)
- **Protocol**: Model Context Protocol (MCP)
- **Browser Control**: Playwright Python
- **Container**: Python 3.13 slim

### Infrastructure Layer

- **LLM**: Ollama (llama3.2, qwen2.5, mistral)
- **Container**: `ollama/ollama:latest`
- **Models**: Function-calling capable models only
- **Browser**: Microsoft Playwright (Docker)
- **Container**: `mcr.microsoft.com/playwright:v1.56.1-noble`
- **Vector DB**: ChromaDB or Qdrant (future, optional)
- **Orchestration**: Docker Compose

### Supporting Technologies

- **Embeddings**: sentence-transformers (for future Vector DB)
- **Monitoring**: LangSmith (future, optional)
- **Logging**: Structured JSON logs
- **Testing**: pytest (Python), Playwright Test (E2E)

## Best Practices

### General Guidelines

- Use meaningful, descriptive names for variables, functions, and classes that minimize the need for comments.
- Write simple, clear code; avoid unnecessary complexity.
- Follow the DRY principle (Don't Repeat Yourself) to minimize code duplication.
- Write modular code with single-responsibility functions and classes.
- Use efficient data structures and algorithms; avoid unnecessary computations
- Use comments to explain "why" not "what"; avoid obvious comments
- Update comments when code changes; remove outdated comments
- Use try-except blocks for graceful exception handling. Handle errors explicitly.
- Avoid global variables to reduce side effects.
- Write unit tests for all new features and bug fixes; aim for high coverage but prioritize critical paths.
- Write integration tests that mock external dependencies.
- Write end-to-end tests to simulate real user scenarios.
- Document new scripts, flags, and environment variables in the README
- Never hardcode secrets; use environment variables and mask sensitive logs

### Dev vs Prod Containers
- All services provide multistage Dockerfiles (`base`, `dev`, `prod`).
- Use `docker/docker-compose.yml` + `docker/docker-compose.dev.yml` together for development.
- Dev stage: hot reload (watchfiles/uvicorn reload for Python, Vite HMR for frontend), debug ports (backend 5671, langchain 5672, fastmcp 5673, optional frontend 9229).
- Prod stage: minimal runtime (no dev/test tooling), non-root execution, health checks enabled.

### Devcontainer & Container Tooling
- Primary workflow: run builds and tests directly inside the VS Code devcontainer (Python 3.13 & Node 24 available).
- Optional: use `docker compose exec` for parity, isolation, or reproducing CI conditions.
- Ensure equivalent results (same failures/coverage) across devcontainer shell and container exec.
- Coverage thresholds: >80% statement, branch, function per project.
- Test directories: `tests/unit`, `tests/integration`, `tests/e2e` (frontend additionally `tests/browser`).

### Async & Streaming Interfaces
- Python service public I/O functions should be `async def`.
- Long-running operations stream incremental events over WebSockets (thinking, tool_call, tool_result, screenshot, complete, error).
- Avoid blocking calls (`time.sleep`)—use `await asyncio.sleep`.
- Tool implementations return structured dicts (`status`, `data` or `error`) instead of raising unhandled exceptions.

### Hot Reload Expectations
- Editing code in dev mode triggers automatic reload (no manual container restart).
- If reload fails, check watcher command & mounted volume paths.
- Frontend HMR must work over network (configure `--host 0.0.0.0`).

### Coverage & Testing Commands (Examples)
Devcontainer (preferred):
```bash
# FastMCP unit
cd fastmcp && pytest tests/unit --cov=src --cov-branch
# Backend integration
cd backend && pytest tests/integration -v
# LangChain e2e
cd langchain && pytest tests/e2e -v
# Frontend unit
cd frontend && npm run test:unit
```
Optional container exec:
```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec fastmcp pytest tests/unit --cov=src --cov-branch
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec backend pytest tests/integration -v
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec langchain pytest tests/e2e -v
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec frontend npm run test:unit
```

### Adding New Features
- Update relevant Dockerfile if new dependencies added (both dev & prod).
- Ensure new I/O or network functions are async and, if multi-step, emit streaming events.
- Add unit tests first; integration tests if cross-service impact; extend E2E flows if user-visible.
- Maintain coverage thresholds—refactor rather than exclude lines.

### Typescript, Node.js, Frontend

- Strict TypeScript: enable `strict`, `noUncheckedIndexedAccess`, `esModuleInterop` as needed
- Use ESM `import`/`export` (type-only imports where possible).
- Use React functional components, hooks, and best practices.
- Prefer defined types over `any`; avoid `unknown` unless necessary. If a value is truly dynamic, narrow it with type guards instead of using `any`.
- Use `async`/`await` for async code; avoid callbacks and `.then()`; support request cancellation.
- Respect robots.txt, http 429 status code, throttle and randomize delays, and stream data when possible
- Use Pino for structured logging; log to both file and console based on environment variables.
- Use path aliases (e.g., `~/*`: ["./src/*"]) for all imports not in current directory or subdirectories for cleaner imports.
- Use JSDoc for all functions, classes, and complex logic. Include bloc k and inline tags and type parameters, for example:
  - Block tags: `@param`, `@returns`, `@template`, `@throws`, `@example`, `@remarks`, `@see`
  - Inline tags: `{@link Symbol}` `{@inheritDoc}` `{@label}`
  - Type parameters: `@template T`, `@template K, V`
- Test component following Vitest best practices ('https://vitest.dev/guide/browser/component-testing')

### Python, FastAPI, Backend

- Follow PEP 8 for code formatting.
- Document functions and classes with docstrings.
- Prefer list comprehensions over traditional loops when appropriate.
- Use type hints for clarity and type checking.
- Prefer Pydantic models for input validation.
- Use pytest for testing but prefer unittest.mock for mocking.

### File Watching (Python Services)
- Use `watchfiles` to restart application on source changes.
- Keep startup fast (<2s) to support rapid iteration.
- Avoid heavy initialization in module top-level; defer to async startup hooks.

### Frontend Hot Reload
- Vite dev server must bind to `0.0.0.0` for container access.
- Keep dependencies lean; move build-only packages to dev stage.

### Failure Handling & Resilience
- Retry transient network/tool errors with exponential backoff (LangChain agent handles parse errors automatically when configured).
- Emit error events to WebSocket; never silently fail.
- Provide `recoverable` flag in structured errors to guide agent retries.

### Do Not Modify
- `notes.md` is a developer scratch pad; leave untouched unless explicitly requested.

### Summary
These instructions emphasize flexible (devcontainer or container) workflows, async streaming interfaces, hot reload, and strict test coverage to maintain reliability and velocity.

## Project Architecture

### System Layers (Top to Bottom)

```
User → Frontend (TanStack Start)
      ↓
    Backend API (FastAPI)
      ↓
      LangChain Orchestrator (REQUIRED)
      ↓ (MCP Protocol)      ↓ (HTTP API)
      FastMCP Server      Ollama LLM
      ↓ (Playwright API)
      Playwright Browser
```

### Key Architectural Decisions

1. **LangChain is REQUIRED**: Not optional. It's the orchestration layer that provides:

   - ReAct agent pattern for step-by-step reasoning
   - Conversation memory for context retention
   - Callback system for real-time streaming
   - Error recovery and retry logic
   - Tool wrapper infrastructure

2. **MCP Protocol**: FastMCP exposes browser automation tools via Model Context Protocol

   - LangChain tools wrap MCP tools
   - Clean separation: reasoning (LangChain) vs. execution (FastMCP/Playwright)

3. **Deidentified Browsing**: Every task gets a fresh browser context

   - No cookies, storage, or history
   - Randomized user agents
   - Tracking prevention enabled

4. **Rate Limiting**: Hard requirement for ethical scraping

   - Max 5 requests per 90 seconds per domain
   - Randomized 10-20 second delays
   - 429 handling with exponential backoff

5. **Domain Filtering**: Allow/deny lists in config files
   - `config/allowed-domains.txt`
   - `config/disallowed-domains.txt`
   - Wildcard support: `*.example.com`

## Coding Guidelines

Configuration: Use a single `.env` at the repository root, shared by all services (Compose `env_file` and app processes). No hardcoded config.

### Python Code Style

```python
# Use type hints everywhere
async def execute_task(
    question: str,
    seed_url: Optional[str] = None,
    max_depth: int = 3
) -> Dict[str, Any]:
    """Execute research task with LangChain agent."""
    pass

# Use structured logging
logger.info("Task started", extra={
    "task_id": task_id,
    "question": question[:50]  # Truncate for logs
})

# Handle errors gracefully with structured responses
try:
    result = await agent.ainvoke(input)
    return {"status": "success", "data": result}
except Exception as e:
    logger.error(f"Task failed: {e}", exc_info=True)
    return {"status": "error", "error": str(e)}
```

### TypeScript Code Style

```typescript
// Use strict types
interface TaskCreate {
  question: string;
  seed_url?: string;
  max_depth?: number;
}

// Use async/await for all API calls
async function createTask(task: TaskCreate): Promise<Task> {
  const response = await fetch(`${API_URL}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

// Handle WebSocket lifecycle properly
useEffect(() => {
  const ws = connectTaskStream(taskId, handleEvent);
  return () => ws.close(); // Cleanup
}, [taskId]);
```

### Logging Requirements

- JavaScript/TypeScript: Use Pino with Pretty transport in development; enable file output when `LOG_TARGET` includes `file`.
- Python: Use Loguru with colorized console output; add a rotating file sink when `LOG_TARGET` includes `file`.
- Control via `.env`: `LOG_LEVEL` (debug|info|warn|error), `LOG_TARGET` (console|file|both), `LOG_FILE` (path).

### LangChain Patterns

```python
# Always use StructuredTool for type safety
browser_tool = StructuredTool.from_function(
    func=lambda url: mcp.call_tool("navigate_to", {"url": url}),
    name="navigate_to",
    description="Navigate browser to URL. Use for search engines and web pages.",
    args_schema=NavigateToSchema  # Pydantic model
)

# Use callbacks for streaming
callbacks = [WebSocketCallbackHandler(websocket)]
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=callbacks,
    verbose=True
)

# Implement proper error recovery
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,  # Automatic retry on parsing errors
    max_iterations=15,
    early_stopping_method="generate"
)
```

### FastMCP Tool Patterns

```python
@mcp.tool()
async def navigate_to(url: str, wait_until: str = "networkidle") -> dict:
    """
    Navigate to URL and wait for page load.

    Args:
        url: Target URL (must be http or https)
        wait_until: Load event to wait for

    Returns:
        Dict with status, title, url, timing
    """
    # 1. Validate inputs
    if not url.startswith(('http://', 'https://')):
        return {"status": "error", "error": "Invalid URL scheme"}

    # 2. Check domain filters
    if not is_domain_allowed(url):
        return {"status": "error", "error": f"Domain blocked"}

    # 3. Enforce rate limiting
    await enforce_rate_limit(get_domain(url))

    # 4. Execute with error handling
    try:
        page = await get_current_page()
        response = await page.goto(url, wait_until=wait_until, timeout=30000)

        # 5. Handle HTTP errors
        if response.status >= 400:
            return {
                "status": "error",
                "http_status": response.status,
                "error": HTTP_STATUS_MESSAGES.get(response.status)
            }

        # 6. Return structured success response
        return {
            "status": "success",
            "title": await page.title(),
            "url": page.url,
            "http_status": response.status
        }
    except PlaywrightTimeoutError:
        return {"status": "error", "error": "Timeout (30s exceeded)"}
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        return {"status": "error", "error": str(e)}
```

## Common Patterns

### WebSocket Event Streaming

```python
# Backend: LangChain callback handler
class WebSocketCallbackHandler(BaseCallbackHandler):
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        asyncio.create_task(self.websocket.send_json({
            "type": "agent:tool_call",
            "tool": serialized.get("name"),
            "args": input_str,
            "timestamp": datetime.utcnow().isoformat()
        }))
```

```typescript
// Frontend: WebSocket event handler
const handleEvent = (event: AgentEvent) => {
  switch (event.type) {
    case "agent:thinking":
      setThoughts((prev) => [...prev, event.content]);
      break;
    case "agent:tool_call":
      setLogs((prev) => [...prev, `Calling ${event.tool}...`]);
      break;
    case "agent:screenshot":
      setScreenshot(event.image);
      break;
    case "agent:complete":
      setAnswer(event.answer);
      setCitations(event.citations);
      break;
  }
};
```

### Rate Limiting

```python
_rate_limits: dict[str, list[float]] = {}

async def enforce_rate_limit(domain: str):
    """Max 5 requests per 90 seconds, 10-20s delays."""
    now = time.time()

    # Clean old timestamps (>90s ago)
    if domain in _rate_limits:
        _rate_limits[domain] = [t for t in _rate_limits[domain] if now - t < 90]
    else:
        _rate_limits[domain] = []

    # Check if at limit
    if len(_rate_limits[domain]) >= 5:
        oldest = _rate_limits[domain][0]
        wait_time = 90 - (now - oldest)
        if wait_time > 0:
            await asyncio.sleep(wait_time)

    # Random delay between requests
    if _rate_limits[domain]:  # Not first request
        delay = random.uniform(10, 20)
        await asyncio.sleep(delay)

    _rate_limits[domain].append(time.time())
```

### Domain Filtering

```python
def is_domain_allowed(url: str) -> bool:
    """Check domain against allow/deny lists."""
    domain = urlparse(url).netloc.lower()

    # Check deny list
    for pattern in DISALLOWED_DOMAINS:
        if fnmatch.fnmatch(domain, pattern):
            return False

    # Check allow list (if exists and not empty)
    if ALLOWED_DOMAINS:
        for pattern in ALLOWED_DOMAINS:
            if fnmatch.fnmatch(domain, pattern):
                return True
        return False  # Not in allow list

    return True  # No allow list, not denied
```

## Testing Patterns

### Unit Tests

### Browser Component Tests (Vitest Browser Mode)

Use Vitest Browser Mode for interactive component behavior instead of react-testing-library where possible. This runs tests in a real browser iframe with native events.

Configuration excerpt (see `frontend/vitest.config.ts`):

```
projects: [
    {
        test: {
            name: 'unit',
            include: ['tests/unit/**/*.{test,spec}.ts', 'tests/unit/**/*.{test,spec}.tsx'],
            environment: 'node',
        },
    },
    {
        test: {
            name: 'browser',
            include: ['tests/browser/**/*.{test,spec}.tsx'],
            browser: {
                enabled: true,
                provider: preview(),
            },
        },
    },
]
```

Example browser test (no testing-library):

```tsx
import { expect, test } from "vitest";
import { page } from "vitest/browser";
import { render } from "vitest-browser-react";
import { TaskForm } from "~/components/TaskForm";

test("TaskForm submit enabled after valid input", async () => {
  render(<TaskForm onSubmit={() => Promise.resolve()} submitting={false} />);
  const submitBtn = page.getByRole("button", { name: /start research/i });
  await expect.element(submitBtn).toBeDisabled();
  const textarea = page.getByLabelText(/research question/i);
  await textarea.fill("What is quantum computing?");
  await expect.element(submitBtn).toBeEnabled();
});
```

Reference: Vitest Browser Mode Guide — https://vitest.dev/guide/browser/

```python
@pytest.mark.asyncio
async def test_rate_limiting():
    """Test 5 requests per 90 seconds enforcement."""
    domain = "example.com"

    # Should allow 5 requests
    for i in range(5):
        await enforce_rate_limit(domain)

    # 6th should wait
    start = time.time()
    await enforce_rate_limit(domain)
    assert time.time() - start >= 45  # Waited for window
```

### Integration Tests

```python
@pytest.mark.integration
async def test_navigate_to():
    """Test navigation with real Playwright."""
    result = await navigate_to("https://example.com")

    assert result["status"] == "success"
    assert result["title"]
    assert result["http_status"] == 200
```

### E2E Tests

```typescript
// Frontend E2E with Playwright
test("submit task and see results", async ({ page }) => {
  await page.goto("/");

  // Submit question
  await page.fill('[data-testid="question"]', "What is the capital of France?");
  await page.click('[data-testid="submit"]');

  // Wait for answer
  await page.waitForSelector('[data-testid="answer"]', { timeout: 120000 });

  const answer = await page.textContent('[data-testid="answer"]');
  expect(answer).toContain("Paris");
});
```

## Success Criteria Reference

When implementing features, ensure they meet these criteria:

### Functional Success

- ✅ User can ask a question and receive an accurate, cited answer
- ✅ System successfully navigates multi-page workflows
- ✅ Real-time progress visible in UI via WebSocket
- ✅ Error handling provides actionable feedback
- ✅ Task history persists and can be reviewed

### Non-Functional Success

- ✅ 95% success rate for common queries
- ✅ Answers within 60 seconds for 95% of simple queries
- ✅ System respects rate limits (5 requests/90s)
- ✅ No privacy leaks (PII, tracking data)
- ✅ Comprehensive logging for debugging

### Performance Targets

- Tool execution: < 5 seconds average
- Container startup: < 30 seconds
- WebSocket latency: < 200ms
- Memory: < 2GB per browser context

## References

### Official Documentation

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [LangChain Documentation](https://python.langchain.com/)
- [LangChain Agents Guide](https://python.langchain.com/docs/modules/agents/)
- [TanStack Start Documentation](https://tanstack.com/start)
- [Playwright Python Documentation](https://playwright.dev/python/)
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)

### Project Documentation

- **Requirements**: See `.github/requirements.md` for WHAT and WHY
- **Use Cases**: See `.github/use-case.md` for user scenarios
- **Implementation**: See `.github/implementation.md` for HOW with code examples
- **Project Plan**: See `.github/project-plan.md` for phased implementation plan

## Common Pitfalls to Avoid

### 1. ❌ Treating LangChain as Optional

**Wrong**: "We can skip LangChain and call MCP tools directly from the backend."
**Right**: LangChain is required for agent orchestration, memory, callbacks, and error recovery.

### 2. ❌ Ignoring Rate Limiting

**Wrong**: Implementing browser automation without rate limiting.
**Right**: Always enforce 5 requests/90s with 10-20s delays. Critical for avoiding bans.

### 3. ❌ Persistent Browser State

**Wrong**: Reusing browser contexts across tasks for "performance".
**Right**: Fresh context per task for privacy (BR-04). Performance gain not worth privacy risk.

### 4. ❌ Synchronous WebSocket Callbacks

**Wrong**: Blocking callback handlers waiting for WebSocket send.
**Right**: Use `asyncio.create_task()` for non-blocking WebSocket sends.

### 5. ❌ Missing Domain Filtering

**Wrong**: Navigating to any URL provided.
**Right**: Check domain against allow/deny lists before every navigation.

### 6. ❌ Exposing PII in Logs

**Wrong**: Logging full URLs with query params, user inputs.
**Right**: Redact sensitive data (auth tokens, email addresses, etc.) in logs.

### 7. ❌ No Error Handling in Tools

**Wrong**: Letting exceptions propagate to agent.
**Right**: Return structured error objects: `{"status": "error", "error": "...", "recoverable": bool}`

### 8. ❌ Infinite Agent Loops

**Wrong**: No max_iterations limit on agent.
**Right**: Set `max_iterations=15` with early stopping.

### 9. ❌ Blocking the Event Loop

**Wrong**: Using `time.sleep()` in async code.
**Right**: Use `await asyncio.sleep()` for async delays.

### 10. ❌ Hardcoded Configuration

**Wrong**: Hardcoding API URLs, timeouts, limits in code.
**Right**: Use environment variables and config files for all tunable parameters.

## Quick Reference: Environment Variables

```bash
# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Backend API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# LangChain
OLLAMA_HOST=ollama
OLLAMA_PORT=11434
OLLAMA_MODEL=qwen3:8b
FASTMCP_HOST=fastmcp
FASTMCP_PORT=3000

# Playwright
PLAYWRIGHT_HOST=playwright
PLAYWRIGHT_PORT=3002
BROWSER_TYPE=chromium

# Application
MAX_BROWSER_CONTEXTS=5
DEFAULT_TIMEOUT=30000
MAX_LINK_DEPTH=3
MAX_PAGES=20
TIME_BUDGET=120
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=90
REQUEST_DELAY_MIN=10
REQUEST_DELAY_MAX=20

# Logging (shared)
LOG_LEVEL=info
LOG_TARGET=console   # console|file|both
LOG_FILE=logs/app.log
```

## Quick Reference: Tool Response Format

All FastMCP tools should return consistent response formats:

### Success Response

```python
{
    "status": "success",
    "data": {...},  # Tool-specific data
    "metadata": {   # Optional metadata
        "duration": 1.5,
        "http_status": 200,
        "url": "https://example.com"
    }
}
```

### Error Response

```python
{
    "status": "error",
    "error": "Human-readable error message",
    "error_code": "TIMEOUT",  # Optional machine-readable code
    "recoverable": True,  # Can agent retry?
    "suggestion": "Try with shorter timeout"  # Optional recovery hint
}
```

---

**Document Version**: 1.1  
**Last Updated**: November 14, 2025  
**Purpose**: AI Assistant Context and Guidelines (flexible test execution)
