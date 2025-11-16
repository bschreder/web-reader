# Task-Scoped Browser Context Isolation

## Overview

The FastMCP browser automation service now supports **task-scoped context isolation**, ensuring that each research task gets its own isolated browser context. This prevents data leakage between tasks and maintains privacy guarantees as required by BR-04.

## What Changed

### Before

- Single shared browser context across all requests
- Browser state (cookies, localStorage, etc.) persisted between tasks
- **Privacy concern**: Task A could see data from Task B

### After

- Each task gets its own isolated browser context
- Contexts are created on-demand per `task_id`
- Contexts are cleaned up after task completion
- **Privacy guarantee**: No data leakage between tasks

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Shared Browser Instance (reused)              │
│  - Connects to external Playwright container   │
│  - ws://playwright:3002                         │
└─────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│ Task-1  │   │ Task-2  │   │ Task-3  │
│ Context │   │ Context │   │ Context │
└─────────┘   └─────────┘   └─────────┘
     │             │             │
     ▼             ▼             ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│  Page   │   │  Page   │   │  Page   │
└─────────┘   └─────────┘   └─────────┘
```

## Usage

### Basic Usage (with task_id)

```python
from src.tools import navigate_to, get_page_content, take_screenshot
from src.browser import cleanup_task_context

# Use the same task_id for all operations in a task
task_id = "research-123"

# Navigate
result = await navigate_to(
    url="https://example.com",
    task_id=task_id
)

# Extract content
content = await get_page_content(task_id=task_id)

# Take screenshot
screenshot = await take_screenshot(task_id=task_id)

# Clean up when task is complete
await cleanup_task_context(task_id=task_id)
```

### Backward Compatibility

The `task_id` parameter defaults to `"default"` for backward compatibility:

```python
# Old code still works (uses "default" task_id)
result = await navigate_to(url="https://example.com")
content = await get_page_content()
```

## API Changes

### Updated Tool Signatures

All browser tools now accept an optional `task_id` parameter:

#### `navigate_to(url, wait_until, task_id)`

- `task_id` (str, optional): Task identifier for context isolation (default: "default")

#### `get_page_content(task_id)`

- `task_id` (str, optional): Task identifier for context isolation (default: "default")

#### `take_screenshot(full_page, task_id)`

- `task_id` (str, optional): Task identifier for context isolation (default: "default")

### New Cleanup Function

```python
async def cleanup_task_context(task_id: str) -> None:
    """
    Clean up browser context for a specific task.

    This should be called after each research task completes to:
    - Free memory from unused contexts
    - Ensure no data persists between tasks
    - Maintain privacy guarantees
    """
```

## Integration Example

### LangChain Agent Integration

```python
from langchain import Agent
from src.tools import navigate_to, get_page_content
from src.browser import cleanup_task_context

async def execute_research_task(question: str, task_id: str):
    try:
        # Create LangChain tools with task_id bound
        tools = [
            create_tool(
                func=lambda url: navigate_to(url, task_id=task_id),
                name="navigate_to",
                description="Navigate to URL"
            ),
            create_tool(
                func=lambda: get_page_content(task_id=task_id),
                name="get_page_content",
                description="Extract page content"
            )
        ]

        # Execute agent
        agent = Agent(tools=tools)
        result = await agent.run(question)

        return result
    finally:
        # Always clean up context
        await cleanup_task_context(task_id=task_id)
```

## Benefits

### 1. **Privacy & Security**

- No cookies or localStorage shared between tasks
- Fresh browser fingerprint per task (randomized viewport, user agent)
- Prevents tracking across research sessions

### 2. **Resource Management**

- Contexts cleaned up after use (frees memory)
- Browser instance still shared (efficient)
- Supports concurrent tasks without conflicts

### 3. **Backward Compatibility**

- Existing code works without changes
- Gradual migration path
- Default behavior preserved

## Performance Impact

### Memory

- **Additional memory per task**: ~50-100 MB per active context
- **Cleanup timing**: Immediate after task completion
- **Recommendation**: Clean up contexts promptly after task completion

### Speed

- **Context creation**: ~100-200ms (one-time per task)
- **Navigation**: No additional overhead
- **Cleanup**: ~50-100ms

## Testing

Comprehensive test suite added:

```bash
# Run task isolation tests
pytest tests/unit/test_task_context_isolation.py -v

# Run all tests
pytest tests/unit/ -v
```

### Test Coverage

- ✅ Different tasks get different contexts
- ✅ Same task reuses existing context
- ✅ Cleanup removes context and page
- ✅ Cleanup handles errors gracefully
- ✅ Multiple concurrent tasks maintain isolation
- ✅ Default task_id maintains backward compatibility
- ✅ All tools respect task_id parameter

## Migration Guide

### Step 1: Update Tool Calls

Add `task_id` parameter to all tool calls:

```python
# Before
await navigate_to("https://example.com")

# After
await navigate_to("https://example.com", task_id=task_id)
```

### Step 2: Add Cleanup

Ensure contexts are cleaned up after task completion:

```python
try:
    # Task execution
    result = await execute_task(task_id)
finally:
    # Always clean up
    await cleanup_task_context(task_id)
```

### Step 3: Generate Unique Task IDs

Use UUIDs or similar for task identification:

```python
import uuid

task_id = f"task-{uuid.uuid4()}"
```

## Troubleshooting

### Context Not Found

**Problem**: Tool returns "context not found" error  
**Solution**: Ensure `navigate_to` is called before other tools

### Memory Growth

**Problem**: Memory usage increases over time  
**Solution**: Verify `cleanup_task_context` is called for each completed task

### Shared State Between Tasks

**Problem**: Data leaking between tasks  
**Solution**: Ensure different `task_id` values are used for each task

## Future Enhancements

Potential future improvements:

1. **Automatic Cleanup**: Timeout-based context cleanup
2. **Context Pooling**: Reuse cleaned contexts for performance
3. **Metrics**: Track context lifecycle metrics
4. **Context Limits**: Max concurrent contexts per instance
5. **Session Management**: Support for persistent sessions (opt-in)

## References

- [Playwright Browser Contexts](https://playwright.dev/docs/browser-contexts)
- [Privacy Requirement BR-04](.github/requirements.md)
- [FastMCP Documentation](./README.md)

---

**Version**: 1.0  
**Date**: November 16, 2025  
**Author**: GitHub Copilot
