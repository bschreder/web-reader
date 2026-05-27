# Web Reader Debug Guide

This is the canonical debug workflow for the monorepo.

## Command Surface

Use the wrapper commands only.

- Full debug stack: `./infra/scripts/wr.ps1 debug up --build`
- Infra only: `./infra/scripts/wr.ps1 up --infra --build`
- App only: `./infra/scripts/wr.ps1 up --app --build`
- Stop stack: `./infra/scripts/wr.ps1 down`
- Stream logs: `./infra/scripts/wr.ps1 logs [service]`

## Environment Setup

Root `.env` is the active runtime file used by compose and debug runs.

If you want to reset it to the canonical contract, copy [.env.example](.env.example) over [.env](.env).

[`infra/env/.env.example`](infra/env/.env.example) is the checked-in template for environment bootstrapping, and [`infra/env/.env.prod.example`](infra/env/.env.prod.example) is the production variant.

The shared logging keys are `LOG_LEVEL` and `LOG_TARGET`; they are global and consumed by all services.

Legacy entrypoints (`start.ps1`, `stop.ps1`, `container/*`, `docker/*`) are compatibility wrappers and should not be used for new workflows.

## Debug Ports

- Backend debugpy: `5671`
- LangChain debugpy: `5672`
- FastMCP debugpy: `5673`
- Frontend Node inspect: `9229`

## VS Code Launch Profiles

Use [.vscode/launch.json](.vscode/launch.json):

- `Debug (Devcontainer): Backend`
- `Debug (Devcontainer): LangChain`
- `Debug (Devcontainer): FastMCP`
- `Debug (Host): Backend`
- `Debug (Host): LangChain`
- `Debug (Host): FastMCP`
- `Debug Frontend (Node Inspect)`

And compounds:

- `Debug (Devcontainer): Python Services`
- `Debug (Host): Python Services`

## Recommended Flows

### Devcontainer Python debugging

1. Start stack: `./infra/scripts/wr.ps1 debug up --build`
2. Launch `Debug (Devcontainer): Python Services`
3. Set breakpoints in `apps/backend/`, `apps/langchain/`, or `apps/fastmcp/`

### Host attach debugging

1. Start stack: `./infra/scripts/wr.ps1 debug up --build`
2. Launch `Debug (Host): Python Services`
3. Set breakpoints from host VS Code session

### Frontend debug

1. Start debug stack: `./infra/scripts/wr.ps1 debug up --build`
2. Launch `Debug Frontend (Node Inspect)`

## Health Checks

- FastMCP: `curl http://localhost:3101/health`
- LangChain: `curl http://localhost:8001/health`
- Backend: `curl http://localhost:8000/health`

## Troubleshooting

- If attach fails, verify service is running: `./infra/scripts/wr.ps1 logs <service>`
- If ports conflict, run `./infra/scripts/wr.ps1 down` then restart.
- If backend starts before dependency readiness in debug mode, wait for health to report `healthy` before submitting tasks.
