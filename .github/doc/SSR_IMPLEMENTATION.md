# Frontend SSR Architecture Implementation

## Overview

The Web Reader frontend now implements **Selective Server-Side Rendering (SSR)** using TanStack Start, enabling optimized performance, better SEO, and improved initial page load times.

## Architecture

### SSR Configuration

- **Root Route** (`src/routes/__root.tsx`): `ssr: true`
  - All child routes inherit SSR by default
  - Server renders the HTML shell and initial layout
  - Client hydrates and takes over interaction

- **Index Route** (`src/routes/index.tsx`): `ssr: true`
  - Form submission page - no server-side data loading required
  - Component renders statically with minimal client logic
  - Full client-side interactivity for form handling

- **History Route** (`src/routes/history.tsx`): `ssr: true` with `loader`
  - Fetches task history on server during initial request
  - Server renders page with pre-populated task list
  - Client hydrates and enables dynamic filtering/sorting
  - Benefits: Fast initial load, SEO-friendly, reduced time-to-first-meaningful-paint

- **Task Detail Route** (`src/routes/tasks/$id.tsx`): `ssr: true` with `loader`
  - Fetches task details on server before rendering
  - Server renders complete task page with data
  - Client hydrates and sets up real-time WebSocket streaming
  - Benefits: Faster task page load, proper Open Graph tags support

### Server Functions

Server functions are defined in `src/lib/server-functions.ts` using `createServerFn`:

```typescript
export const getTaskServerFn = createServerFn({...}).handler(async (taskId) => {
  // Runs on server during initial request
  // Runs on client during subsequent navigation (via React Query)
  return fetch(`${API_URL}/api/tasks/${taskId}`);
});
```

**Functions:**

- `getTaskServerFn(taskId)` - Fetch single task details
- `listTasksServerFn(offset, limit)` - Fetch task list with pagination
- `createTaskServerFn(req)` - Create new task (POST)
- `cancelTaskServerFn(taskId)` - Cancel existing task (DELETE)

### Request Flow

#### Initial Page Load (SSR Path)

```
1. Browser requests /tasks/abc123
2. Server calls loader: getTaskServerFn('abc123')
3. API call happens on backend server (not exposed to client)
4. Page renders on server with task data
5. HTML sent to client
6. Client hydrates React tree
7. WebSocket connection established for real-time updates
8. Client-side React Query takes over for future navigation
```

#### Client-Side Navigation (Hydration Path)

```
1. User clicks link to /tasks/another-id
2. TanStack Router calls loader on client
3. Server function executes in browser
4. Task data fetched and loaded
5. Component renders with data
6. WebSocket streaming begins
```

## Use Cases Met

### UC-01: Question → Web Search → Answer (Depth-limited)

- ✅ Index route renders form on server
- ✅ Form submission creates task via server function
- ✅ Task detail route loads task data server-side
- ✅ WebSocket streams real-time progress
- ✅ Initial HTML includes task structure for faster FCP

### UC-02: Question → Seed URL → Linked Reading

- ✅ Same SSR flow as UC-01
- ✅ Server-side data loading enables faster rendering
- ✅ History route shows previously executed tasks

### UC-03: Rate Limits, Budgets, and Guardrails

- ✅ Server functions enforce API timeouts (30s)
- ✅ Task history available for audit trail
- ✅ Real-time progress streaming via WebSocket

## Performance Benefits

| Metric                        | Benefit                                         |
| ----------------------------- | ----------------------------------------------- |
| FCP (First Contentful Paint)  | Reduced by rendering HTML server-side           |
| FID (First Input Delay)       | Improved with pre-hydrated state                |
| CLS (Cumulative Layout Shift) | Stable with server-rendered layout              |
| SEO                           | Task pages include proper meta tags and content |
| Initial Load                  | No spinners, instant content visibility         |

## Technical Details

### Hydration Strategy

- Server renders complete HTML (including layout)
- Client receives and hydrates React tree
- JavaScript takes over for interactivity
- No content shift or "flash of unstyled content"

### Data Freshness

- Loaders run on server (using backend API)
- Query clients configured with appropriate stale-while-revalidate
- WebSocket provides real-time updates after hydration
- Client-side React Query handles cache updates

### Error Handling

- Server function timeouts (30s per request)
- Graceful fallback to empty data on server errors
- Client-side error boundaries handle hydration mismatches
- Network errors display in UI with retry options

## Configuration

### Environment Variables

- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)
- `VITE_WS_URL`: WebSocket URL (default: ws://localhost:8000)

### Router Configuration

- Located in `src/router.tsx`
- Uses `createRouter` from TanStack Start
- Configured with error boundaries and scroll restoration

### Entry Points

- **Server**: `src/entries/server.tsx` - Runs on Node.js
- **Client**: `src/entries/client.tsx` - Runs in browser

## Routing Structure

```
src/routes/
├── __root.tsx              # Root layout (SSR)
├── index.tsx               # Home/form (SSR)
├── history.tsx             # Task history (SSR + loader)
└── tasks/
    └── $id.tsx             # Task detail (SSR + loader)
```

## Type Safety

Server functions include proper TypeScript types:

```typescript
import type { TaskResponse, TaskListResponse } from "@src/types/task";

// Type-safe server function
const task: TaskResponse = await getTaskServerFn(taskId);
const list: TaskListResponse = await listTasksServerFn(0, 100);
```

## Testing

### Unit Tests

- Test server functions in isolation
- Mock API responses
- Test error handling

### E2E Tests

- Test SSR rendering
- Verify hydration
- Test client-side navigation
- Verify WebSocket streaming

### Coverage

- Target: >80%
- Includes server function paths
- Tests error boundaries and fallbacks

## Future Enhancements

1. **Static Prerendering**: Prerender history page with recent tasks
2. **ISR (Incremental Static Regeneration)**: Cache task pages and revalidate on updates
3. **Edge Rendering**: Run some loaders at CDN edge for faster responses
4. **Streaming HTML**: Stream component chunks as they render (currently full HTML sent)
5. **Partial Hydration**: Defer hydration for non-interactive components
