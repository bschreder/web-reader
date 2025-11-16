# Web Reader

> AI-powered web research assistant that autonomously browses the web to answer your questions with cited, verifiable sources.

## 🎯 Overview

Web Reader is a production-ready system that combines large language models (LLMs) with automated web browsing to provide accurate, well-researched answers to natural language questions. It leverages:

- **LangChain** for agentic orchestration and reasoning
- **FastMCP + Playwright** for browser automation via Model Context Protocol
- **Ollama** for local LLM inference (privacy-preserving)
- **TanStack Start** for modern, responsive frontend
- **FastAPI** for robust backend API and WebSocket streaming

### Key Features

✅ **Natural Language Questions** - Ask questions in plain English  
✅ **Autonomous Research** - Agent navigates web, follows links, synthesizes information  
✅ **Source Attribution** - Every claim cited with URLs and snippets  
✅ **Real-time Monitoring** - Watch the agent work with live WebSocket updates  
✅ **Privacy-First** - Deidentified browsing with no tracking or PII exposure  
✅ **Rate Limiting** - Respectful web scraping with configurable limits  
✅ **Domain Filtering** - Allow/deny lists for controlled access  
✅ **Task History** - Review and export past research sessions

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (required)
- **Git** (required)
- **VS Code** with Dev Containers extension (recommended for development)

> **Note**: No local Python or Node.js installation required! Everything runs in containers.

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/web-reader.git
cd web-reader
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env to customize settings (optional - defaults work out of the box)
nano .env
```

### 3. Start External Services (Playwright, Ollama)

```bash
cd container
docker-compose up -d
```

This starts:

- **Playwright** browser automation (headless Chrome)
- **Ollama** LLM inference engine
- **Model-Loader** Pulls the LLM model
  To manually pull the default LLM model (qwen3:8b):

```bash
docker exec ollama ws-ollama pull qwen3:8b
```

### 4. Start Application Services

```bash
cd ../docker
docker-compose up -d
```

This starts:

- **Frontend** (TanStack Start) - http://localhost:3000
- **Backend API** (FastAPI) - http://localhost:5000
- **LangChain Orchestrator** - Internal service
- **FastMCP Server** - Internal service

### 5. Open Application

Open your browser to **http://localhost:3000** and start asking questions!

## 📋 Usage Examples

### Example 1: Simple Question

**Question**: "What is the capital of France?"

**Process**:

1. Agent searches DuckDuckGo
2. Parses search results
3. Visits top result (Wikipedia)
4. Extracts answer
5. Returns: "Paris" with citation

**Time**: ~15-30 seconds

### Example 2: Multi-Page Research

**Question**: "Compare the key features of React, Vue, and Svelte"

**Process**:

1. Searches for each framework
2. Visits official documentation
3. Follows links to feature pages
4. Synthesizes comparison table
5. Returns answer with 5-10 citations

**Time**: ~45-90 seconds

### Example 3: Seed URL Research

**Question**: "Summarize the latest features in Python 3.13"  
**Seed URL**: https://docs.python.org/3.13/whatsnew/

**Process**:

1. Navigates directly to seed URL
2. Extracts main content
3. Follows relevant links for details
4. Synthesizes summary
5. Returns answer with citations to official docs

**Time**: ~30-60 seconds

## 🏗️ Architecture

```
┌─────────────────────┐
│  Frontend (React)   │  ← User Interface
│  TanStack Start     │
└──────────┬──────────┘
           │ HTTP/WebSocket
┌──────────▼──────────┐
│  Backend API        │  ← Task Management
│  FastAPI            │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  LangChain          │  ← Agentic Orchestration
│  ReAct Agent        │
└─────┬────────────┬──┘
      │ MCP        │ HTTP
┌─────▼──────┐ ┌───▼────┐
│  FastMCP   │ │ Ollama │  ← LLM Inference
│  Browser   │ └────────┘
│  Tools     │
└─────┬──────┘
      │ Playwright API
┌─────▼──────────┐
│  Playwright    │  ← Headless Browser
│  (Chromium)    │
└────────────────┘
```

### Component Responsibilities

| Component       | Purpose                                 | Technology                    |
| --------------- | --------------------------------------- | ----------------------------- |
| **Frontend**    | User interface, real-time updates       | TanStack Start (React)        |
| **Backend API** | REST/WebSocket, task queue              | FastAPI (Python)              |
| **LangChain**   | Agent reasoning, memory, callbacks      | LangChain (Python)            |
| **FastMCP**     | Browser automation tools (MCP protocol) | FastMCP + Playwright (Python) |
| **Playwright**  | Headless browser execution              | Chromium (Docker)             |
| **Ollama**      | LLM inference                           | Ollama (Docker)               |

## ⚙️ Configuration

### Environment Variables

Key settings in `.env`:

```bash
# LLM Configuration
OLLAMA_MODEL=qwen3:8b           # Model to use
MAX_ITERATIONS=15               # Max agent steps

# Task Limits
MAX_CONCURRENT_TASKS=5          # Simultaneous tasks
MAX_PAGES=20                    # Pages per task
MAX_LINK_DEPTH=3                # Link following depth
TIME_BUDGET=120                 # Task timeout (seconds)

# Rate Limiting
RATE_LIMIT_REQUESTS=5           # Max requests per window
RATE_LIMIT_WINDOW=90            # Window duration (seconds)
REQUEST_DELAY_MIN=10            # Min delay between requests
REQUEST_DELAY_MAX=20            # Max delay between requests

