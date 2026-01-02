# JSON Property Name Mapping (camelCase ↔ snake_case)

## Overview

The Web Reader system handles property name mapping between the **frontend** (JavaScript/TypeScript) and **backend** (Python/FastAPI) using **Pydantic's field aliasing** feature.

- **Frontend** uses `camelCase` (JavaScript convention)
- **Backend** uses `snake_case` (Python convention)
- **Automatic conversion** happens at the HTTP boundary via Pydantic

## How It Works

### Backend Configuration

The backend uses Pydantic's `ConfigDict` with `alias_generator` to automatically map between Python field names and JSON property names:

#### [backend/src/models.py](backend/src/models.py)

```python
from pydantic import BaseModel, ConfigDict, Field

def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

class TaskCreate(BaseModel):
    """Request model for creating a new task."""

    model_config = ConfigDict(
        alias_generator=to_camel,      # Convert snake_case → camelCase for JSON
        populate_by_name=True           # Accept both naming conventions in input
    )

    # Python field names (snake_case)
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

### Configuration Details

| Setting                    | Purpose                                                             |
| -------------------------- | ------------------------------------------------------------------- |
| `alias_generator=to_camel` | Automatically generates camelCase aliases for all snake_case fields |
| `populate_by_name=True`    | Accepts **both** naming conventions on input (flexible)             |

### What This Means

**Input Handling (Frontend → Backend):**

- Frontend sends: `{ "seedUrl": "...", "maxDepth": 3, ... }`
- Backend accepts BOTH:
  - `{ "seedUrl": "...", "maxDepth": 3, ... }` (camelCase - JavaScript style)
  - `{ "seed_url": "...", "max_depth": 3, ... }` (snake_case - Python style)
- Pydantic automatically maps to Python fields: `seed_url`, `max_depth`, etc.

**Output Handling (Backend → Frontend):**

- Backend stores: `task.seed_url = "..."`
- FastAPI serializes with `by_alias=True`
- Frontend receives: `{ "seedUrl": "...", "maxDepth": 3, ... }` (camelCase)

## Property Mapping Examples

| Python Field           | JSON Alias           | Frontend Property    |
| ---------------------- | -------------------- | -------------------- |
| `seed_url`             | `seedUrl`            | `seedUrl`            |
| `max_depth`            | `maxDepth`           | `maxDepth`           |
| `max_pages`            | `maxPages`           | `maxPages`           |
| `time_budget`          | `timeBudget`         | `timeBudget`         |
| `search_engine`        | `searchEngine`       | `searchEngine`       |
| `max_results`          | `maxResults`         | `maxResults`         |
| `safe_mode`            | `safeMode`           | `safeMode`           |
| `same_domain_only`     | `sameDomainOnly`     | `sameDomainOnly`     |
| `allow_external_links` | `allowExternalLinks` | `allowExternalLinks` |

## Implementation Details

### Backend Models

**Modified Files:**

- [backend/src/models.py](backend/src/models.py):
  - Added `to_camel()` utility function
  - Added `ConfigDict` to `TaskCreate` model
  - Added `ConfigDict` to `TaskResponse` model

### FastAPI Configuration

**Modified Files:**

- [backend/server.py](backend/server.py):
  - Configured custom JSON encoder to use `by_alias=True`
  - Ensures all Pydantic models serialize with aliases

### Frontend Types

**Reference Files:**

- [frontend/src/types/task.ts](frontend/src/types/task.ts):
  - `CreateTaskRequest` uses camelCase properties
  - Matches JSON aliases from backend

## API Request/Response Examples

### Creating a Task

**Frontend Request (TypeScript):**

```typescript
const response = await fetch("/api/tasks", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    question: "What is Python?",
    seedUrl: "https://example.com", // camelCase
    maxDepth: 2,
    maxPages: 10,
    timeBudget: 60,
    searchEngine: "google",
    maxResults: 5,
    safeMode: false,
    sameDomainOnly: true,
    allowExternalLinks: false,
  }),
});
```

**Backend Processing (Python):**

```python
# Pydantic automatically maps camelCase input to snake_case fields
task_data = TaskCreate(**request_body)
# task_data.seed_url = "https://example.com"
# task_data.max_depth = 2
# etc.
```

**Backend Response (JSON):**

```json
{
  "taskId": "uuid-here",
  "question": "What is Python?",
  "seedUrl": "https://example.com", // camelCase (via alias_generator)
  "maxDepth": 2,
  "maxPages": 10,
  "timeBudget": 60,
  "searchEngine": "google",
  "maxResults": 5,
  "safeMode": false,
  "sameDomainOnly": true,
  "allowExternalLinks": false,
  "status": "created",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

**Frontend Receives (TypeScript):**

```typescript
interface Task {
  taskId: string;
  question: string;
  seedUrl?: string; // camelCase
  maxDepth: number;
  maxPages: number;
  timeBudget: number;
  searchEngine: string;
  maxResults: number;
  safeMode: boolean;
  sameDomainOnly: boolean;
  allowExternalLinks: boolean;
  status: "created" | "queued" | "running" | "completed" | "failed";
  createdAt: string;
}
```

## Verification

### Test Property Mapping

```bash
cd backend
python3 << 'EOF'
from src.models import TaskCreate

# Frontend sends camelCase
frontend_data = {
    "question": "Test?",
    "seedUrl": "https://example.com",
    "maxDepth": 2,
    "maxPages": 10,
    "timeBudget": 60,
    "searchEngine": "google",
    "maxResults": 5,
    "safeMode": False,
    "sameDomainOnly": True,
    "allowExternalLinks": False
}

task = TaskCreate(**frontend_data)
print(f"✓ Backend accepts camelCase from frontend")
print(f"  Internal field: task.seed_url = {task.seed_url}")

# Convert back to camelCase for API response
api_response = task.model_dump(by_alias=True)
print(f"✓ API response uses camelCase: {list(api_response.keys())}")
EOF
```

## Why This Approach?

1. **Convention Adherence**:

   - JavaScript/TypeScript use camelCase
   - Python uses snake_case
   - Each language respects its own conventions

2. **Pydantic Native Support**:

   - Aliases are built into Pydantic
   - No custom middleware needed
   - Automatic OpenAPI documentation

3. **Backward Compatibility**:

   - `populate_by_name=True` allows either naming style
   - Flexible for future transitions

4. **Type Safety**:
   - Frontend types match JSON aliases (camelCase)
   - Backend fields match Python conventions (snake_case)
   - TypeScript and Pydantic both validate

## OpenAPI Documentation

The alias configuration automatically appears in the auto-generated OpenAPI schema at `http://localhost:8000/docs`:

**Request Body Schema** shows camelCase property names (from aliases)  
**Response Schema** shows camelCase property names (from aliases)  
**Python docstrings** are preserved in the documentation

## Related Files

- **Backend Models**: [backend/src/models.py](backend/src/models.py)
- **API Server**: [backend/server.py](backend/server.py)
- **Frontend Types**: [frontend/src/types/task.ts](frontend/src/types/task.ts)
- **API Client**: [frontend/src/lib/api.ts](frontend/src/lib/api.ts)
