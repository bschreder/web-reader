# Property Mapping Implementation - Complete

## Status: ✅ COMPLETE & VERIFIED

The **JSON property name mapping** between frontend (camelCase) and backend (snake_case) has been **fully implemented and tested**.

---

## Quick Answer

You asked: _"How can I set the JSON properties that are sent between the frontend and backend? Is there a model that I can use to change the names?"_

**Answer**: Use **Pydantic's `ConfigDict` with `alias_generator`** in your backend models. It automatically maps camelCase (JSON) ↔ snake_case (Python).

---

## Implementation

### Backend Models Configuration

**File**: [backend/src/models.py](backend/src/models.py)

```python
from pydantic import BaseModel, ConfigDict, Field

# Utility function
def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

# Apply to models
class TaskCreate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,      # Auto-convert snake_case → camelCase
        populate_by_name=True           # Accept both naming conventions
    )

    # Python uses snake_case
    question: str
    seed_url: Optional[str] = None
    max_depth: int = 3
    max_pages: int = 20
    time_budget: int = 120
    search_engine: str = "duckduckgo"
    max_results: int = 10
    safe_mode: bool = True
    same_domain_only: bool = False
    allow_external_links: bool = True
```

### FastAPI Configuration

**File**: [backend/server.py](backend/server.py)

FastAPI automatically handles the `by_alias=True` serialization when you define `response_model=TaskCreate` on your endpoints.

```python
@app.post("/api/tasks", response_model=TaskResponse, status_code=201)
async def create_new_task(task_data: TaskCreate):
    # FastAPI automatically uses by_alias=True when returning the model
    return TaskResponse(**task_dict)  # Returns camelCase JSON
```

---

## How It Works

```
Request Flow (Frontend → Backend):
  1. Frontend sends: {"seedUrl": "...", "maxDepth": 3, ...}
  2. FastAPI receives JSON payload
  3. Pydantic `TaskCreate` model with aliases:
     - Accepts "seedUrl" as input
     - Maps to internal field: seed_url
     - Validates using snake_case field name
  4. Backend code uses: task.seed_url (snake_case)

Response Flow (Backend → Frontend):
  1. Backend creates: TaskResponse(seed_url="...", ...)
  2. FastAPI serializes with response_model=TaskResponse
  3. Pydantic model_dump(by_alias=True):
     - Takes internal: seed_url
     - Converts to alias: seedUrl
     - Outputs to JSON: {"seedUrl": "...", ...}
  4. Frontend receives: camelCase JSON matching TypeScript interface
```

---

## Property Mapping Reference

| Frontend (camelCase) | Backend (snake_case)   | JSON Response        |
| -------------------- | ---------------------- | -------------------- |
| `question`           | `question`             | `question`           |
| `seedUrl`            | `seed_url`             | `seedUrl`            |
| `maxDepth`           | `max_depth`            | `maxDepth`           |
| `maxPages`           | `max_pages`            | `maxPages`           |
| `timeBudget`         | `time_budget`          | `timeBudget`         |
| `searchEngine`       | `search_engine`        | `searchEngine`       |
| `maxResults`         | `max_results`          | `maxResults`         |
| `safeMode`           | `safe_mode`            | `safeMode`           |
| `sameDomainOnly`     | `same_domain_only`     | `sameDomainOnly`     |
| `allowExternalLinks` | `allow_external_links` | `allowExternalLinks` |

---

## Test Results

All 6 test scenarios passed ✓

```
✓ TEST 1: Frontend sends camelCase JSON → Backend accepts it
✓ TEST 2: TaskCreate serializes with camelCase aliases
✓ TEST 3: TaskResponse serializes with camelCase aliases
✓ TEST 4: Round-trip conversion successful
✓ TEST 5: Backward compatibility (accepts both camelCase AND snake_case)
✓ TEST 6: JSON serialization works correctly
```

### Verification Output

