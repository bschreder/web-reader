# Integrating Zod Validation into Existing TaskForm

This guide shows how to add Zod validation to the existing [TaskForm.tsx](./src/components/TaskForm.tsx) component.

## Current Implementation

The current `TaskForm` has basic validation:

```typescript
if (!question.trim()) {
  setError("Question is required");
  return;
}
```

## Enhanced Implementation with Zod

### Step 1: Import Zod Schema

```typescript
import { CreateTaskRequestSchema } from "@src/schemas/task.schema";
import { ZodError } from "zod";
```

### Step 2: Add Validation State

```typescript
const [validationErrors, setValidationErrors] = useState<
  Record<string, string>
>({});
```

### Step 3: Update Submit Handler

Replace the current validation with Zod:

```typescript
async function onSubmit(e: React.FormEvent): Promise<void> {
  e.preventDefault();
  setError(null);
  setValidationErrors({});

  // Build request object
  const requestData = {
    question,
    seedUrl: seedUrl || undefined,
    searchEngine: searchEngine,
    maxResults: maxResults,
    safeMode: safeMode,
    maxDepth: maxDepth,
    maxPages: maxPages,
    timeBudget: timeBudget,
    sameDomainOnly: sameDomainOnly,
    allowExternalLinks: allowExternalLinks,
  };

  // Validate with Zod
  const result = CreateTaskRequestSchema.safeParse(requestData);

  if (!result.success) {
    // Extract field-level errors
    const fieldErrors: Record<string, string> = {};
    result.error.issues.forEach((issue) => {
      const fieldName = issue.path.join(".");
      fieldErrors[fieldName] = issue.message;
    });
    setValidationErrors(fieldErrors);
    setError("Please fix the validation errors below");
    return;
  }

  // Data is validated, proceed with submission
  setSubmitting(true);
  try {
    const { id } = await createTask(result.data); // Use validated data
    navigate({ to: `/tasks/${id}` });
  } catch (err) {
    if (err instanceof ZodError) {
      setError("Validation error: " + err.message);
    } else {
      setError(err instanceof Error ? err.message : String(err));
    }
  } finally {
    setSubmitting(false);
  }
}
```

### Step 4: Display Field-Level Errors

Update each input field to show validation errors:

```tsx
{
  /* Question Field */
}
<div>
  <label htmlFor="question" className="block text-sm font-medium mb-1">
    Question *
  </label>
  <input
    id="question"
    type="text"
    value={question}
    onChange={(e) => setQuestion(e.target.value)}
    className={`w-full px-4 py-2 border rounded ${
      validationErrors.question ? "border-red-500" : "border-gray-300"
    }`}
  />
  {validationErrors.question && (
    <p className="text-red-500 text-sm mt-1">{validationErrors.question}</p>
  )}
</div>;

{
  /* Seed URL Field */
}
<div>
  <label htmlFor="seedUrl" className="block text-sm font-medium mb-1">
    Starting URL (optional)
  </label>
  <input
    id="seedUrl"
    type="url"
    value={seedUrl}
    onChange={(e) => setSeedUrl(e.target.value)}
    className={`w-full px-4 py-2 border rounded ${
      validationErrors.seedUrl ? "border-red-500" : "border-gray-300"
    }`}
    placeholder="https://example.com"
  />
  {validationErrors.seedUrl && (
    <p className="text-red-500 text-sm mt-1">{validationErrors.seedUrl}</p>
  )}
</div>;

{
  /* Max Pages Field */
}
<div>
  <label htmlFor="maxPages" className="block text-sm font-medium mb-1">
    Max Pages
  </label>
  <input
    id="maxPages"
    type="number"
    value={maxPages}
    onChange={(e) => setMaxPages(parseInt(e.target.value, 10))}
    className={`w-full px-4 py-2 border rounded ${
      validationErrors.maxPages ? "border-red-500" : "border-gray-300"
    }`}
    min="1"
  />
  {validationErrors.maxPages && (
    <p className="text-red-500 text-sm mt-1">{validationErrors.maxPages}</p>
  )}
</div>;
```

### Step 5: Optional - Real-time Validation

Add real-time validation as users type:

```typescript
const handleQuestionChange = (value: string): void => {
  setQuestion(value);

  // Real-time validation
  const result = CreateTaskRequestSchema.shape.question.safeParse(value);
  if (!result.success) {
    setValidationErrors((prev) => ({
      ...prev,
      question: result.error.issues[0]?.message ?? "Invalid",
    }));
  } else {
    setValidationErrors((prev) => {
      const { question, ...rest } = prev;
      return rest;
    });
  }
};

const handleSeedUrlChange = (value: string): void => {
  setSeedUrl(value);

  if (!value) {
    // Clear error if empty (optional field)
    setValidationErrors((prev) => {
      const { seedUrl, ...rest } = prev;
      return rest;
    });
    return;
  }

  // Real-time validation
  const result = CreateTaskRequestSchema.shape.seedUrl.safeParse(value);
  if (!result.success) {
    setValidationErrors((prev) => ({
      ...prev,
      seedUrl: result.error.issues[0]?.message ?? "Invalid URL",
    }));
  } else {
    setValidationErrors((prev) => {
      const { seedUrl, ...rest } = prev;
      return rest;
    });
  }
};
```

Then use them in the inputs:

```tsx
<input
  value={question}
  onChange={(e) => handleQuestionChange(e.target.value)}
  // ...
/>

<input
  value={seedUrl}
  onChange={(e) => handleSeedUrlChange(e.target.value)}
  // ...
/>
```

## Benefits

1. **Consistent Validation**: Same rules as API and backend
2. **Better UX**: Field-level error messages
3. **Type Safety**: Validated data is strongly typed
4. **Maintainability**: Single source of truth for validation rules
5. **Comprehensive**: Validates URLs, numbers, enums, etc.

## Validation Rules Enforced

- `question`: Required, non-empty string
- `seedUrl`: Optional, must be valid URL format
- `maxDepth`, `maxPages`, `timeBudget`, `maxResults`: Must be positive integers
- `searchEngine`: Must be one of: 'duckduckgo', 'bing', 'google', 'custom'
- All boolean fields are validated

## Error Messages

Zod provides helpful default messages:

- "Question is required" - for empty required fields
- "Must be a valid URL" - for invalid URLs
- "Expected number, received nan" - for invalid numbers
- Custom messages can be added to schema

## Testing

After integration, test:

1. Submit with empty question → Should show "Question is required"
2. Enter invalid URL → Should show "Must be a valid URL"
3. Enter negative number → Should show validation error
4. Valid form → Should submit successfully

## See Also

- [TaskFormExample.tsx](./src/components/TaskFormExample.tsx) - Complete working example
- [ZOD_USAGE.md](./ZOD_USAGE.md) - Full Zod usage documentation
- [task.schema.ts](./src/schemas/task.schema.ts) - Schema definitions
