# LangChain Orchestrator Service

Agent orchestration service that connects the Backend API, FastMCP tools, and Ollama LLM to execute web research tasks.

## Architecture

```
Backend API (FastAPI)
     ↓ HTTP POST /execute
LangChain Orchestrator (This Service)
     ├→ Ollama LLM (HTTP) - ReAct reasoning
     └→ FastMCP Server (HTTP/MCP) - Browser automation
          └→ Playwright Browser
```

## Features

- **ReAct Agent**: Step-by-step reasoning with tool use
- **MCP Protocol**: Clean separation between reasoning and execution
- **Tool Wrappers**: LangChain StructuredTools wrapping FastMCP browser automation
- **Streaming Support**: Real-time progress updates (TODO: WebSocket callbacks)
- **Error Recovery**: Automatic retry on parsing errors
- **Configurable**: Environment-based configuration

## Components

### 1. MCP Client (`src/mcp_client.py`)

- HTTP client for FastMCP server communication
- Tool invocation via MCP protocol
- Health checking
- Error handling and timeout management

### 2. Tool Wrappers (`src/tools.py`)

- `navigate_to`: Navigate browser to URL
- `get_page_content`: Extract page content and links
- `take_screenshot`: Capture page screenshots
- Wrapped as LangChain `StructuredTool`s with Pydantic schemas

### 3. Agent (`src/agent.py`)

- ReAct agent creation with Ollama LLM
- Configurable max iterations and execution time
- Custom prompt for web research tasks
- Result extraction and formatting

### 4. FastAPI Server (`server.py`)

- `/health` - Health check endpoint
- `/execute` - Execute research task endpoint
- CORS enabled
- Structured logging

## Installation

```bash
# Install dependencies
poetry install

# Install test dependencies
poetry install --with test
```

## Configuration

Environment variables (see `.env` at repository root):

```bash
# Service
LANGCHAIN_HOST=0.0.0.0
LANGCHAIN_PORT=8001

# FastMCP connection
FASTMCP_HOST=fastmcp
FASTMCP_PORT=3000

# Ollama LLM
OLLAMA_HOST=ollama
OLLAMA_PORT=11434
OLLAMA_MODEL=qwen2.5:7b

# Agent behavior
AGENT_MAX_ITERATIONS=15
AGENT_MAX_EXECUTION_TIME=300
AGENT_TEMPERATURE=0.0
AGENT_VERBOSE=true

# Logging
LOG_LEVEL=info
LOG_TARGET=console
LOG_FILE=logs/langchain.log
```

## Running

### Standalone

```bash
python server.py
```

### With Docker Compose

```bash
docker-compose up langchain
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_mcp_client.py -v
```

### Test Coverage

Current coverage: **71%**

```
src/config.py:       100%
src/tools.py:        100%
src/mcp_client.py:    74%
src/agent.py:          0% (TODO: agent execution tests)
```

## API Usage

### Execute Task

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task-123",
    "question": "What is the capital of France?",
    "seed_url": "https://www.wikipedia.org",
    "max_depth": 3,
    "max_pages": 20,
    "time_budget": 120
  }'
```

Response:

```json
{
  "status": "success",
  "answer": "The capital of France is Paris...",
  "citations": [],
  "screenshots": [],
  "metadata": {
    "iterations": 5,
    "question": "What is the capital of France?"
  }
}
```

### Health Check

```bash
curl http://localhost:8001/health
```

Response:

```json
{
  "status": "healthy",
  "service": "langchain-orchestrator",
  "mcp_connected": true,
  "ollama_model": "qwen2.5:7b"
}
```

## Development

### Project Structure

```
langchain/
├── src/
│   ├── __init__.py
│   ├── config.py          # Environment configuration
│   ├── mcp_client.py      # FastMCP HTTP client
│   ├── tools.py           # LangChain tool wrappers
│   └── agent.py           # ReAct agent implementation
├── tests/
│   ├── conftest.py        # Shared fixtures
│   ├── test_mcp_client.py # MCP client tests
│   └── test_tools.py      # Tool wrapper tests
├── server.py              # FastAPI application
├── requirements.txt       # Production dependencies
├── requirements-test.txt  # Test dependencies
└── pytest.ini             # Pytest configuration
```

### Adding New Tools

1. Add tool function in `src/tools.py`:

```python
async def new_tool_wrapper(arg: str, mcp_client: MCPClient) -> str:
    result = await mcp_client.call_tool("new_tool", {"arg": arg})
    # Process and return human-readable message
    return f"Tool result: {result}"
```

2. Create Pydantic schema:

```python
class NewToolArgs(BaseModel):
    arg: str = Field(..., description="Tool argument")
```

3. Add to `create_langchain_tools()`:

```python
new_tool = StructuredTool.from_function(
    coroutine=lambda arg: new_tool_wrapper(arg, mcp_client),
    name="new_tool",
    description="Tool description for LLM",
    args_schema=NewToolArgs,
)
tools.append(new_tool)
```

4. Write tests in `tests/test_tools.py`

## TODO

- [ ] Add WebSocket callback handler for real-time streaming
- [ ] Extract citations from agent intermediate steps
- [ ] Extract screenshots from tool call results
- [ ] Add conversation memory (ConversationBufferMemory)
- [ ] Add agent execution tests with mocked LLM
- [ ] Add integration tests with real Ollama (optional)
- [ ] Implement early stopping on answer found
- [ ] Add retry logic with exponential backoff
- [ ] Add metrics and monitoring hooks

## Dependencies

- **LangChain**: Agent framework and tool abstractions
- **langchain-ollama**: Ollama LLM integration
- **FastAPI**: HTTP server
- **httpx**: Async HTTP client
- **Pydantic**: Data validation
- **loguru**: Structured logging

## License

See repository root LICENSE file.