# Logging
LOG_LEVEL=info                  # debug | info | warn | error
LOG_TARGET=console              # console | file | both
```

### Domain Filtering

**Allow List** (`config/allowed-domains.txt`):

- If **empty**: All domains allowed (except disallowed)
- If **populated**: Only these domains accessible

**Deny List** (`config/disallowed-domains.txt`):

- Always blocked, regardless of allow list

**Format**:

```
# One domain per line, wildcards supported
wikipedia.org
*.wikipedia.org
duckduckgo.com
```

### Supported LLM Models

Any Ollama model with **function calling** support:

```bash
# Pull alternative models
docker exec ollama ollama pull llama3.2
docker exec ollama ollama pull mistral
docker exec ollama ollama pull qwen2.5:14b

# Update .env
OLLAMA_MODEL=llama3.2
```

**Recommended models**:

- `qwen3:8b` - Best balance of speed and quality (default)
- `llama3.2` - Good general purpose
- `mistral` - Fast for simple queries
- `qwen2.5:14b` - Higher quality (requires more RAM)

## 🛠️ Development

### Using Dev Container (Recommended)

1. Install **VS Code** and **Dev Containers** extension
2. Open project in VS Code
3. Click "Reopen in Container" when prompted
4. Dev environment ready with Python 3.13 and Node.js 24!

### Manual Setup (Without Dev Container)

```bash
# Backend
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

### Monitoring Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# View logs directory (if LOG_TARGET=file or both)
tail -f logs/backend.log
```

## 📊 Performance & Limits

### Performance Targets

| Metric                | Target   | Notes                         |
| --------------------- | -------- | ----------------------------- |
| **Simple queries**    | < 60s    | Single search, 1-3 pages      |
| **Complex queries**   | < 120s   | Multiple searches, 5-10 pages |
| **Tool execution**    | < 5s avg | Per tool call                 |
| **WebSocket latency** | < 200ms  | Real-time updates             |
| **Success rate**      | > 95%    | For common queries            |

### Resource Usage

| Component      | CPU           | Memory    | Notes                                    |
| -------------- | ------------- | --------- | ---------------------------------------- |
| **Frontend**   | 0.1-0.5 cores | 100-200MB | Per instance                             |
| **Backend**    | 0.2-1.0 cores | 200-500MB | Depends on task queue                    |
| **LangChain**  | 0.5-2.0 cores | 500MB-1GB | Depends on model                         |
| **Ollama**     | 2-8 cores     | 4-16GB    | CPU-only; GPU recommended for production |
| **Playwright** | 0.5-2.0 cores | 500MB-2GB | Per browser context                      |

**Minimum recommended**: 4 CPU cores, 8GB RAM  
**Production recommended**: 8+ CPU cores, 16GB+ RAM, GPU for Ollama

### Rate Limiting (Default)

- **Max requests**: 5 per 90 seconds per domain
- **Delay between requests**: 10-20 seconds (randomized)
- **Concurrent browser contexts**: 5 max
- **429 handling**: Exponential backoff (max 5 minutes)

## 🔒 Security & Privacy

### Privacy Features

✅ **Fresh browser contexts** - No cookies, storage, or history between tasks  
✅ **Randomized user agents** - Pool of 10+ recent browser versions  
✅ **Tracking prevention** - Third-party cookies blocked, fingerprinting mitigated  
✅ **PII redaction** - Sensitive data removed from logs  
✅ **No personalization** - Deidentified browsing by design

### Security Measures

✅ **Input validation** - All user inputs validated and sanitized  
✅ **Output sanitization** - XSS prevention for scraped content  
✅ **Domain filtering** - Allow/deny lists for access control  
✅ **Resource limits** - Per-container CPU and memory limits  
✅ **Network isolation** - Services communicate via internal Docker network

### Compliance

✅ **robots.txt respect** - Enabled by default  
✅ **Rate limiting** - Prevents aggressive scraping  
✅ **User agent declaration** - Transparent identification  
✅ **Audit trails** - Complete navigation history logged

## 🐛 Troubleshooting

### Common Issues

**Issue**: Ollama model not found  
**Solution**: Pull model: `docker exec ollama ollama pull qwen3:8b`

**Issue**: Frontend can't connect to backend  
**Solution**: Check `VITE_API_URL` in `.env` matches backend port

**Issue**: Browser automation fails  
**Solution**: Ensure Playwright container running: `docker ps | grep playwright`

**Issue**: Slow responses  
**Solution**: Try smaller model (`mistral`) or reduce `MAX_PAGES` in `.env`

**Issue**: Rate limit errors  
**Solution**: Increase delays in `.env`: `REQUEST_DELAY_MIN=20`, `REQUEST_DELAY_MAX=30`

### Debug Mode

Enable debug logging:

```bash
# In .env
LOG_LEVEL=debug
LOG_TARGET=both

# Restart services
docker-compose restart
```

View detailed logs:

```bash
tail -f logs/backend.log logs/langchain.log logs/fastmcp.log
```

## 📚 Documentation

- **[Requirements](./. github/requirements.md)** - Detailed system requirements
- **[Use Cases](./.github/use-case.md)** - Practical usage scenarios
- **[Implementation](./.github/implementation.md)** - Technical implementation guide
- **[Project Plan](./.github/project-plan.md)** - Development roadmap
- **[Copilot Instructions](./.github/copilot-instructions.md)** - AI assistant context

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

[MIT License](LICENSE) - See LICENSE file for details

## 🙏 Acknowledgments

- **LangChain** - Agentic orchestration framework
- **FastMCP** - Model Context Protocol server
- **Playwright** - Browser automation
- **Ollama** - Local LLM inference
- **TanStack** - Modern React tooling
- **FastAPI** - Python web framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/web-reader/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/web-reader/discussions)
- **Documentation**: [.github/ folder](./.github/)

---

**Built with ❤️ for researchers, developers, and curious minds.**
