# Web Reader - Implementation Guide

This document provides implementation details, code patterns, and technical guidance for building the Web Reader system. This is a companion to `requirements.md`, which defines WHAT and WHY; this document describes HOW.

## Implementation Overview

The system is built using a microservices architecture with 6 containerized components:

1. Frontend (TanStack Start)
2. Backend API (FastAPI)
3. LangChain Orchestrator
4. FastMCP Server
5. Playwright Browser
6. Ollama LLM
## Multistage Dockerfile Pattern (Dev vs Prod)

All application services (`frontend`, `backend`, `langchain`, `fastmcp`) MUST use a three-stage Dockerfile:

1. `base` stage:
   - Runtime base (Python 3.13 slim / Node 24 alpine)
   - System packages only (no dev tooling)
   - Non-root user created (`appuser` with UID/GID stable)
   - Common environment variables (e.g. `PYTHONUNBUFFERED=1`, `NODE_ENV` default)
2. `dev` stage:
   - Installs development dependencies (Python: `pytest`, `pytest-cov`, `pytest-asyncio`, `watchfiles`, `debugpy`; Node: `vite`, `vitest`, `playwright`, `@types/*`)
   - Sets `ENVIRONMENT=development`
   - Exposes debug ports (backend 5671, langchain 5672, fastmcp 5673, frontend optional 9229)
   - Entry command uses watcher or hot reload (Python: `watchfiles 'uvicorn server:app --host 0.0.0.0 --port 8000' src/`; FastMCP / LangChain similar; frontend: `npm run dev -- --host 0.0.0.0` for Vite HMR)
3. `prod` stage:
   - Installs production-only dependencies
   - Copies source code (no mounts)
   - Optimized build (e.g. `poetry install --only main` or `pip install --no-cache-dir -r requirements.txt`)
   - Final CMD minimal (uvicorn with tuned workers; Node static serve / nginx)
   - Healthcheck readiness endpoints available.

Example Python service Dockerfile sketch:
```Dockerfile
FROM python:3.13-slim AS base
ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN useradd -m -u 1001 appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS dev
COPY requirements-test.txt requirements-test.txt
RUN pip install --no-cache-dir -r requirements-test.txt && pip install watchfiles debugpy
ENV ENVIRONMENT=development
USER appuser
COPY src ./src
COPY server.py .
CMD ["watchfiles", "uvicorn server:app --host 0.0.0.0 --port 8000 --reload", "src/"]

FROM base AS prod
COPY src ./src
COPY server.py .
USER appuser
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Example frontend Dockerfile sketch:
```Dockerfile
FROM node:24-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM base AS dev
ENV NODE_ENV=development
RUN npm install --save-dev vite vitest @vitest/browser playwright
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS build
ENV NODE_ENV=production
COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK CMD wget -q -O /dev/null http://localhost || exit 1
```

## Development vs Production Compose

Two compose files layer configurations:
1. `docker/docker-compose.yml` (production baseline) – uses `prod` image target, minimal environment, persistent data volumes only.
2. `docker/docker-compose.dev.yml` (development overlay) – selects `dev` build target, mounts source + test directories, exposes debug ports, overrides CMD with watcher/HMR.

Launch (dev):
```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d --build
```

Example dev overrides snippet:
```yaml
services:
  backend:
    build:
      context: ../backend
      target: dev
    volumes:
      - ../backend/src:/app/src:rw
      - ../backend/tests:/app/tests:rw
    environment:
      - ENVIRONMENT=development
    command: ["watchfiles", "uvicorn server:app --host 0.0.0.0 --port 8000", "src/"]
    ports:
      - "8000:8000"
      - "5671:5671"
  frontend:
    build:
      context: ../frontend
      target: dev
    volumes:
      - ../frontend/src:/app/src:rw
      - ../frontend/tests:/app/tests:rw
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - VITE_API_URL=http://localhost:8000
    command: ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

## Volume Mount Strategy
| Mode | Source Code | Tests | Node/Python deps | Data (artifacts, models) |
|------|-------------|-------|------------------|---------------------------|
| Dev  | Mounted (rw)| Mounted| In image (dev + watchers) | Mounted named volumes |
| Prod | Copied (ro) | Copied| Production only | Mounted named volumes |

Benefits: fast iteration in dev, immutable & predictable in prod.

## Test Directory Layout & Coverage
Each project:
```
<project>/
  src/
  tests/
    unit/
    integration/
    e2e/
    (frontend adds browser/)
```

Coverage thresholds:
- Statement: >80%
- Branch: >80%
- Function: >80%

Python execution (devcontainer preferred):
```bash
cd fastmcp && pytest tests/unit --cov=src --cov-branch
cd backend && pytest tests/integration -v
cd langchain && pytest tests/e2e -v
```
Optional container exec:
```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec fastmcp pytest tests/unit --cov=src --cov-branch
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec backend pytest tests/integration -v
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec langchain pytest tests/e2e -v
```

Frontend execution (devcontainer):
```bash
cd frontend && npm run test:unit
npm run test:browser
npx playwright test tests/e2e
```
Optional container exec:
```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec frontend npm run test:unit
```

