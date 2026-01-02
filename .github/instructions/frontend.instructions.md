--- 
applyTo: ./frontend/**/*.{ts,tsx}
description: This file describes the post-change validation steps for Frontend TypeScript/React files.
---
# Frontend - Post-Change Validation Instructions

**Scope**: This applies to all TypeScript/React files in `./frontend/**/*.{ts,tsx}`

After making any changes or additions to TypeScript/React files in the frontend directory, you **MUST** run the following validation steps in order:

## 0. Verify Dependencies First (CRITICAL)

**Before validating Frontend changes**, check if any changes were made to dependent projects:

### If Backend was modified:
Frontend depends on Backend (calls Backend API and WebSocket). If Backend files were changed, you **MUST** first execute all steps in `.github/instructions/backend.instructions.md` to ensure Backend is working correctly before proceeding with Frontend validation.

### If LangChain was modified:
Backend depends on LangChain. If LangChain files were changed, ensure Backend validation is completed (which includes LangChain validation).

### If FastMCP was modified:
LangChain depends on FastMCP. If FastMCP files were changed, ensure full dependency chain is validated:
1. `.github/instructions/fastmcp.instructions.md`
2. `.github/instructions/langchain.instructions.md`
3. `.github/instructions/backend.instructions.md`

Then proceed with Frontend validation.

### Dependency Chain:
```
FastMCP (MCP tools) → LangChain (orchestration) → Backend (API) → Frontend
```

Always validate dependencies from left to right before validating the current project.

---

## 1. Navigate to Frontend Directory

```bash
cd ./frontend
```

## 2. Run ESLint

Run ESLint to check for code style and quality issues:

```bash
npm run lint
```

If errors are found, attempt to auto-fix them:

```bash
npm run lint:fix
```

If there are remaining errors that cannot be auto-fixed, manually correct them before proceeding.

## 3. Run TypeScript Type Checker

Ensure TypeScript has no type errors:

```bash
npm run typecheck
```

Fix any type errors before proceeding.

## 4. Run Unit Tests

Run all unit tests to ensure functionality is not broken:

```bash
npm run test:unit
```

Fix any failing tests before proceeding.

## 5. Run Browser Tests

Run browser-based component and integration tests:

```bash
npm run test:browser
```

Fix any failing browser tests before proceeding.

## 6. Run E2E Tests

Run all end-to-end tests to validate the complete workflow:

```bash
npm run test:e2e
```

Fix any failing E2E tests before proceeding.

## 7. Run Full Test Suite with Coverage

Run the complete test suite with coverage reporting:

```bash
npm run test:coverage
```

Verify that code coverage meets the required thresholds. Fix any coverage gaps as necessary before proceeding.

## 8. Build the Application

Build the frontend application for production validation:

```bash
npm run build
```

Ensure the build completes without errors or warnings.

## 9. Verify Dev Server Starts

Verify that the development server can start and connect to the backend:

```bash
npm run dev
```

The dev server should start without errors. In the console output, verify:
- Vite dev server is running on `http://localhost:3000`
- No connection errors to Backend API
- WebSocket connection attempts are visible in the logs

Stop the dev server with `Ctrl+C` after verification.

**Important**: Ensure the Backend service is running before starting the dev server, as the frontend will attempt to connect to it.

## Quick Command Reference

For rapid validation during development:

```bash
# Full validation in one go (from frontend directory)
cd ./frontend && \
  npm run lint:fix && \
  npm run typecheck && \
  npm run test:unit && \
  npm run test:browser && \
  npm run test:e2e && \
  npm run build
```

Then verify dev server:

```bash
npm run dev
```

(Stop with Ctrl+C after verification)

## Critical Reminders

- **Verify Backend first**: Always ensure Backend service is running and healthy before validating Frontend
- **Never skip tests**: All tests must pass before considering the change complete
- **Fix linting first**: Code style issues should be resolved before running tests
- **Type safety**: All TypeScript errors must be resolved
- **E2E tests are mandatory**: They validate the complete user workflow
- **Build must succeed**: Ensure production build completes without errors
- **Dev server integration**: The dev server must be able to connect to Backend
- **WebSocket connectivity**: Verify real-time updates work correctly

