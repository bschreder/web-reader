---
description: "Use when reviewing, building, linting, or testing the Web Reader workspace. Defines the repository-specific command matrix and validation prerequisites for review agents and implementation agents."
---

# Web Reader Review Workflow

Use this file when an agent needs repository-specific commands for review, validation, or release checks. Keep generic review logic in user-level agents; use this file only for Web Reader command selection and prerequisite handling.

## Base Branch Resolution

When a branch-diff review needs a merge base, resolve in this order:

1. `main`
2. `origin/main`
3. `master`
4. `origin/master`

If none exists, stop and report a configuration error.

## Validation Strategy

- Prefer a full report over fail-fast behavior.
- Always run e2e validation when the relevant suite exists.
- Validate dependencies from left to right when multiple services are affected:
  - FastMCP
  - LangChain
  - Backend
  - Frontend
- Use existing task definitions when they are appropriate for starting or stopping infrastructure.

## Infrastructure Prerequisites

Use these when integration or e2e validations require the stack or shared infrastructure:

- Start infrastructure only: `Start Infrastructure`
- Start full app stack for release-style or full-stack validation: `Start (Debug)`
- Stop infrastructure or app stack after validation if you started it for the review.

## Repository-Level Commands

Run these from the repository root when a full workspace check is needed:

```bash
./scripts/test-all-python.sh
./scripts/test-all.sh all
```

Use `./scripts/test-all.sh all` for full release-style validation because it includes unit, integration, and e2e coverage across the stack.

## Service Command Matrix

### FastMCP

Run from `./fastmcp`:

```bash
uv run ruff check .
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
uv run pytest tests/e2e/ -v
```

### LangChain

Run from `./langchain`:

```bash
uv run ruff check .
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
uv run pytest tests/e2e/ -v
```

### Backend

Run from `./backend`:

```bash
uv run ruff check .
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
uv run pytest tests/e2e/ -v
```

### Frontend

Run from `./frontend`:

```bash
npm run lint
npm run typecheck
npm run build
npm run test:unit
npm run test:browser
npm run test:e2e
npm run test:coverage
```

## Review Guidance For This Repository

- Security focus: pay extra attention to secrets, secret logging, `.env` handling, config propagation, and logs.
- Performance focus: watch for repeated HTTP calls across services, blocking async behavior, browser-session churn, and frontend bundle or render regressions.
- Architecture focus: preserve the required chain `Frontend -> Backend -> LangChain -> FastMCP -> Playwright` and do not bypass LangChain orchestration.
- Privacy focus: preserve deidentified browsing behavior and fresh browser context isolation.

## Notes

- If a service-specific instruction file applies to edited files, honor it in addition to this workflow file.
- If a required dependency is not running, report the blocked validation explicitly instead of silently skipping it.