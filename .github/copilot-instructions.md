# Web Reader - AI Assistant Instructions (Concise)

This guide is for AI coding assistants (like GitHub Copilot) working in this repo. It prioritizes the rules and patterns you must follow; deep details live in the linked docs below.

## Project Overview

Frontend (TanStack Start, TypeScript) → Backend API (FastAPI) → LangChain Orchestrator (required) → FastMCP (MCP tools) → Playwright Browser. LLM via Ollama (function-calling models). All services run via Docker Compose with a shared root `.env`.

## Critical Rules

- LangChain required: Use LangChain for orchestration, memory, callbacks, and error recovery. Do not bypass it.
- MCP separation: Reasoning (LangChain) is separate from execution (FastMCP/Playwright).
- Deidentified browsing: Fresh browser context per task; no cookies/storage/history; randomized user agents.
- Rate limiting: Max 5 requests/90s per domain with 10–20s randomized delays; handle 429 with exponential backoff.
- Domain filtering: Enforce allow/deny lists from `config/` before every navigation.
- Config hygiene: No hardcoded config; use the root `.env` and config files.

## Working Guidelines

- Async + streaming: Public I/O is `async`; long steps stream events (thinking, tool_call, tool_result, screenshot, complete, error).
- Non-blocking callbacks: Use `asyncio.create_task(...)` for WebSocket sends to avoid blocking.
- Structured results: Return `{status: "success", data, metadata?}` or `{status: "error", error, recoverable?}` from tools instead of raising unhandled exceptions.
- Logging: Use structured logs; redact sensitive data (tokens, emails, query params with secrets).
- Respect hot reload: Dev mode should live-reload; avoid slow module-level init.
- Do not modify: Leave `notes.md` untouched unless explicitly asked.

## Essential Environment Variables

Use `.env.example` as the source of truth. Common keys you’ll reference most:

- Frontend: `VITE_API_URL`, `VITE_WS_URL`
- Backend: `API_HOST`, `API_PORT`, `CORS_ORIGINS`
- LangChain/LLM: `OLLAMA_HOST`, `OLLAMA_PORT`, `OLLAMA_MODEL`
- MCP/Browser: `FASTMCP_HOST`, `FASTMCP_PORT`, `PLAYWRIGHT_HOST`, `PLAYWRIGHT_PORT`, `BROWSER_TYPE`
- Behavior: `ENABLE_RATE_LIMITING`, `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW`, `REQUEST_DELAY_MIN`, `REQUEST_DELAY_MAX`, `MAX_BROWSER_CONTEXTS`, `DEFAULT_TIMEOUT`
- Logging: `LOG_LEVEL`, `LOG_TARGET`, `LOG_FILE`

## Success Criteria (Short)

- Functional: Accurate, cited answers; multi-page workflows; live progress via WebSocket; actionable error feedback; task history persists.
- Non-functional: 95% success on common queries; answers ≤60s for simple queries; respects rate limits; no privacy leaks; comprehensive logging.
- Performance targets: Tool exec <5s avg; container startup <30s; WS latency <200ms; memory <2GB per browser context.

## Common Pitfalls (Condensed)

- Skipping LangChain: Always orchestrate via LangChain.
- No rate/domain checks: Enforce limits and filters before navigation.
- Blocking callbacks: Never await WebSocket sends inline; schedule tasks.
- Throwing raw exceptions: Return structured error objects instead.
- Hardcoded config: Read from `.env` and `config/` files.
- Persistent browser state: New context per task; never reuse session storage.

## More Information

- Implementation details, Docker strategy, patterns: `.github/implementation.md`
- Requirements and architecture (WHAT/WHY): `.github/requirements.md`
- Use cases: `.github/use-case.md`
- Project plan: `.github/project-plan.md`
- Testing commands and patterns: `README.TEST.md`
- Dev vs Prod and local debugging: `README.DEBUG.md`, `README.VSCODE-TESTING.md`
- FastMCP tool design, rate limiting, domain filtering: `fastmcp/README.md`
- LangChain agent patterns and streaming callbacks: `langchain/README.md`
- Backend API and WebSocket events: `backend/README.md`
- Frontend HMR and structure: `frontend/README.md`

## Technology Links

- LangChain: https://docs.langchain.com/oss/python/langchain/overview
- FastMCP: https://gofastmcp.com/getting-started/welcome
- FastAPI: https://fastapi.tiangolo.com

- Tanstack Start: https://tanstack.com/start/latest/docs/framework/react/overview
- Tanstack Router: https://tanstack.com/router/latest/docs/framework/react/overview
- Tanstack Query: https://tanstack.com/query/latest/docs/framework/react/overview
- Tanstack Devtools: https://tanstack.com/devtools/latest/docs
- React: https://react.dev/reference/react

- Ollama: https://docs.ollama.com/
- Playwright: https://playwright.dev/docs/intro

- Vite: https://vite.dev/guide/
- Vitest: https://vitest.dev/guide/
- Chrome DevTools MCP Server: https://github.com/ChromeDevTools/chrome-devtools-mcp
