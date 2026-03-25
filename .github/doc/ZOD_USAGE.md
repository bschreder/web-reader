# Zod Validation in Frontend

This project uses [Zod](https://zod.dev/) v4.2.1 for runtime validation and type safety.

## Overview

Zod provides:

- **Runtime validation** of API responses and user input
- **Type inference** from schemas for TypeScript
- **Clear error messages** with detailed validation feedback
- **Zero dependencies** and small bundle size (2kb gzipped)

## Usage

### Schema Definitions

All Zod schemas are defined in [src/schemas/task.schema.ts](./src/schemas/task.schema.ts):

```typescript
import {
  CreateTaskRequestSchema,
  TaskDetailSchema,
} from "@src/schemas/task.schema";
```

### Validating API Responses

The API client ([src/lib/api.ts](./src/lib/api.ts)) validates all responses:

```typescript
export async function getTask(id: string): Promise<TaskDetail> {
  const res = await fetch(`${API_URL}/api/tasks/${id}`);
  if (!res.ok) throw new Error(`Failed to get task: ${res.status}`);

  const data = await res.json();
  return TaskDetailSchema.parse(data); // ✅ Validates response
}
```

### Validating User Input

Form data is validated before sending to the API:

```typescript
export async function createTask(
  req: CreateTaskRequest
): Promise<{ id: string }> {
  const validatedReq = CreateTaskRequestSchema.parse(req); // ✅ Validates input

  const res = await fetch(`${API_URL}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(validatedReq),
  });
  // ...
}
```

### Validating WebSocket Events

Stream events are validated in [src/lib/ws.ts](./src/lib/ws.ts):

```typescript
this.ws.onmessage = (e: MessageEvent<string>): void => {
  try {
    const rawData = JSON.parse(e.data);
    const ev = StreamEventSchema.parse(rawData); // ✅ Validates event
    this.opts.onEvent(ev);
  } catch (err) {
    console.error("Invalid event data:", err);
  }
};
```

## Available Schemas

### Request Schemas

- `CreateTaskRequestSchema` - Validates task creation requests with constraints:
  - `question`: Required, non-empty string
  - `seedUrl`: Optional valid URL
  - `maxDepth`, `maxPages`, `timeBudget`: Optional positive integers
  - `searchEngine`: Optional enum ('duckduckgo' | 'bing' | 'google' | 'custom')
  - `maxResults`: Optional positive integer
  - `safeMode`, `sameDomainOnly`, `allowExternalLinks`: Optional booleans

### Response Schemas

- `TaskDetailSchema` - Validates task detail responses
- `TaskSummarySchema` - Validates task summary responses
- `CreateTaskResponseSchema` - Validates task creation response
- `ListTasksResponseSchema` - Validates task list response

### Stream Event Schemas

- `StreamEventSchema` - Discriminated union of all event types:
  - `ThinkingEventSchema`
  - `ToolCallEventSchema`
  - `ToolResultEventSchema`
  - `ScreenshotEventSchema`
  - `CompleteEventSchema`
  - `ErrorEventSchema`

### Supporting Schemas

- `TaskStatusSchema` - Enum validation
- `SearchEngineSchema` - Enum validation
- `CitationSchema` - Citation object validation

## Type Inference

Zod schemas can infer TypeScript types:

```typescript
import { z } from "zod";
import { CreateTaskRequestSchema } from "@src/schemas/task.schema";

// Infer the type from the schema
type CreateTaskRequest = z.infer<typeof CreateTaskRequestSchema>;

// Or use the exported type
import type { CreateTaskRequest } from "@src/schemas/task.schema";
```

## Error Handling

### Parse Errors

When validation fails, Zod throws a `ZodError` with detailed information:

```typescript
try {
  const task = TaskDetailSchema.parse(data);
} catch (err) {
  if (err instanceof z.ZodError) {
    console.error(err.issues); // Array of validation issues
  }
}
```

### Safe Parsing

For non-throwing validation, use `.safeParse()`:

```typescript
const result = TaskDetailSchema.safeParse(data);

if (!result.success) {
  console.error(result.error); // ZodError
} else {
  console.log(result.data); // Validated data
}
```

## Best Practices

1. **Validate at boundaries**: Always validate data coming from external sources (APIs, WebSockets, user input)
2. **Use parse for internal errors**: Use `.parse()` when validation failure is unexpected
3. **Use safeParse for user input**: Use `.safeParse()` for form validation to handle errors gracefully
4. **Reuse schemas**: Define schemas once and reuse them across the application
5. **Type inference**: Leverage `z.infer<>` for DRY type definitions

## Resources

- [Zod Documentation](https://zod.dev/)
- [Zod GitHub](https://github.com/colinhacks/zod)
- [Zod API Reference](https://zod.dev/api)