## Common Issues and Solutions

### ESLint Errors
- Import order issues: Let eslint auto-fix with `--fix`
- Line length: Consider refactoring long lines for readability
- Unused variables: Remove them or prefix with `_` if intentional
- React hooks: Ensure all dependencies are in dependency arrays

### TypeScript Errors
- Type mismatches: Check against Backend API response types
- Missing type definitions: Import types from `src/types/`
- Schema validation: Ensure Zod schemas match Backend Pydantic models
- Component props: Verify prop types match usage

### Test Failures
- API connection: Ensure Backend service is running on port 8000
- WebSocket issues: Check WebSocket URL configuration
- Component rendering: Verify component state and props
- Async operations: Ensure all promises are properly handled
- Timeouts: Increase timeout if tests are flaky

### Build Failures
- Dependency conflicts: Check package.json for version constraints
- Missing dependencies: Run `npm install` to ensure all deps are installed
- TypeScript errors: Run `npm run typecheck` to identify issues
- Asset loading: Verify all imported assets exist

### Dev Server Issues
- Port conflicts: Ensure port 3000  is available
- Backend connection: Verify Backend is running and accessible
- WebSocket URL: Check configuration in `src/lib/config.ts`
- Module resolution: Clear `.tanstack/tmp` directory if caching issues occur
- Hot Module Reload (HMR): Works automatically; restart dev server if not updating

## Integration Points

Frontend depends on and is depended upon by:

- **Backend** (DEPENDENCY): Calls Backend API for task submission and WebSocket for real-time updates
- **Config files**: API URL from `src/lib/config.ts` and root `.env`
- **Zod schemas**: Task validation schemas in `src/schemas/task.schema.ts`
- **TanStack Router**: Client-side routing and navigation
- **TanStack Query**: Server state management and caching

### Critical Integration Flow:
1. **Frontend** renders TaskForm component
2. User submits task via form
3. **Frontend** validates with Zod schema
4. **Frontend** sends HTTP POST to Backend `/tasks/` endpoint
5. **Frontend** establishes WebSocket connection for real-time updates
6. **Backend** streams progress events (thinking, tool_call, etc.)
7. **Frontend** renders updates as they arrive
8. **Frontend** displays final results with artifacts

Always test the complete integration flow with Backend running.

## Frontend-Specific Validation

### Component Testing
- Test TaskForm component with various inputs
- Verify TaskHistory displays task list correctly
- Test TaskDetail component with streaming updates
- Validate AnswerDisplay renders results correctly
- Test error handling and user feedback

### State Management
- Verify TanStack Query caching works correctly
- Check component state management with React hooks
- Validate WebSocket state during reconnection
- Test task history persistence

### API Client Integration
- Test API endpoints match Backend routes
- Verify request/response serialization
- Check error handling and retry logic
- Validate WebSocket message format
- Test request cancellation on unmount

### Schema Validation (Zod)
- Test TaskRequest schema validates correctly
- Verify TaskResponse schema matches Backend model
- Check validation error messages
- Validate form validation before submission

### TypeScript Types
- Ensure task types match Backend models
- Verify type safety throughout components
- Check API response types
- Validate form field types

### Real-Time Communication
- Test WebSocket connection establishment
- Verify streaming events display in real-time
- Test connection error handling and recovery
- Validate message parsing and state updates
- Check memory leaks on connection cleanup

### Responsive UI
- Test layout on various screen sizes
- Verify form accessibility
- Test keyboard navigation
- Check dark/light mode if implemented
- Validate touch interactions on mobile

### Performance
- Check bundle size after build
- Verify lazy loading works correctly
- Test large task history scrolling
- Monitor memory usage during long sessions
- Check network request batching and caching
