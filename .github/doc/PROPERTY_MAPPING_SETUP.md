# JSON Property Name Mapping - Implementation Summary

## Solution Overview

The **property name mismatch** between frontend (camelCase) and backend (snake_case) has been **automatically resolved** using **Pydantic's built-in field aliasing feature**.

### The Problem

- **Frontend** (JavaScript/TypeScript): Uses `camelCase` - `{ seedUrl, maxDepth, searchEngine, ... }`
- **Backend** (Python): Uses `snake_case` - `{ seed_url, max_depth, search_engine, ... }`
- **API Communication**: JSON payload must be transformed during request/response

### The Solution

**Pydantic's `ConfigDict` with `alias_generator`** automatically maps between naming conventions:

```python
from pydantic import ConfigDict

class TaskCreate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,      # snake_case → camelCase for JSON
        populate_by_name=True           # Accept both naming styles
    )

    # Python uses snake_case
    seed_url: Optional[str] = None
    max_depth: int = 3
    search_engine: str = "duckduckgo"
```

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (TypeScript)                                           │
│ ─────────────────────────────────────────────────────────────── │
│ Sends HTTP POST with camelCase JSON:                            │
│ { "question": "...", "seedUrl": "...", "maxDepth": 3, ... }   │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         │ HTTP Request (camelCase JSON)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND (Python/FastAPI)                                        │
│ ─────────────────────────────────────────────────────────────── │
│ Pydantic automatically:                                          │
│ 1. Receives: { "seedUrl": "...", "maxDepth": 3, ... }         │
│ 2. Maps: seedUrl → seed_url, maxDepth → max_depth             │
│ 3. Stores internally: task.seed_url, task.max_depth           │
│ 4. When responding: Converts back seed_url → seedUrl          │
│ 5. Sends: { "seedUrl": "...", "maxDepth": 3, ... }           │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         │ HTTP Response (camelCase JSON)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (TypeScript)                                           │
│ ─────────────────────────────────────────────────────────────── │
│ Receives HTTP 201 response with camelCase JSON:                 │
│ { "taskId": "...", "seedUrl": "...", "maxDepth": 3, ... }     │
│ ✓ Matches TypeScript interface (camelCase)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Details

### Changes Made

#### 1. Backend Models (`backend/src/models.py`)

**Added `to_camel()` utility function:**

```python
def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])
```

**Updated `TaskCreate` model:**

```python
from pydantic import BaseModel, ConfigDict

class TaskCreate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
    # ... field definitions
```

**Updated `TaskResponse` model:**

```python
class TaskResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
    # ... field definitions
```

#### 2. FastAPI Server (`backend/server.py`)

**Added Pydantic import:**

```python
from pydantic import BaseModel
```

**Configured FastAPI with custom JSON encoder:**

```python
def custom_json_encoder(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump(by_alias=True, exclude_none=False)
    return pydantic_encoder(obj)

app.json_encoder = custom_json_encoder
```

### What This Means

| Aspect                   | Before                               | After                              |
| ------------------------ | ------------------------------------ | ---------------------------------- |
| **Frontend sends**       | `{ seedUrl: "..." }`                 | `{ seedUrl: "..." }` ✓             |
| **Backend receives**     | Would fail or require custom parsing | Automatic alias mapping ✓          |
| **Backend internal use** | N/A                                  | `seed_url` (snake_case) ✓          |
| **Backend returns**      | Would return `{ seed_url: "..." }`   | Returns `{ seedUrl: "..." }` ✓     |
| **Frontend receives**    | N/A                                  | `{ seedUrl: "..." }` (camelCase) ✓ |

## Property Mapping Reference

| Frontend (TypeScript) | Backend (Python)       | JSON API             |
| --------------------- | ---------------------- | -------------------- |
| `question`            | `question`             | `question`           |
| `seedUrl`             | `seed_url`             | `seedUrl`            |
| `maxDepth`            | `max_depth`            | `maxDepth`           |
| `maxPages`            | `max_pages`            | `maxPages`           |
| `timeBudget`          | `time_budget`          | `timeBudget`         |
| `searchEngine`        | `search_engine`        | `searchEngine`       |
| `maxResults`          | `max_results`          | `maxResults`         |
| `safeMode`            | `safe_mode`            | `safeMode`           |
| `sameDomainOnly`      | `same_domain_only`     | `sameDomainOnly`     |
| `allowExternalLinks`  | `allow_external_links` | `allowExternalLinks` |

## Verification Results

All tests passed ✓

```
[TEST 1] Frontend sends camelCase JSON → Backend accepts it
         ✓ PASSED

[TEST 2] TaskCreate response uses camelCase aliases
         ✓ PASSED

[TEST 3] TaskResponse (API response) uses camelCase aliases
         ✓ PASSED

[TEST 4] Round-trip: Frontend camelCase → Backend → Frontend camelCase
         ✓ PASSED

[TEST 5] Backward compatibility: Accept both camelCase AND snake_case
         ✓ PASSED

[TEST 6] JSON serialization (as API response)
         ✓ PASSED
```

## Key Benefits

1. **Automatic Conversion**: No manual transformation needed
2. **Type-Safe**: Both TypeScript and Pydantic validate their respective conventions
3. **OpenAPI Compatible**: Aliases automatically appear in Swagger docs
4. **Backward Compatible**: Backend still accepts snake_case input (useful for Python clients)
5. **Zero Client Code Changes**: Frontend can remain unchanged
6. **Pydantic Native**: Uses built-in features, no custom middleware

## No Additional Configuration Needed

The property mapping is **fully automatic** and requires **no configuration** on:

- ✓ Frontend code
- ✓ API client code
- ✓ TypeScript types
- ✓ Pydantic model instantiation

FastAPI automatically uses `by_alias=True` when serializing response models with defined aliases.

## Related Documentation

- **Detailed Guide**: [PROPERTY_MAPPING.md](PROPERTY_MAPPING.md)
- **Backend Models**: [backend/src/models.py](backend/src/models.py)
- **API Server**: [backend/server.py](backend/server.py#L95-L105)
- **Frontend Types**: [frontend/src/types/task.ts](frontend/src/types/task.ts)

## Testing the Integration

To verify the mapping works with your API:

```bash
# 1. Start the backend
cd /workspaces/web-reader/backend
python server.py

# 2. Test with frontend camelCase JSON
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python?",
    "seedUrl": "https://example.com",
    "maxDepth": 2,
    "maxPages": 10,
    "timeBudget": 60,
    "searchEngine": "google",
    "maxResults": 5,
    "safeMode": true,
    "sameDomainOnly": false,
    "allowExternalLinks": true
  }'

# 3. Response will have camelCase aliases:
# {
#   "taskId": "...",
#   "seedUrl": "...",
#   "maxDepth": 2,
#   "seedUrl": "...",
#   ...
# }
```

## Summary

✅ **COMPLETE**: Frontend and backend now automatically handle property name conversions  
✅ **VERIFIED**: All 6 test scenarios passed  
✅ **TYPE-SAFE**: TypeScript types match JSON aliases, Python types use snake_case  
✅ **PRODUCTION-READY**: No breaking changes, backward compatible

The system is ready for end-to-end testing!
