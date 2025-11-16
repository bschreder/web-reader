# FastMCP Browser Automation Server

FastMCP server providing browser automation tools via the Model Context Protocol (MCP).

## Features

- **Browser Automation Tools**:

  - `navigate_to`: Navigate to URLs with automatic protocol normalization
  - `get_page_content`: Extract visible text content from pages
  - `take_screenshot`: Capture page screenshots

- **Privacy & Ethics**:

  - Deidentified browser contexts (no cookies, storage, history)
  - Randomized user agents
  - Domain filtering (allow/deny lists)
  - Rate limiting (5 requests per 90 seconds per domain)

- **Architecture**:
  - Connects to remote Playwright server (Docker)
  - Falls back to local browser for development

## Quick Start

### Prerequisites

- Python 3.13+
- Playwright server running (or local fallback)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For local development (installs browsers)
playwright install chromium
```

### Configuration

Create `.env` file (or use environment variables):

```bash
# Playwright Connection
PLAYWRIGHT_HOST=playwright
PLAYWRIGHT_PORT=3002

# Rate Limiting
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=90
REQUEST_DELAY_MIN=10
REQUEST_DELAY_MAX=20

# Logging
LOG_LEVEL=info
LOG_TARGET=console
```

### Running

```bash
# Start FastMCP server
python server.py

# Server listens on stdio for MCP protocol
```

### Docker

```bash
# Build image
docker build -t web-reader-fastmcp .

# Run container
docker run -it \
  -e PLAYWRIGHT_HOST=playwright \
  -e PLAYWRIGHT_PORT=3002 \
  web-reader-fastmcp
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=server --cov-report=html

# Run specific test file
pytest tests/test_domain_filtering.py

# Run integration tests
pytest -m integration
```

## Architecture

### Connection Flow

```
LangChain Agent
      ↓
  MCP Protocol
      ↓
 FastMCP Server (this)
      ↓
  ws://playwright:3002
      ↓
Playwright Server (Docker)
      ↓
  Chromium Browser
```

### Tools

#### `navigate_to(url, wait_until)`

Navigate to a URL.

**Arguments**:

- `url` (str): Target URL (protocol optional, http→https conversion)
- `wait_until` (str): Load event (`load`, `domcontentloaded`, `networkidle`)

**Returns**:

```json
{
  "status": "success",
  "title": "Page Title",
  "url": "https://example.com",
  "http_status": 200
}
```

#### `get_page_content()`

Extract visible text content from current page.

**Returns**:

```json
{
  "status": "success",
  "text": "Visible text content...",
  "char_count": 1234
}
```

**Note**: Content truncated at 10,000 characters.

#### `take_screenshot(full_page)`

Capture screenshot of current page.

**Arguments**:

- `full_page` (bool): Capture full scrollable page (default: False)

**Returns**:

```json
{
  "status": "success",
  "image": "base64_encoded_png...",
  "format": "png"
}
```

## Rate Limiting

Per-domain rate limiting enforces ethical scraping:

- **Limit**: 5 requests per 90 seconds per domain
- **Delays**: 10-20 seconds randomized between requests
- **Enforcement**: Automatic backoff on 429 responses

### Example

```python
# First 5 requests to example.com: allowed (with delays)
await navigate_to("https://example.com/page1")  # No delay
await navigate_to("https://example.com/page2")  # 10-20s delay
await navigate_to("https://example.com/page3")  # 10-20s delay
await navigate_to("https://example.com/page4")  # 10-20s delay
await navigate_to("https://example.com/page5")  # 10-20s delay

# 6th request: waits for window reset (~90s)
await navigate_to("https://example.com/page6")  # Waits for window

# Requests to other domains: independent limits
await navigate_to("https://other.com/page1")    # No delay (different domain)
```

## Domain Filtering

Control allowed/blocked domains via config files:

### Allow List (`config/allowed-domains.txt`)

```
# Allowed domains (empty = allow all except disallowed)
example.com
*.research-site.edu
```

### Deny List (`config/disallowed-domains.txt`)

```
# Blocked domains
*.blocked.com
malicious-site.com
```

**Wildcard Support**: Use `*.domain.com` to match all subdomains.

**Precedence**: Deny list overrides allow list.

## URL Normalization

URLs are automatically normalized:

- **No protocol**: `example.com` → `https://example.com`
- **HTTP to HTTPS**: `http://example.com` → `https://example.com`
- **Preserves paths/query**: `example.com/path?q=1` → `https://example.com/path?q=1`

## Logging

Structured logging with Loguru:

```python
# Log levels: debug, info, warning, error, critical
LOG_LEVEL=info

# Output targets: console, file, both
LOG_TARGET=console

# File path (when LOG_TARGET=file or both)
LOG_FILE=logs/fastmcp.log
```

**Log Format**:

```
2025-01-31 12:34:56 [INFO] Connecting to remote Playwright server at ws://playwright:3002
2025-01-31 12:34:57 [INFO] Connected to remote Playwright server successfully
2025-01-31 12:35:00 [INFO] Normalized URL: http://example.com -> https://example.com
2025-01-31 12:35:01 [INFO] Successfully navigated to https://example.com (200)
```

## Error Handling

All tools return structured responses:

### Success Response

```json
{
  "status": "success",
  "data": {...}
}
```

### Error Response

```json
{
  "status": "error",
  "error": "Human-readable error message",
  "recoverable": true
}
```

### Common Errors

- **Domain blocked**: Domain in deny list or not in allow list
- **Rate limit**: Exceeded 5 requests/90s for domain
- **Timeout**: Page load exceeded 30 seconds
- **HTTP error**: Status code >= 400
- **No page**: Tool called before navigation

## Development

### Local Testing

```bash
# Start local Playwright server
npx playwright run-server --port 3002

# Run FastMCP server (connects to local)
PLAYWRIGHT_HOST=localhost PLAYWRIGHT_PORT=3002 python server.py
```

### Adding Tests

```python
# tests/test_new_feature.py
import pytest
from server import new_function

class TestNewFeature:
    @pytest.mark.asyncio
    async def test_new_function(self):
        result = await new_function()
        assert result["status"] == "success"
```

### Code Style

- Type hints for all functions
- Docstrings with Args and Returns
- Structured error responses
- Comprehensive logging

## Troubleshooting

### Connection Errors

**Problem**: `Failed to connect to remote Playwright`

**Solutions**:

1. Verify Playwright server running: `docker ps | grep playwright`
2. Check network: `docker network inspect external-net`
3. Test connectivity: `curl ws://playwright:3002`

### Rate Limit Issues

**Problem**: Unexpected rate limiting

**Solutions**:

1. Check `_rate_limits` state (logged at DEBUG level)
2. Adjust `RATE_LIMIT_WINDOW` for testing
3. Clear rate limit cache: restart server

### Domain Filtering

**Problem**: Domain incorrectly blocked/allowed

**Solutions**:

1. Check wildcard syntax: `*.example.com` (not `*example.com`)
2. Verify file paths in logs
3. Test with `is_domain_allowed("https://example.com")`

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Playwright Python](https://playwright.dev/python/)

## License

MIT License - See LICENSE file for details
