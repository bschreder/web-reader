# Contributing Guide

Concise standards for contributing code to Web Reader. For deep architectural details see `requirements.md` and `implementation.md`; for assistant workflow see `copilot-instructions.md`.

## Principles

- Small, focused changes; prefer incremental PRs.
- No hardcoded config/secrets; use root `.env` and `config/` files.
- Deterministic builds (Poetry lock / package-lock.json).
- Code must be readable without explanatory comments (use clear naming).
- Comments explain "why", not obvious "what".
- Structured error responses instead of uncaught exceptions.

## Python Style (Backend, LangChain, FastMCP)

- Follow PEP 8; 120 char soft line limit.
- Use type hints everywhere (functions, class attributes); avoid `any`
- Async I/O: public service entrypoints and tool functions use `async def`.
- Logging via Loguru: structured context (`extra={}`) and avoid sensitive values (tokens, emails, full query params).
- Return structured dicts for tool/service results: `{"status": "success", "data": ...}` or `{"status": "error", "error": str(e), "recoverable": bool}`.
- Keep module top-level light (no heavy initialization or network calls).
- Prefer list/dict comprehensions where clearer; avoid over-nesting.
- Use Pydantic models for external input validation.

## TypeScript Style (Frontend)

- `strict` mode; avoid `any`; if dynamic use type guards.
- ESM imports; type-only imports (`import type { ... }`).
- Functional React components; hooks only at top level; no side effects in render.
- Centralize API calls in a client module; use `async/await` rather than `.then` chains.
- Use path alias `~/*` for non-local imports.
- Logging via Pino (Pretty in dev, file when `LOG_TARGET` includes `file`).
- WebSocket handlers must be resilient: reconnection with capped exponential backoff.
- Avoid leaking PII in logs or UI state.

## Testing

- Minimum coverage target: >80% statements/branches/functions per service (enforced via reporting, not hard fail yet).
- Write tests nearest to change: unit first, then integration if cross-boundary, then E2E if user-visible.
- Python: pytest + `pytest.mark.asyncio` for async tests; use `unittest.mock` over monkeypatch for clarity.
- Frontend: Vitest (node) for logic; Vitest Browser mode for interactive component behavior; Playwright for full E2E.
- Avoid brittle selectors in E2E tests; prefer `data-testid` attributes.
- Structure test output artifacts under `<service>/coverage/`.

## Logging & Observability

- Respect `.env` keys: `LOG_LEVEL`, `LOG_TARGET`, `LOG_FILE`.
- Include task or trace identifiers (`task_id`, `trace_id`) to correlate multi-service flows.
- Redact sensitive substrings (regex for email, token patterns) before logging.
- Avoid multi-line log messages; prefer structured fields.

## Environment & Configuration

- Single root `.env` powers all containers; replicate new keys into `.env.example` with comments.
- Never duplicate config into code constants; import via existing config helpers.
- Domain allow/deny lists live in `config/allowed-domains.txt` and `config/disallowed-domains.txt` (one per line; wildcards allowed).

## Browser Automation Ethics

- Enforce rate limit (5 requests / 90s / domain + 10–20s delay) before navigation or interaction.
- Fresh Playwright context per task (no cookie/local/session storage reuse).
- Respect `robots.txt` when `RESPECT_ROBOTS_TXT=true`.

## PR Checklist

Before opening a PR:

1. Code follows style guidelines (Python/TS) and passes lint (if configured).
2. Added/updated tests relevant to changes; coverage unaffected or improved.
3. No secrets or hardcoded environment values introduced.
4. New env vars documented in `.env.example` and referenced in service config.
5. Logs do not include sensitive values; added trace/task IDs where appropriate.
6. Updated documentation (README, service README, or this guide) if behavior or public API changed.
7. Verified dev hot reload still works (no blocking init code).
8. Confirmed structured success/error responses from new tools/functions.

## Commit Conventions

Format (recommended, not enforced):

`<scope>: <short imperative summary>`

Examples:

- `frontend: add websocket reconnection backoff`
- `fastmcp: enforce rate limit in navigate_to`
- `langchain: add citation extraction util`

## Dependency Changes

- Python: add to `pyproject.toml`; avoid pinning unless necessary for reproducibility; run `poetry lock`.
- Node: use `npm install <pkg>`; do not commit unused dependencies; prefer micro-libraries for specific needs.
- After adding dependencies in Docker context, ensure both `dev` and `prod` stages updated if required at runtime.

## Security & Privacy

- No PII in logs or artifacts; sanitize scraped content before persisting.
- Validate URLs (http/https only) and strip fragments before navigation.
- Handle 4xx/5xx gracefully: return structured error with `recoverable` flag where retries make sense.

## Performance Considerations

- Avoid unnecessary screenshot captures (limit to significant steps); large images inflate artifact storage.
- Cap extracted text length (e.g., 10k chars) to prevent token explosion in LLM prompts.
- Reuse HTTP clients and avoid creating new connections per request in Python.

## When to Refactor

- Duplicate logic across services (e.g., rate limiting) → centralize in one module and import.
- Excessive branching or deeply nested conditionals → extract helper functions.
- Growing test setup complexity → introduce fixtures/factories.

## Links

- Requirements: `./requirements.md`
- Implementation: `./implementation.md`
- Use Cases: `./use-case.md`
- Project Plan: `./project-plan.md`
- Assistant Guide: `./copilot-instructions.md`
- FastMCP: `../fastmcp/README.md`
- LangChain: `../langchain/README.md`
- Backend: `../backend/README.md`
- Frontend: `../frontend/README.md`

---

Document version: 1.0  
Last updated: 2025-11-22
