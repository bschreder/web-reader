# Refactor Baseline Contracts (Phase 0)

Date: 2026-05-26
Status: Approved for implementation

## Canonical Port Map

| Service          | Container Port | Host Port       | Debug Port |
| ---------------- | -------------- | --------------- | ---------- |
| frontend         | 3000           | 3000            | 9229       |
| backend          | 8000           | 8000            | 5671       |
| langchain        | 8001           | 8001 (optional) | 5672       |
| fastmcp (mcp)    | 3100           | 3100            | 5673       |
| fastmcp (health) | 3101           | 3101            | n/a        |
| playwright ws    | 3002           | 3002            | n/a        |
| ollama http      | 11434          | 11434           | n/a        |

## Canonical URL + Env Contract

All runtime URL configuration must originate from root `.env`.

| Key                    | Value Contract                        | Example                 |
| ---------------------- | ------------------------------------- | ----------------------- |
| FRONTEND_PUBLIC_URL    | Browser-access URL for frontend       | http://localhost:3000   |
| BACKEND_PUBLIC_URL     | Browser-access URL for backend API    | http://localhost:8000   |
| BACKEND_INTERNAL_URL   | In-compose backend URL                | http://backend:8000     |
| LANGCHAIN_INTERNAL_URL | In-compose langchain URL              | http://langchain:8001   |
| FASTMCP_INTERNAL_URL   | In-compose FastMCP MCP endpoint URL   | http://fastmcp:3100/mcp |
| PLAYWRIGHT_WS_URL      | In-compose Playwright websocket URL   | ws://playwright:3002    |
| OLLAMA_BASE_URL        | In-compose Ollama base URL            | http://ollama:11434     |
| VITE_API_URL           | Frontend browser API base URL         | /api                    |
| VITE_WS_URL            | Frontend browser WS fallback base URL | ws://localhost:3000     |
| INTERNAL_API_URL       | Frontend SSR/server-functions API URL | http://backend:8000     |

## Approved Command Matrix

Canonical entrypoint: `wr` wrappers under `infra/scripts/`.

| Action             | Command                                 |
| ------------------ | --------------------------------------- |
| full stack (dev)   | ./infra/scripts/wr.ps1 up               |
| full stack (debug) | ./infra/scripts/wr.ps1 debug up         |
| infra only         | ./infra/scripts/wr.ps1 up --infra       |
| app only           | ./infra/scripts/wr.ps1 up --app         |
| stop all           | ./infra/scripts/wr.ps1 down             |
| logs               | ./infra/scripts/wr.ps1 logs [service]   |
| lint               | ./infra/scripts/wr.ps1 lint             |
| unit tests         | ./infra/scripts/wr.ps1 test unit        |
| integration tests  | ./infra/scripts/wr.ps1 test integration |
| e2e tests          | ./infra/scripts/wr.ps1 test e2e         |
| full validation    | ./infra/scripts/wr.ps1 test all         |

## Freeze Scope

During refactor implementation, avoid adding new startup scripts and avoid introducing new compose entrypoints outside `infra/compose/`.

## Acceptance Criteria for Phase 0

- Port map is explicit and unambiguous.
- URL contract has no localhost fallback requirement in code.
- One command surface is identified for docs, tasks, and CI.