```
Mapping verification (Frontend → Backend):
  ✓ question = What is quantum computing?
  ✓ seedUrl → seed_url = https://www.nature.com
  ✓ maxDepth → max_depth = 3
  ✓ maxPages → max_pages = 25
  ✓ timeBudget → time_budget = 300
  ✓ searchEngine → search_engine = google
  ✓ maxResults → max_results = 15
  ✓ safeMode → safe_mode = True
  ✓ sameDomainOnly → same_domain_only = False
  ✓ allowExternalLinks → allow_external_links = True
```

---

## Files Modified

| File                                           | Changes                                                                                   |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [backend/src/models.py](backend/src/models.py) | Added `to_camel()` function, added `ConfigDict` to `TaskCreate` and `TaskResponse` models |
| [backend/server.py](backend/server.py)         | Added custom JSON encoder configuration (optional, for explicit control)                  |

## Files Referenced (No Changes Needed)

| File                                                                         | Reason                                             |
| ---------------------------------------------------------------------------- | -------------------------------------------------- |
| [frontend/src/types/task.ts](frontend/src/types/task.ts)                     | Already uses camelCase - compatible with aliases ✓ |
| [frontend/src/components/TaskForm.tsx](frontend/src/components/TaskForm.tsx) | Frontend sends camelCase - works automatically ✓   |

---

## Key Features

✅ **Automatic Conversion**: No manual transformation in code  
✅ **Type-Safe**: Both TypeScript and Pydantic enforce their conventions  
✅ **OpenAPI Compatible**: Aliases appear in Swagger documentation  
✅ **Backward Compatible**: Backend also accepts snake_case input  
✅ **Zero Frontend Changes**: Frontend works as-is  
✅ **Pydantic Native**: Uses built-in features, no custom middleware

---

## How to Use

### For Frontend Developers

Send camelCase JSON - that's it! Pydantic handles the rest.

```typescript
const response = await fetch("/api/tasks", {
  method: "POST",
  body: JSON.stringify({
    question: "...",
    seedUrl: "...", // camelCase
    maxDepth: 2,
    searchEngine: "google",
    // ...
  }),
});
```

### For Backend Developers

Write Python code using snake_case - the model handles JSON conversion.

```python
async def create_task(task_data: TaskCreate):
    # Use snake_case internally
    url = task_data.seed_url
    depth = task_data.max_depth
    engine = task_data.search_engine

    # When returning, Pydantic automatically converts to camelCase
    return TaskResponse(**db_record.dict())
```

---

## Common Questions

### Q: Do I need to change my frontend code?

**A:** No. Frontend already sends camelCase, which is exactly what the alias_generator expects.

### Q: Do I need to change my TypeScript types?

**A:** No. Your `CreateTaskRequest` interface already uses camelCase - it matches the JSON perfectly.

### Q: What if I want to accept Python clients too?

**A:** The `populate_by_name=True` setting handles it! Backend accepts both:

- `{"seedUrl": "..."}` (frontend style)
- `{"seed_url": "..."}` (Python style)

### Q: How does FastAPI know to return camelCase?

**A:** FastAPI calls `model.model_dump(by_alias=True)` automatically when you use `response_model=YourModel` and the model has a `ConfigDict` with `alias_generator`.

### Q: What about nested models?

**A:** The `ConfigDict` applies recursively. All nested Pydantic models also get the alias treatment.

---

## Documentation

- **Quick Setup Guide**: [PROPERTY_MAPPING_SETUP.md](PROPERTY_MAPPING_SETUP.md)
- **Detailed Reference**: [PROPERTY_MAPPING.md](PROPERTY_MAPPING.md)
- **Backend Models**: [backend/src/models.py](backend/src/models.py#L40-L76)
- **Pydantic Docs**: https://docs.pydantic.dev/latest/api/config/#alias-generator

---

## Summary

The property mapping is **complete, tested, and production-ready**.

**No additional configuration is needed.** The system:

- Accepts camelCase from frontend ✓
- Processes with snake_case internally ✓
- Returns camelCase in API responses ✓
- All handled automatically by Pydantic ✓

You can now run end-to-end tests with confidence that property names will be correctly mapped throughout the request/response cycle.
