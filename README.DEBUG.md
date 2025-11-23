# Web Reader Debug Guide

This guide explains how to run and debug all services (frontend, backend API, LangChain orchestrator, FastMCP tool server, and external infra: Ollama + Playwright) using the debug-enabled root scripts.

## Overview

Services:

- Frontend (Vite + React) — port 3000, optional Node inspect port 9229 (commented by default)
- Backend API (FastAPI) — port 8000, debugpy 5671 when `-Debug`
- LangChain Orchestrator — internal port 8001, debugpy 5672 when `-Debug`
- FastMCP Tool Server — internal port 3000, debugpy 5673 when `-Debug`
- Ollama (LLM) — port 11434
- Playwright server — port 3002

Debug mode (`-Debug`) replaces container commands with `python -m debugpy --wait-for-client --listen 0.0.0.0:<port> server.py` for Python services.

## Prerequisites

- Docker and Docker Compose installed (Windows / macOS / Linux).
- VS Code + Python extension.
- (Optional) Dev Containers extension if developing inside a container.

## Production vs Debug Builds

The project supports two distinct build modes:

### Production Mode (Default)

- Optimized builds using multi-stage Dockerfiles
- Frontend: Built static assets served by Node SSR (target: `prod`)
- Backend: Minimal Python runtime with production dependencies (target: `prod`)
- No volume mounts, no debug ports, no hot reload
- Start with: `./start.ps1` or `./start.ps1 -Rebuild`

### Debug Mode

- Development builds with debugging and hot reload enabled (target: `dev`)
- Frontend: Vite dev server with HMR, optional Node inspect on port 9229
- Backend: uvicorn with `--reload`, debugpy on port 5671
- LangChain: watchfiles auto-restart, debugpy on port 5672
- FastMCP: watchfiles auto-restart, debugpy on port 5673
- Source code mounted as volumes for live editing
- Start with: `./start.ps1 -Debug` or `./start.ps1 -Debug -Rebuild`

## Starting in Debug Mode

````powershell
./start.ps1 -Debug

The script uses `docker-compose.override.yml` when `-Debug` is specified.

**Production build:**
```powershell
./start.ps1
# Or force rebuild
./start.ps1 -Rebuild
````

**Debug build:**

```powershell
./start.ps1 -Debug
# Or force rebuild
./start.ps1 -Debug -Rebuild
```

**Other options:**

- `-Attach` — keep logs attached in current terminal
- `-Services backend,langchain` — start only these services
- `-InfraOnly` — start only Ollama and Playwright
- `-Help` — show usage

## Attaching Debuggers

Create VS Code launch configurations in `.vscode/launch.json` like:
Start a specific subset (e.g., only backend and langchain):

```json
./start.ps1 -Services backend,langchain
  "version": "0.2.0",
Start infra only (Ollama + Playwright, used by app stack):
    {
./start.ps1 -InfraOnly
      "type": "python",
Start in attached mode (logs stay in the terminal):
      "connect": { "host": "localhost", "port": 5671 },
./start.ps1 -Attach
    },
Stop everything (app + infra):
      "name": "Attach LangChain (debugpy)",
./stop.ps1
      "request": "attach",
Stop only selected app services:
      "justMyCode": true
./stop.ps1 -Services backend,langchain
```

Prune after stopping:
{
"name": "Attach FastMCP (debugpy)",
"type": "python",
"request": "attach",
"connect": { "host": "localhost", "port": 5673 },
"justMyCode": true
}
]
}

````

(Frontend Node inspect is commented out; to enable, uncomment the `frontend` section in the generated debug override file and add a Node attach config.)

Node attach example:

```json
{
  "name": "Attach Frontend (Node Inspect)",
  "type": "node",
  "request": "attach",
  "port": 9229,
  "restart": true
}
````

## Breakpoints & Flow

1. Start with `./start.ps1 -Debug`.

- Note: without pwsh installed, run `docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build`

2. Attach to `backend` port 5671 — breakpoints in `backend/server.py` will halt HTTP or WebSocket request handling.
3. Attach to `langchain` port 5672 — set breakpoints in agent logic (`langchain/src/agent.py`, callbacks) to inspect thought/action cycles.
4. Attach to `fastmcp` port 5673 — breakpoints in `fastmcp/src/tools.py` for navigation, screenshot, or content extraction tools.

## Common Debug Scenarios

### Investigate Browser Tool Failures

- Attach FastMCP (5673)
- Trigger a task from frontend
- Verify domain filtering, rate limiting, and error object structure.

### Agent Decision Loop Analysis

- Attach LangChain (5672)
- Set breakpoints in `execute_research_task`
- Observe sequence of tool calls and memory usage.

### API/WebSocket Issues

- Attach Backend (5671)
- Inspect task creation, event streaming, and screenshot endpoints.

## FastMCP Local vs Docker Hybrid

If you prefer to run FastMCP locally:

1. Stop only fastmcp service:
   ```powershell
   ./stop.ps1 -Services fastmcp
   ```
2. Set `FASTMCP_HOST=host.docker.internal` in `.env` (on Linux you may need an extra host mapping in compose).
3. From `fastmcp/` run (use Poetry for local development):
      ```powershell
      # Install dependencies with Poetry
      cd fastmcp
      poetry install --with dev

      # Start FastMCP under debugpy
      python -m debugpy --listen 0.0.0.0:5673 --wait-for-client server.py
      ```
4. Attach VS Code to port 5673.

## Stopping Services

```powershell
./stop.ps1 -All
```

Selective stop:

```powershell
./stop.ps1 -Services backend,langchain
```

Prune unused resources:

```powershell
./stop.ps1 -Prune
```

Help:

```powershell
./stop.ps1 -Help
```

## Troubleshooting

| Issue                         | Cause                                    | Fix                                                    |
| ----------------------------- | ---------------------------------------- | ------------------------------------------------------ |
| Debugger won't attach         | Port not exposed                         | Ensure `-Debug` was passed, regenerate override        |
| Breakpoints never hit         | Service not restarted with debug command | Run `./stop.ps1 -All` then `./start.ps1 -Debug`        |
| Frontend cannot reach backend | Env mismatch                             | Check `.env` values and container logs                 |
| FastMCP tool errors           | Playwright not healthy                   | Verify `container/docker-compose.yml` infra is running |

## Best Practices

- Keep debug sessions short to avoid holding locks.
- Use selective service start (`-Services`) when focusing on one component.
- Prefer Docker debug over local to match production-like environment.
- Capture logs in `logs/` for post-mortem analysis.

## Next Steps

- Add dedicated VS Code tasks for starting/stopping in debug.
- Integrate live reload (watch + debug) for Python services via `watchfiles`.
- Add structured tracing (OpenTelemetry) across service boundaries.

---

_Version: 1.0 — Updated: 2025-11-07_