## Cross-Service End-to-End Tests
Optional root-level `tests/e2e` can coordinate multi-service flows (e.g., submit task, observe streaming, verify citations). Use a dedicated ephemeral service in `docker-compose.dev.yml`:
```yaml
  e2e-tests:
    image: python:3.13-slim
    working_dir: /workspace
    volumes:
      - ../tests/e2e:/workspace/tests/e2e:ro
    depends_on:
      - backend
      - langchain
      - fastmcp
      - ollama
    command: ["bash", "-c", "pip install pytest pytest-asyncio && pytest tests/e2e -v"]
```

## Start Script Integration (`start.ps1`)
The PowerShell script should optionally layer development compose file:
- Default (docker mode): production-only compose
- With dev flag (future enhancement) or internal logic: `docker/docker-compose.yml` + `docker/docker-compose.dev.yml`
Ensure help text documents how dev overlay is applied for hot reload.

## Async & Streaming Conventions
Python services:
- Public I/O functions use `async def`.
- Long-running or multi-step operations stream progress via WebSocket callbacks (agent thoughts, tool invocations, results).
- Tools return structured JSON (status, data, error fields) instead of raising unhandled exceptions.

Frontend:
- WebSocket client handles incremental events; UI updates are diff-based.
- Avoid blocking operations in event handlers; leverage React state for streaming.

## Adding New Services
When introducing another service:
1. Create multistage Dockerfile with same pattern.
2. Add service section to both compose files (prod target / dev target overrides).
3. Implement test scaffolding & coverage.
4. Update `project-plan.md` phase tasks if it changes timeline.
5. Extend `start.ps1` only if orchestration semantics differ.

## Summary
This implementation guide codifies dev vs prod container strategy, supports test execution via devcontainer shell (preferred) or inside dev-stage containers, and documents async/streaming patterns required for reliable agentic behavior.

## LangChain Agent Implementation

### Agentic Loop Pattern

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler

# Initialize LLM
llm = ChatOllama(
  model="qwen3:8b",
    base_url="http://ollama:11434",
    temperature=0.1,  # Low temperature for factual research
    callbacks=[StreamingCallbackHandler()]
)

# MCP Client for browser tools
from mcp_client import MCPClient

mcp = MCPClient("http://fastmcp:3000")

# Wrap MCP tools as LangChain tools
from langchain.tools import StructuredTool

browser_tools = [
    StructuredTool.from_function(
        func=lambda url, wait_until="networkidle": mcp.call_tool("navigate_to", {
            "url": url,
            "wait_until": wait_until
        }),
        name="navigate_to",
        description="Navigate browser to URL and wait for page load. Use this to visit search engines or web pages.",
        args_schema=NavigateToSchema
    ),
    StructuredTool.from_function(
        func=lambda: mcp.call_tool("get_page_content", {}),
        name="get_page_content",
        description="Extract text content, title, and metadata from current page. Use this to read page content.",
        args_schema=GetPageContentSchema
    ),
    StructuredTool.from_function(
        func=lambda schema: mcp.call_tool("extract_structured_data", {"schema": schema}),
        name="extract_structured_data",
        description="Extract structured data from page using a schema. Use this for search results or specific data extraction.",
        args_schema=ExtractDataSchema
    ),
    StructuredTool.from_function(
        func=lambda full_page=False: mcp.call_tool("take_screenshot", {"full_page": full_page}),
        name="take_screenshot",
        description="Capture screenshot of current page. Use this for visual evidence or debugging.",
        args_schema=ScreenshotSchema
    ),
    # Add other tools...
]

# Create agent with memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# System prompt for research agent
system_prompt = """You are a web research assistant. Your goal is to answer user questions by browsing the web.

Guidelines:
1. Start with a web search (navigate to DuckDuckGo) unless a seed URL is provided
2. Extract and analyze search results before visiting pages
3. Visit the most relevant pages (top 3-5 results)
4. Synthesize information from multiple sources
5. Always cite sources with URLs
6. If you can't find a definitive answer, say so and provide the best available information
7. Respect depth limits and time budgets
8. Handle errors gracefully and continue with partial results when possible

Current Constraints:
- Max link depth: {max_depth}
- Max pages: {max_pages}
- Time budget: {time_budget} seconds
- Rate limit: 5 requests per 90 seconds, 10-20 second delays between requests

Remember: Be thorough but efficient. Quality over quantity."""

# Create agent
agent = create_tool_calling_agent(
    llm=llm,
    tools=browser_tools,
    prompt=PromptTemplate.from_template(system_prompt)
)

# Agent executor with callbacks
agent_executor = AgentExecutor(
    agent=agent,
    tools=browser_tools,
    memory=memory,
    verbose=True,
    max_iterations=15,
    handle_parsing_errors=True,
    early_stopping_method="generate",  # Generate final answer if iterations exceeded
    callbacks=[WebSocketCallbackHandler(websocket)]
)

