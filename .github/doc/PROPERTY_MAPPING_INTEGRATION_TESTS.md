# Property Mapping Integration Tests

## Overview

Created comprehensive integration tests for camelCase ↔ snake_case property mapping between frontend (JavaScript/TypeScript) and backend (Python) API endpoints.

## Test Suite

**File**: [backend/tests/integration/test_property_mapping.py](backend/tests/integration/test_property_mapping.py)

**Test Count**: 13 tests, all passing ✅

### Test Categories

#### 1. **Input Acceptance Tests**

- `test_create_task_with_camelcase_input` - Verify API accepts camelCase JSON from frontend
- `test_both_camelcase_and_snakecase_accepted_on_input` - Verify backward compatibility with snake_case (due to Pydantic's `populate_by_name=True`)

#### 2. **Response Format Tests**

- `test_create_task_response_uses_camelcase` - Verify POST /api/tasks returns camelCase properties
- `test_get_task_response_uses_camelcase` - Verify GET /api/tasks/{taskId} returns camelCase
- `test_list_tasks_uses_camelcase` - Verify GET /api/tasks returns camelCase in list
- `test_response_model_consistency_across_endpoints` - Verify consistent camelCase across all endpoints

#### 3. **Data Integrity Tests**

- `test_property_values_preserved_through_mapping` - Verify values aren't corrupted during transformation
- `test_create_task_with_minimal_payload` - Verify minimal required fields work
- `test_create_task_with_default_parameters` - Verify default parameters are applied

#### 4. **Validation Tests**

- `test_invalid_enum_value_rejected` - Verify searchEngine enum validation
- `test_property_range_validation` - Verify maxDepth range constraints (1-5)
- `test_missing_required_field_validation` - Verify required field validation

#### 5. **API Documentation Tests**

- `test_field_description_in_openapi_schema` - Verify OpenAPI schema generation

## Implementation Details

### Backend Configuration

**File**: [backend/src/models.py](backend/src/models.py)

```python
def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

class TaskCreate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,      # Auto-convert snake_case → camelCase
        populate_by_name=True          # Accept both naming conventions
    )
    # All fields use snake_case in Python code
    question: str
    seed_url: Optional[str]
    max_depth: int
    # ... etc
```

### JSON Serialization

**File**: [backend/server.py](backend/server.py)

```python
def custom_json_encoder(obj):
    """Custom JSON encoder that handles Pydantic models with by_alias."""
    if isinstance(obj, BaseModel):
        return obj.model_dump(by_alias=True, exclude_none=False)
    return jsonable_encoder(obj)

app.json_encoder = custom_json_encoder
```

## What Tests Verify

✅ **Frontend → Backend Communication**

- Frontend sends: `{ "seedUrl": "...", "maxDepth": 2, "searchEngine": "google" }`
- Backend receives and parses correctly (Pydantic aliases handle conversion)

✅ **Backend → Frontend Communication**

- Backend stores: `{ "seed_url": "...", "max_depth": 2, "search_engine": "google" }`
- API returns: `{ "seedUrl": "...", "maxDepth": 2, "searchEngine": "google" }`

✅ **Validation**

- Input validation works with camelCase properties
- Enum constraints checked (searchEngine: duckduckgo|bing|google|custom)
- Range constraints checked (maxDepth: 1-5, maxPages: 1-50, etc.)

✅ **Consistency**

- All endpoints return same property names
- No snake_case leakage in API responses

## Running Tests

```bash
# Run all property mapping tests
python3 -m pytest tests/integration/test_property_mapping.py -v

# Run specific test
python3 -m pytest tests/integration/test_property_mapping.py::TestPropertyMappingIntegration::test_create_task_response_uses_camelcase -v

# Run with coverage
python3 -m pytest tests/integration/test_property_mapping.py --cov=src --cov-report=html
```

## Test Results

```
===================== 13 passed in 4.62s ======================
Coverage: 62% (models.py at 100%)
```

All tests verify the complete request/response cycle:

1. **Input**: camelCase JSON from frontend
2. **Processing**: Pydantic alias conversion and validation
3. **Output**: camelCase JSON in API response

## Architecture

```
Frontend (TypeScript)
    ↓ sends JSON with camelCase
Browser/fetch()
    ↓ HTTP POST /api/tasks
FastAPI Route Handler
    ↓ receives JSON body
Pydantic TaskCreate Model
    ↓ applies alias_generator=to_camel
    ↓ populate_by_name=True
Python code (snake_case fields)
    ↓ business logic
Python Response
    ↓ model_dump(by_alias=True)
FastAPI Encoder
    ↓ converts to camelCase JSON
HTTP Response
    ↓ 201 Created
Browser
    ↓ receives JSON with camelCase
Frontend (TypeScript)
```

## Key Features Tested

| Feature                        | Test                                                | Status |
| ------------------------------ | --------------------------------------------------- | ------ |
| camelCase input accepted       | test_create_task_with_camelcase_input               | ✅     |
| camelCase in response          | test_create_task_response_uses_camelcase            | ✅     |
| Backward compat (snake_case)   | test_both_camelcase_and_snakecase_accepted_on_input | ✅     |
| No snake_case in API responses | test_response_model_consistency_across_endpoints    | ✅     |
| Data integrity preserved       | test_property_values_preserved_through_mapping      | ✅     |
| Validation (enum)              | test_invalid_enum_value_rejected                    | ✅     |
| Validation (range)             | test_property_range_validation                      | ✅     |
| Validation (required)          | test_missing_required_field_validation              | ✅     |
| OpenAPI docs                   | test_field_description_in_openapi_schema            | ✅     |

## Notes

- Tests use FastAPI's `TestClient` for synchronous testing
- No external services required (all tests self-contained)
- Tests verify full HTTP request/response cycle
- Comprehensive coverage of happy paths, edge cases, and error conditions
- All UC-01/UC-02/UC-03 parameters properly mapped and validated
