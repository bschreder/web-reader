# Implementation Summary: UC-01, UC-02, UC-03

## Overview

Successfully implemented frontend and backend support for all three use cases from the requirements:

- **UC-01**: Question → Web Search → Answer (Depth-limited)
- **UC-02**: Question → Seed URL → Linked Reading  
- **UC-03**: Rate Limits, Budgets, and Guardrails (Operational)

## Changes Made

### Backend Changes

#### 1. Extended TaskCreate Model (`backend/src/models.py`)
Added new parameters:
- `search_engine`: 'duckduckgo' | 'bing' | 'google' | 'custom' (default: 'duckduckgo')
- `max_results`: int (1-50, default: 10)
- `safe_mode`: bool (default: True)
- `same_domain_only`: bool (default: False)
- `allow_external_links`: bool (default: True)

#### 2. Updated Task Class (`backend/src/tasks.py`)
- Extended `__init__` to accept new UC parameters
- Updated `to_dict()` to include all UC parameters in API responses
- Modified `create_task()` function signature

#### 3. Updated Server (`backend/server.py`)
- Pass all new parameters when creating tasks from API requests

### Frontend Changes

#### 1. Removed Duplicate Entry Files
- Deleted `src/main.tsx` (duplicate of `entries/client.tsx`)
- Kept standard TanStack Start entry structure in `entries/`

#### 2. Updated Type Definitions (`src/types/task.ts`)
- Replaced nested `options` object with flat parameter structure
- Added all UC-01, UC-02, UC-03 parameters to `CreateTaskRequest`
- Added 'created' status to `TaskStatus` enum

#### 3. Enhanced TaskForm Component (`src/components/TaskForm.tsx`)
- Added collapsible "Advanced Options" section
- Organized parameters by use case:
  - **UC-01 (Search Settings)**: search_engine, max_results, safe_mode
  - **UC-02 (Link Following)**: max_depth, same_domain_only, allow_external_links
  - **UC-03 (Limits)**: max_pages, time_budget
- All parameters optional with sensible defaults
- Includes help text and validation

#### 4. Created E2E Tests

**UC-01.spec.ts** (9 tests):
- Happy path: submit question and receive answer
- Parameter validation: max_results, safe_mode, search_engine
- Boundary testing: max_results (1-50), max_depth (1-5)
- Default parameter verification
- Error handling: empty question, invalid inputs

**UC-02.spec.ts** (11 tests):
- Happy path: seed URL navigation
- Link following constraints: same_domain_only, allow_external_links
- URL format handling: query params, fragments, invalid URLs
- Fallback to search when no seed URL provided
- Hybrid scenarios combining UC-01 and UC-02 parameters

**UC-03.spec.ts** (9 tests):
- Limit enforcement: max_pages (1-50), time_budget (30-600s), max_depth (1-5)
- Default limit verification
- Boundary value testing for all limits
- Minimal resource configuration (strictest limits)
- Maximum resource configuration (most generous limits)
- Comprehensive test with all UC parameters combined

**Total: 29 E2E tests**

## Test Execution

### Run All UC Tests
\`\`\`bash
cd /workspaces/web-reader/frontend
npx playwright test tests/e2e/UC-*.spec.ts
\`\`\`

### Run Specific UC
\`\`\`bash
npx playwright test tests/e2e/UC-01.spec.ts  # Search workflow
npx playwright test tests/e2e/UC-02.spec.ts  # Seed URL workflow  
npx playwright test tests/e2e/UC-03.spec.ts  # Limits & guardrails
\`\`\`

### Prerequisites
Tests require running services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

Start with:
\`\`\`bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d
\`\`\`

## API Compatibility

The backend now fully supports the OpenAPI schema with all UC parameters. Access documentation at:
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

FastAPI automatically generates and validates the OpenAPI specification.

## What's Not Implemented (Out of Scope)

While the **API surface** is complete, the **agent logic** for these use cases is not yet implemented:

### Missing Agent Features
1. **Search Engine Integration**: No DuckDuckGo/Bing/Google SERP parsing
2. **Link Following Logic**: No link extraction, prioritization, or depth tracking
3. **Evidence Aggregation**: No multi-page synthesis
4. **Rate Limiting Enforcement**: Backend accepts parameters but doesn't enforce delays
5. **Domain Filtering at Runtime**: No pre-navigation domain checks in agent

These features belong in the `langchain` service and are tracked separately. The frontend E2E tests verify parameter passing and UI behavior, not end-to-end research workflows.

## Next Steps

To make tests fully functional (not just parameter validation):

1. **Implement Search Integration** (`langchain/src/search.py`):
   - DuckDuckGo SERP parsing
   - Search result extraction
   - Query construction

2. **Implement Link Following** (`langchain/src/agent.py`):
   - Extract links from page content
   - Track visited URLs and depth
   - Respect same_domain_only/allow_external_links

3. **Implement Rate Limiting** (`fastmcp/src/rate_limiting.py`):
   - Already exists but needs agent integration
   - Enforce 10-20s delays
   - Handle 429 responses

4. **Update Agent Prompts** (`langchain/src/agent.py`):
   - Search-first workflow for UC-01
   - Seed URL navigation for UC-02
   - Respect all limits from UC-03

## Files Changed

### Backend
- `backend/src/models.py` - Extended TaskCreate model
- `backend/src/tasks.py` - Updated Task class and create_task function
- `backend/server.py` - Pass new parameters

### Frontend
- `frontend/src/types/task.ts` - Updated type definitions
- `frontend/src/components/TaskForm.tsx` - Enhanced form with advanced options
- `frontend/src/main.tsx` - Removed (duplicate)
- `frontend/tests/e2e/UC-01.spec.ts` - New E2E tests
- `frontend/tests/e2e/UC-02.spec.ts` - New E2E tests
- `frontend/tests/e2e/UC-03.spec.ts` - New E2E tests

## Verification

\`\`\`bash
# Frontend builds and typechecks successfully
cd frontend && npm run lint:fix && npm run typecheck

# All 29 tests are recognized by Playwright
npx playwright test --list tests/e2e/UC-*.spec.ts
# Output: "Total: 29 tests in 3 files"
\`\`\`

## OpenAPI for Python

FastAPI includes built-in OpenAPI support (no additional packages needed):
- **Automatic Schema Generation**: Based on Pydantic models
- **Swagger UI**: Interactive API documentation at `/docs`
- **ReDoc**: Alternative docs at `/redoc`
- **JSON Schema**: Machine-readable spec at `/openapi.json`

No additional installation required for OpenAPI functionality.