# Execute research task
async def execute_research_task(question: str, seed_url: Optional[str] = None,
                                 max_depth: int = 3, max_pages: int = 20,
                                 time_budget: int = 120) -> Dict[str, Any]:
    """
    Execute a research task using the LangChain agent.

    Args:
        question: User's question
        seed_url: Optional starting URL (skips search if provided)
        max_depth: Maximum link depth to follow
        max_pages: Maximum pages to visit
        time_budget: Maximum time in seconds

    Returns:
        Dict with answer, citations, confidence, and metadata
    """
    input_text = f"""Question: {question}

    {'Starting URL: ' + seed_url if seed_url else 'Start with a web search on DuckDuckGo'}

    Research this question thoroughly and provide a well-cited answer."""

    try:
        result = await agent_executor.ainvoke({
            "input": input_text,
            "chat_history": memory.load_memory_variables({}),
            "max_depth": max_depth,
            "max_pages": max_pages,
            "time_budget": time_budget
        })

        return {
            "answer": result["output"],
            "citations": extract_citations(result),
            "confidence": estimate_confidence(result),
            "pages_visited": count_tool_calls(result, "navigate_to"),
            "metadata": {
                "iterations": result.get("iterations", 0),
                "total_tokens": result.get("total_tokens", 0)
            }
        }
    except Exception as e:
        logger.error(f"Research task failed: {e}")
        return {
            "answer": "I encountered an error while researching this question.",
            "error": str(e),
            "citations": [],
            "confidence": 0.0
        }
```

### Custom WebSocket Callback Handler

```python
from langchain.callbacks.base import BaseCallbackHandler
from fastapi import WebSocket
import json

class WebSocketCallbackHandler(BaseCallbackHandler):
    """
    Streams LangChain agent events to WebSocket clients in real-time.
    """

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.tool_start_time = None

    async def send_event(self, event_type: str, data: dict):
        """Send event to WebSocket client."""
        try:
            await self.websocket.send_json({
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                **data
            })
        except Exception as e:
            logger.warning(f"Failed to send WebSocket event: {e}")

    def on_llm_start(self, serialized: dict, prompts: list[str], **kwargs):
        """Called when LLM starts generating."""
        asyncio.create_task(self.send_event("agent:thinking", {
            "content": "Analyzing the question and planning next steps..."
        }))

    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes generating."""
        asyncio.create_task(self.send_event("agent:thought", {
            "content": response.generations[0][0].text
        }))

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        """Called when a tool is about to be executed."""
        self.tool_start_time = time.time()
        tool_name = serialized.get("name", "unknown")

        asyncio.create_task(self.send_event("agent:tool_call", {
            "tool": tool_name,
            "args": input_str,
            "status": "starting"
        }))

    def on_tool_end(self, output: str, **kwargs):
        """Called when a tool finishes executing."""
        duration = time.time() - self.tool_start_time if self.tool_start_time else 0

        # Special handling for screenshot tool
        if "screenshot" in str(kwargs.get("name", "")):
            asyncio.create_task(self.send_event("agent:screenshot", {
                "image": output,  # base64 image
                "duration": duration
            }))
        else:
            asyncio.create_task(self.send_event("agent:tool_result", {
                "tool": kwargs.get("name", "unknown"),
                "result": output[:500],  # Truncate long results
                "duration": duration,
                "status": "success"
            }))

    def on_tool_error(self, error: Exception, **kwargs):
        """Called when a tool encounters an error."""
        asyncio.create_task(self.send_event("agent:tool_result", {
            "tool": kwargs.get("name", "unknown"),
            "error": str(error),
            "status": "error",
            "recoverable": isinstance(error, (TimeoutError, NetworkError))
        }))

    def on_agent_finish(self, finish, **kwargs):
        """Called when agent finishes (success or failure)."""
        asyncio.create_task(self.send_event("agent:complete", {
            "answer": finish.return_values.get("output", ""),
            "citations": finish.return_values.get("citations", []),
            "confidence": finish.return_values.get("confidence", 0.5)
        }))
```

### Memory Management

```python
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory

# Option 1: Full conversation history (for short tasks)
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="output"
)

# Option 2: Windowed memory (keep last N turns, for longer tasks)
memory = ConversationBufferWindowMemory(
    k=5,  # Keep last 5 conversation turns
    memory_key="chat_history",
    return_messages=True
)

# Option 3: Summary memory (for very long tasks - future enhancement)
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True
)

# Option 4: Vector-backed memory (future enhancement with vector DB)
from langchain.memory import VectorStoreRetrieverMemory
from langchain.vectorstores import Chroma

vectorstore = Chroma(persist_directory="/data/chroma")
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

memory = VectorStoreRetrieverMemory(
    retriever=retriever,
    memory_key="chat_history",
    input_key="input",
    output_key="output"
)
```

## FastMCP Server Implementation

### Server Setup

```python
from fastmcp import FastMCP
from playwright.async_api import async_playwright, Browser, BrowserContext
import asyncio

# Initialize FastMCP server
mcp = FastMCP("Browser Automation Server")

# Global browser instance (shared across contexts)
_browser: Optional[Browser] = None
_contexts: dict[str, BrowserContext] = {}

async def get_browser() -> Browser:
    """Get or create shared browser instance."""
    global _browser
    if _browser is None:
        playwright = await async_playwright().start()
        _browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
    return _browser

async def create_context(
    user_agent: Optional[str] = None,
    viewport: Optional[dict] = None
) -> BrowserContext:
    """Create a new deidentified browser context."""
    browser = await get_browser()

    # Randomize user agent if not provided
    if user_agent is None:
        user_agent = random.choice(USER_AGENT_POOL)

    # Randomize viewport if not provided
    if viewport is None:
        viewport = {
            "width": random.randint(1280, 1920),
            "height": random.randint(720, 1080)
        }

    context = await browser.new_context(
        user_agent=user_agent,
        viewport=viewport,
        ignore_https_errors=True,
        java_script_enabled=True,
        # Privacy settings
        accept_downloads=False,
        has_touch=False,
        is_mobile=False,
        permissions=[],  # No permissions granted
        geolocation=None,
        extra_http_headers={
            "DNT": "1",  # Do Not Track
            "Sec-GPC": "1"  # Global Privacy Control
        }
    )

    # Enable tracking prevention
    await context.add_init_script("""
        // Block tracking scripts
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
    """)

    return context

# Tool definitions
@mcp.tool()
async def navigate_to(url: str, wait_until: str = "networkidle") -> dict:
    """
    Navigate to a URL and wait for page load.

    Args:
        url: Target URL (must be http or https)
        wait_until: When to consider navigation complete
                    Options: 'load', 'domcontentloaded', 'networkidle'

    Returns:
        Dict with status, title, url, and timing info
    """
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        return {"error": "Invalid URL scheme. Must be http or https."}

    # Check domain filters
    if not is_domain_allowed(url):
        return {"error": f"Domain blocked by allow/deny lists: {urlparse(url).netloc}"}

    # Enforce rate limiting
    await enforce_rate_limit(urlparse(url).netloc)

    try:
        context = await get_or_create_context()
        page = await context.new_page()

        start_time = time.time()
        response = await page.goto(url, wait_until=wait_until, timeout=30000)
        load_time = time.time() - start_time

        # Handle error responses
        if response.status >= 400:
            status_text = HTTP_STATUS_MESSAGES.get(response.status, "Unknown Error")
            return {
                "status": "error",
                "http_status": response.status,
                "error": f"{response.status} {status_text}",
                "url": url,
                "suggestion": get_error_suggestion(response.status)
            }

        title = await page.title()
        final_url = page.url

        return {
            "status": "success",
            "title": title,
            "url": final_url,
            "http_status": response.status,
            "load_time": load_time,
            "redirected": final_url != url
        }

    except PlaywrightTimeoutError:
        return {
            "status": "error",
            "error": "Page load timeout (30s exceeded)",
            "url": url,
            "suggestion": "Try with 'load' wait_until option or increase timeout"
        }
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "url": url
        }

@mcp.tool()
async def get_page_content() -> dict:
    """
    Extract text content and metadata from the current page.

    Returns:
        Dict with title, text, url, links, and metadata
    """
    try:
        page = await get_current_page()

        # Extract structured content
        title = await page.title()
        url = page.url

        # Get main content (exclude nav, footer, ads)
        content = await page.evaluate("""
            () => {
                // Remove unwanted elements
                const exclude = 'nav, footer, aside, .ad, .advertisement, script, style';
                document.querySelectorAll(exclude).forEach(el => el.remove());

                // Get main content
                const main = document.querySelector('main, article, .content, #content')
                             || document.body;

                return {
                    text: main.innerText,
                    html: main.innerHTML
                };
            }
        """)

        # Extract links
        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: a.innerText.trim(),
                href: a.href,
                rel: a.rel
            })).filter(link => link.text && link.href)
        """)

        # Extract metadata
        metadata = await page.evaluate("""
            () => {
                const getMeta = (name) => {
                    const el = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
                    return el ? el.content : null;
                };

                return {
                    description: getMeta('description') || getMeta('og:description'),
                    keywords: getMeta('keywords'),
                    author: getMeta('author'),
                    published: getMeta('article:published_time'),
                    og_image: getMeta('og:image')
                };
            }
        """)

        return {
            "status": "success",
            "title": title,
            "url": url,
            "text": content["text"][:10000],  # Limit to 10k chars
            "links": links[:50],  # Limit to 50 links
            "metadata": metadata,
            "word_count": len(content["text"].split())
        }

    except Exception as e:
        logger.error(f"Content extraction error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
async def extract_structured_data(schema: dict) -> dict:
    """
    Extract structured data from the page using a schema.

    Args:
        schema: Dictionary defining the structure to extract
                Example: {"products": [{"name": "str", "price": "str"}]}

    Returns:
        Extracted data matching the schema
    """
    try:
        page = await get_current_page()

        # Use Playwright's built-in extraction with schema
        # This is a simplified example - production would use more sophisticated extraction
        data = await page.evaluate(f"""
            (schema) => {{
                // Custom extraction logic based on schema
                // This would be more sophisticated in production
                const result = {{}};

                // Example: Extract products
                if (schema.products) {{
                    result.products = Array.from(
                        document.querySelectorAll('.product, [data-product]')
                    ).map(el => ({{
                        name: el.querySelector('.name, .title')?.textContent?.trim(),
                        price: el.querySelector('.price')?.textContent?.trim()
                    }})).filter(p => p.name && p.price);
                }}

                return result;
            }}
        """, schema)

        return {
            "status": "success",
            "data": data,
            "count": len(data.get("products", []))
        }

    except Exception as e:
        logger.error(f"Structured extraction error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
async def take_screenshot(full_page: bool = False) -> str:
    """
    Capture a screenshot of the current page.

    Args:
        full_page: If True, capture entire scrollable page. If False, capture viewport only.

    Returns:
        Base64-encoded PNG image
    """
    try:
        page = await get_current_page()

        screenshot_bytes = await page.screenshot(
            full_page=full_page,
            type="png"
        )

        # Convert to base64
        import base64
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')

        return f"data:image/png;base64,{screenshot_b64}"

    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return f"Error capturing screenshot: {str(e)}"

# Rate limiting implementation
_rate_limits: dict[str, list[float]] = {}

async def enforce_rate_limit(domain: str):
    """
    Enforce rate limiting: max 5 requests per 90 seconds per domain.
    Adds randomized 10-20 second delay between requests.
    """
    now = time.time()

    # Clean old timestamps
    if domain in _rate_limits:
        _rate_limits[domain] = [t for t in _rate_limits[domain] if now - t < 90]
    else:
        _rate_limits[domain] = []

    # Check rate limit
    if len(_rate_limits[domain]) >= 5:
        oldest = _rate_limits[domain][0]
        wait_time = 90 - (now - oldest)
        if wait_time > 0:
            logger.warning(f"Rate limit reached for {domain}, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            now = time.time()
            _rate_limits[domain] = []

    # Random delay (10-20 seconds)
    if _rate_limits[domain]:  # Not first request
        delay = random.uniform(10, 20)
        logger.info(f"Rate limit delay: {delay:.1f}s")
        await asyncio.sleep(delay)

    # Record this request
    _rate_limits[domain].append(time.time())

# Domain filtering
ALLOWED_DOMAINS = load_domain_list("config/allowed-domains.txt")
DISALLOWED_DOMAINS = load_domain_list("config/disallowed-domains.txt")

def is_domain_allowed(url: str) -> bool:
    """Check if domain is allowed by allow/deny lists."""
    from urllib.parse import urlparse
    import fnmatch

    domain = urlparse(url).netloc.lower()

    # Check disallow list first
    for pattern in DISALLOWED_DOMAINS:
        if fnmatch.fnmatch(domain, pattern):
            return False

    # If allow list exists and is not empty, domain must be in it
    if ALLOWED_DOMAINS:
        for pattern in ALLOWED_DOMAINS:
            if fnmatch.fnmatch(domain, pattern):
                return True
        return False  # Not in allow list

    return True  # No allow list, and not in deny list

# Start server
if __name__ == "__main__":
    mcp.run()
```

## Backend API Implementation

### Logging (Python, Loguru)

Use Loguru with colorized console output during development and optional file logging controlled via `.env`.

Environment (.env):

```
LOG_LEVEL=info
LOG_TARGET=console   # console | file | both
LOG_FILE=logs/backend.log
```

FastAPI logger setup:

```python
from loguru import logger
import os
from pathlib import Path

LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
LOG_TARGET = os.getenv("LOG_TARGET", "console")
LOG_FILE = os.getenv("LOG_FILE", "logs/backend.log")

# Remove default handler and configure explicitly
logger.remove()

if LOG_TARGET in ("console", "both"):
  logger.add(
    sink=lambda msg: print(msg, end=""),
    colorize=True,
    level=LOG_LEVEL.upper(),
    enqueue=True,
    backtrace=False,
    diagnose=False,
  )

if LOG_TARGET in ("file", "both"):
  Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
  logger.add(
    LOG_FILE,
    rotation="10 MB",
    retention="14 days",
    compression="zip",
    level=LOG_LEVEL.upper(),
    enqueue=True,
    backtrace=False,
    diagnose=False,
    serialize=True,
  )

logger.info("Backend logger configured", extra={"level": LOG_LEVEL, "target": LOG_TARGET})
```

### FastAPI Server with WebSocket

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Optional
import uuid

app = FastAPI(title="Web Reader API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task models
class TaskCreate(BaseModel):
    question: str
    seed_url: Optional[str] = None
    max_depth: int = 3
    max_pages: int = 20
    time_budget: int = 120
    search_engine: str = "duckduckgo"

class TaskResponse(BaseModel):
    task_id: str
    status: str
    question: str
    created_at: str

# In-memory task storage (replace with DB in production)
tasks: dict[str, dict] = {}

# Task queue
task_queue = asyncio.Queue()
active_tasks: set[str] = set()
MAX_CONCURRENT_TASKS = 5

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    """Create a new research task."""
    task_id = str(uuid.uuid4())

    task_record = {
        "id": task_id,
        "question": task.question,
        "seed_url": task.seed_url,
        "max_depth": task.max_depth,
        "max_pages": task.max_pages,
        "time_budget": task.time_budget,
        "search_engine": task.search_engine,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "answer": None,
        "citations": [],
        "error": None
    }

    tasks[task_id] = task_record
    await task_queue.put(task_id)

    return TaskResponse(
        task_id=task_id,
        status="queued",
        question=task.question,
        created_at=task_record["created_at"]
    )

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task status and results."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return tasks[task_id]

@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    if task["status"] in ["completed", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Task already {task['status']}")

    task["status"] = "cancelled"
    return {"message": "Task cancelled"}

@app.websocket("/api/tasks/{task_id}/stream")
async def task_stream(websocket: WebSocket, task_id: str):
    """Stream real-time updates for a task."""
    await websocket.accept()

    if task_id not in tasks:
        await websocket.send_json({"type": "error", "error": "Task not found"})
        await websocket.close()
        return

    try:
        # Execute task with WebSocket callback
        task_record = tasks[task_id]
        task_record["status"] = "running"
        active_tasks.add(task_id)

        try:
            result = await execute_research_task(
                question=task_record["question"],
                seed_url=task_record.get("seed_url"),
                max_depth=task_record["max_depth"],
                max_pages=task_record["max_pages"],
                time_budget=task_record["time_budget"],
                websocket=websocket
            )

            task_record["answer"] = result["answer"]
            task_record["citations"] = result["citations"]
            task_record["confidence"] = result["confidence"]
            task_record["status"] = "completed"
            task_record["completed_at"] = datetime.utcnow().isoformat()

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            task_record["error"] = str(e)
            task_record["status"] = "failed"
            await websocket.send_json({"type": "agent:error", "error": str(e)})

        finally:
            active_tasks.discard(task_id)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for task {task_id}")
        active_tasks.discard(task_id)

# Task processor (background worker)
async def process_task_queue():
    """Background worker to process queued tasks."""
    while True:
        # Wait for available slot
        while len(active_tasks) >= MAX_CONCURRENT_TASKS:
            await asyncio.sleep(1)

        # Get next task
        task_id = await task_queue.get()

        if task_id in tasks and tasks[task_id]["status"] == "queued":
            # Task will be executed when WebSocket connects
            logger.info(f"Task {task_id} ready for execution")

@app.on_event("startup")
async def startup_event():
    """Start background task processor."""
    asyncio.create_task(process_task_queue())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Frontend Implementation (TanStack Start)

### Logging (TypeScript, Pino)

Use Pino for structured logs; Pretty transport in development for readable console output. Optional file logging inside container when `LOG_TARGET` includes `file`.

Environment (.env used by frontend):

```
LOG_LEVEL=info
LOG_TARGET=console   # console | file | both
LOG_FILE=logs/frontend.log
```

Pino initialization (e.g., `app/lib/logger.ts`):

```ts
import pino from 'pino'

const LOG_LEVEL = (import.meta.env?.LOG_LEVEL ?? process.env.LOG_LEVEL ?? 'info') as pino.LevelWithSilent
const LOG_TARGET = (import.meta.env?.LOG_TARGET ?? process.env.LOG_TARGET ?? 'console')
const LOG_FILE = import.meta.env?.LOG_FILE ?? process.env.LOG_FILE ?? 'logs/frontend.log'

const isDev = process.env.NODE_ENV !== 'production'

const targets: any[] = []

if (isDev && LOG_TARGET !== 'file') {
  targets.push({
    target: 'pino-pretty',
    options: { colorize: true, singleLine: false, translateTime: 'SYS:standard' },
    level: LOG_LEVEL,
  })
}

if (LOG_TARGET === 'file' || LOG_TARGET === 'both') {
  targets.push({
    target: 'pino/file',
    options: { destination: LOG_FILE, mkdir: true },
    level: LOG_LEVEL,
  })
}

export const logger = pino({ level: LOG_LEVEL }, targets.length ? pino.transport({ targets }) : undefined)
```

### API Client

```typescript
// app/lib/api-client.ts
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export interface TaskCreate {
  question: string;
  seed_url?: string;
  max_depth?: number;
  max_pages?: number;
  time_budget?: number;
  search_engine?: string;
}

export interface Task {
  id: string;
  question: string;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  answer?: string;
  citations?: Citation[];
  confidence?: number;
  created_at: string;
  completed_at?: string;
  error?: string;
}

export interface Citation {
  url: string;
  title: string;
  snippet: string;
}

export interface AgentEvent {
  type:
    | "agent:thinking"
    | "agent:tool_call"
    | "agent:tool_result"
    | "agent:screenshot"
    | "agent:complete"
    | "agent:error";
  timestamp: string;
  [key: string]: any;
}

export class ApiClient {
  async createTask(task: TaskCreate): Promise<Task> {
    const response = await fetch(`${API_URL}/api/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(task),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getTask(taskId: string): Promise<Task> {
    const response = await fetch(`${API_URL}/api/tasks/${taskId}`);

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async cancelTask(taskId: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/tasks/${taskId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
  }

  connectTaskStream(
    taskId: string,
    onEvent: (event: AgentEvent) => void
  ): WebSocket {
    const ws = new WebSocket(`${WS_URL}/api/tasks/${taskId}/stream`);

    ws.onmessage = (message) => {
      const event = JSON.parse(message.data) as AgentEvent;
      onEvent(event);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket closed");
    };

    return ws;
  }
}

export const apiClient = new ApiClient();
```

### Task Submission Component

```typescript
// app/components/TaskForm.tsx
import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { apiClient } from "../lib/api-client";

export function TaskForm() {
  const [question, setQuestion] = useState("");
  const [seedUrl, setSeedUrl] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [maxDepth, setMaxDepth] = useState(3);
  const [maxPages, setMaxPages] = useState(20);
  const [timeBudget, setTimeBudget] = useState(120);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const task = await apiClient.createTask({
        question,
        seed_url: seedUrl || undefined,
        max_depth: maxDepth,
        max_pages: maxPages,
        time_budget: timeBudget,
      });

      // Navigate to task detail page
      navigate({ to: `/tasks/${task.id}` });
    } catch (error) {
      console.error("Failed to create task:", error);
      alert("Failed to submit question. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="question" className="block text-sm font-medium mb-2">
          Your Question
        </label>
        <textarea
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What would you like to know?"
          required
          rows={3}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="seedUrl" className="block text-sm font-medium mb-2">
          Starting URL (optional)
        </label>
        <input
          id="seedUrl"
          type="url"
          value={seedUrl}
          onChange={(e) => setSeedUrl(e.target.value)}
          placeholder="https://example.com"
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />
        <p className="text-xs text-gray-500 mt-1">
          Leave empty to start with a web search
        </p>
      </div>

      <button
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-sm text-blue-600 hover:underline"
      >
        {showAdvanced ? "Hide" : "Show"} Advanced Options
      </button>

      {showAdvanced && (
        <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
          <div>
            <label className="block text-sm font-medium mb-1">
              Max Link Depth: {maxDepth === 0 ? "Unlimited" : maxDepth}
            </label>
            <input
              type="range"
              min="0"
              max="10"
              value={maxDepth}
              onChange={(e) => setMaxDepth(Number(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Max Pages: {maxPages === 0 ? "Unlimited" : maxPages}
            </label>
            <input
              type="range"
              min="0"
              max="50"
              step="5"
              value={maxPages}
              onChange={(e) => setMaxPages(Number(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Time Budget: {timeBudget}s
            </label>
            <input
              type="range"
              min="30"
              max="600"
              step="30"
              value={timeBudget}
              onChange={(e) => setTimeBudget(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={isSubmitting || !question.trim()}
        className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {isSubmitting ? "Submitting..." : "Ask Question"}
      </button>
    </form>
  );
}
```

### Task Detail Page with Live Updates

```typescript
// app/routes/tasks.$id.tsx
import { useState, useEffect, useRef } from "react";
import { useParams } from "@tanstack/react-router";
import { apiClient, type AgentEvent, type Task } from "../lib/api-client";

export default function TaskDetail() {
  const { id } = useParams();
  const [task, setTask] = useState<Task | null>(null);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Fetch initial task data
    apiClient.getTask(id).then(setTask);

    // Connect to WebSocket for live updates
    const ws = apiClient.connectTaskStream(id, (event) => {
      setEvents((prev) => [...prev, event]);

      // Update task status
      if (event.type === "agent:complete") {
        setTask((prev) =>
          prev
            ? {
                ...prev,
                status: "completed",
                answer: event.answer,
                citations: event.citations,
                confidence: event.confidence,
              }
            : null
        );
      }

      // Update screenshot
      if (event.type === "agent:screenshot") {
        setScreenshot(event.image);
      }

      // Handle errors
      if (event.type === "agent:error") {
        setTask((prev) =>
          prev
            ? {
                ...prev,
                status: "failed",
                error: event.error,
              }
            : null
        );
      }
    });

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [id]);

  const handleCancel = async () => {
    try {
      await apiClient.cancelTask(id);
      setTask((prev) => (prev ? { ...prev, status: "cancelled" } : null));
    } catch (error) {
      console.error("Failed to cancel task:", error);
    }
  };

  if (!task) {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left column: Events and logs */}
        <div>
          <div className="mb-4">
            <h1 className="text-2xl font-bold mb-2">{task.question}</h1>
            <div className="flex items-center gap-2">
              <span
                className={`px-3 py-1 rounded-full text-sm ${
                  task.status === "completed"
                    ? "bg-green-100 text-green-800"
                    : task.status === "running"
                    ? "bg-blue-100 text-blue-800"
                    : task.status === "failed"
                    ? "bg-red-100 text-red-800"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {task.status}
              </span>

              {task.status === "running" && (
                <button
                  onClick={handleCancel}
                  className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4 h-96 overflow-y-auto">
            <h2 className="font-semibold mb-2">Activity Log</h2>
            <div className="space-y-2">
              {events.map((event, i) => (
                <div key={i} className="text-sm">
                  <span className="text-gray-500 text-xs">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>{" "}
                  <span className="font-medium">
                    {event.type.replace("agent:", "")}:
                  </span>{" "}
                  {event.content ||
                    event.tool ||
                    JSON.stringify(event).slice(0, 100)}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column: Screenshot and results */}
        <div>
          {screenshot && (
            <div className="mb-4">
              <h2 className="font-semibold mb-2">Current Page</h2>
              <img
                src={screenshot}
                alt="Browser screenshot"
                className="w-full rounded-lg border"
              />
            </div>
          )}

          {task.answer && (
            <div className="bg-white rounded-lg border p-4">
              <h2 className="font-semibold mb-2">Answer</h2>
              <p className="whitespace-pre-wrap">{task.answer}</p>

              {task.citations && task.citations.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">Sources</h3>
                  <ul className="space-y-2">
                    {task.citations.map((citation, i) => (
                      <li key={i} className="text-sm">
                        <a
                          href={citation.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          {citation.title}
                        </a>
                        <p className="text-gray-600 text-xs mt-1">
                          {citation.snippet}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {task.confidence !== undefined && (
                <div className="mt-4">
                  <span className="text-sm text-gray-600">
                    Confidence: {(task.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

## Docker Compose Configuration

All services should consume a single shared root `.env` using `env_file`. Prefer environment variables to hardcoding values.

Example (excerpt):

```yaml
services:
  backend:
    env_file:
      - ../.env
    environment:
      LOG_FILE: ${LOG_FILE:-logs/backend.log}
```

```yaml
version: "3.8"

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000
    depends_on:
      - backend
    networks:
      - web-reader-net

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - LANGCHAIN_HOST=langchain
      - OLLAMA_HOST=ollama
      - OLLAMA_PORT=11434
      - FASTMCP_HOST=fastmcp
      - FASTMCP_PORT=3000
    depends_on:
      - langchain
      - ollama
      - fastmcp
    networks:
      - web-reader-net
    volumes:
      - ./config:/app/config:ro

  langchain:
    build:
      context: ./langchain
      dockerfile: Dockerfile
    environment:
      - OLLAMA_HOST=ollama
      - OLLAMA_PORT=11434
      - FASTMCP_HOST=fastmcp
      - FASTMCP_PORT=3000
    networks:
      - web-reader-net

  fastmcp:
    build:
      context: ./fastmcp
      dockerfile: Dockerfile
    environment:
      - PLAYWRIGHT_HOST=playwright
  - PLAYWRIGHT_PORT=3002
      - MCP_SERVER_PORT=3000
    depends_on:
      - playwright
    networks:
      - web-reader-net
    volumes:
      - ./config:/app/config:rw

  playwright:
    image: mcr.microsoft.com/playwright:v1.56.0-noble
    command: ["sleep", "infinity"]
    networks:
      - web-reader-net
    shm_size: 2gb

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - web-reader-net
    environment:
      - OLLAMA_HOST=0.0.0.0

networks:
  web-reader-net:
    driver: bridge

volumes:
  ollama-data:
```

## Testing Strategy

### Unit Tests (pytest)

```python
# tests/test_rate_limiting.py
import pytest
import asyncio
from fastmcp.rate_limiting import enforce_rate_limit

@pytest.mark.asyncio
async def test_rate_limit_enforcement():
    """Test that rate limiting enforces 5 requests per 90 seconds."""
    domain = "example.com"

    # First 5 requests should be fast (with delays)
    start = time.time()
    for i in range(5):
        await enforce_rate_limit(domain)
    duration = time.time() - start

    # Should take at least 40 seconds (4 delays of 10-20s each)
    assert duration >= 40, "Rate limiting delays not enforced"

    # 6th request should wait for window to reset
    start = time.time()
    await enforce_rate_limit(domain)
    duration = time.time() - start

    assert duration >= 45, "Rate limit window not enforced"

# tests/test_domain_filtering.py
def test_domain_filtering():
    """Test domain allow/deny list filtering."""
    from fastmcp.domain_filtering import is_domain_allowed

    # Test deny list
    assert not is_domain_allowed("http://blocked.com")

    # Test wildcard deny
    assert not is_domain_allowed("http://malware.bad-site.com")

    # Test allow list
    assert is_domain_allowed("http://allowed.com")

    # Test domain not in allow list (if allow list exists)
    assert not is_domain_allowed("http://random.com")
```

### Integration Tests

```python
# tests/integration/test_research_workflow.py
import pytest
from backend.tasks import execute_research_task

@pytest.mark.asyncio
@pytest.mark.integration
async def test_simple_research_workflow():
    """Test end-to-end research workflow."""
    result = await execute_research_task(
        question="What is the capital of France?",
        seed_url=None,
        max_depth=1,
        max_pages=3,
        time_budget=60
    )

    assert result["answer"]
    assert "Paris" in result["answer"]
    assert len(result["citations"]) > 0
    assert result["confidence"] > 0.5
```

## Configuration Files

### Domain Lists

```
# config/disallowed-domains.txt
*.malware-site.com
*.phishing-*.com
example-blocked.com
```

```
# config/allowed-domains.txt
# Empty = allow all (except disallowed)
# If populated, only these domains allowed:
wikipedia.org
*.wikipedia.org
duckduckgo.com
```

### User Agent Pool

```python
# config/user_agents.py
USER_AGENT_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]
```

---

**Document Version**: 1.1  
**Last Updated**: November 14, 2025  
**Status**: Implementation Guide (flexible test execution)
