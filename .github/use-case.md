# Web Reader – Use Cases

This document defines concrete use cases for the LLM-driven, deidentified browser system using MCP + FastMCP + Playwright + Ollama + LangChain orchestration with a TanStack Start frontend.

## System Assumptions

- **Deidentified browsing**: Fresh Playwright browser context per task, no prior cookies/session, tracking prevention enabled, randomized user agent, no logged-in state by default, no PII in requests, optional egress proxy, and redaction of sensitive fields in logs.
- **Bot protection**: Randomized delays between requests (max 5 requests per 90 seconds, 10-20 second intervals), human-like interaction patterns, rotating user agents.
- **Default search engine**: DuckDuckGo (web search). Can be overridden per task.
- **Max link depth**: default 3; 0 means unlimited.
- **Max total requests**: default 20; 0 means unlimited.
- **Domain filtering**: Allow/disallow lists persisted to configuration files, checked before each navigation.
- **System returns**: Citations (URLs), page snippets, and optional screenshots.

## UC-01: Question → Web Search → Answer (Depth-limited)

Goal

- Answer a user’s question by performing a deidentified web search, scanning results, and optionally opening result links up to a maximum link depth.

Actors

- User (via TanStack Start UI)
- LangChain Agent (orchestrator)
- FastMCP Browser Tooling + Playwright

Preconditions

- Playwright container reachable
- Search engine accessible (DuckDuckGo default)

Parameters

- query: string (required)
- search_engine: enum [duckduckgo, bing, google, custom] (default: duckduckgo)
- max_link_depth: int (default: 3; 0 = unlimited)
- max_results: int (default: 10)
- time_budget_sec: int (default: 120)
- safe_mode: boolean (default: true) – avoid adult/unsafe results

Main Flow

1. Create a fresh browser context (no cookies/storage).
2. Navigate to search engine with the query.
3. Parse SERP: titles, snippets, URLs, and metadata.
4. If the answer appears directly in snippets, synthesize and return with citations.
5. Otherwise, iteratively open result links in priority order (top-N, dedup by domain).
6. For each page, extract structured content (title, headings, main text) and detect answer candidates.
7. Respect max_link_depth: follow intra-page relevant links if needed.
8. Stop when confidence threshold reached, time budget exhausted, or depth limit met.
9. Generate final answer with citations and supporting snippets; attach screenshots optionally.

Alternative Flows

- A1: Query rewrite: If SERP is low-signal, reformulate the query (e.g., add site/domain or keywords) and retry once.
- A2: Multi-engine fanout: Issue parallel searches across two engines and merge results.

Errors/Exceptions

- E1: Network errors/timeouts → retry with backoff; degrade to partial results.
- E2: CAPTCHA or bot detection → pause, reduce concurrency, change UA; surface "manual verification required" state.
- E3: Empty or low-quality SERP → suggest refining the question.

Postconditions

- Answer text with confidence score, citations (URLs), and optional evidence snippets/screenshots persisted in task record.

Metrics/Acceptance

- Finds at least one relevant citation in < 30s for common queries.
- Produces grounded answers (each claim traceable to a cited page).

## UC-02: Question → Seed URL → Linked Reading

Goal

- Answer a question by starting from a specific user-provided URL and following links as needed (within a depth budget) to gather evidence.

Actors

- User, LangChain Agent, Browser subsystem

Preconditions

- Seed URL accessible; no login required unless explicitly allowed.

Parameters

- query: string (required)
- seed_url: string (required)
- max_link_depth: int (default: 3; 0 = unlimited)
- same_domain_only: boolean (default: false)
- allow_external_links: boolean (default: true)
- time_budget_sec: int (default: 90)

Main Flow

1. New deidentified browser context.
2. Navigate to seed_url and extract main content.
3. Attempt to answer directly from the page.
4. If insufficient, follow relevant links (respecting same_domain_only and depth budget).
5. Aggregate evidence across visited pages; deduplicate content.
6. Synthesize an answer with citations.

Alternative Flows

- A1: If page is an index/table of contents, build a prioritized crawl plan (headings/anchors first).
- A2: If seed page blocks automation, switch to fetch+render fallback (HTML-only) or summarize cached copy (if available).

Errors/Exceptions

- E1: 404 Not Found → report URL not found; suggest checking the URL or searching for the topic instead.
- E2: 403/401 → if auth disallowed, stop and report; if allowed, invoke secure credential workflow.
- E3: Infinite link loops → detect cycles and enforce per-domain/page visit caps.
- E4: Heavy JS sites → enable wait-for-networkidle and increase timeouts; fall back to text-only extraction.

Postconditions

- Consolidated answer with citations drawn from the seed page and any followed links.

Metrics/Acceptance

- Completes within time and depth budgets while maintaining answer quality and traceability.

## UC-03: Rate Limits, Budgets, and Guardrails (Operational)

Goal

- Ensure safe, predictable operation under constraints while avoiding bot detection.

Parameters

- max_pages: int per task (default: 20)
- max_concurrent_tabs: int (default: 1 for bot protection)
- robots_txt_respect: boolean (default: true)
- disallowed_domains: list (persisted to config/disallowed-domains.txt)
- allowed_domains: list (persisted to config/allowed-domains.txt)
- request_rate_limit: max 5 requests per 90 seconds
- request_delay_range: 10-20 seconds between requests (randomized)

Flow

1. Load allowed/disallowed domain lists from configuration files at startup.
2. Before each navigation:
   - Check domain against allow/deny lists
   - Verify robots.txt compliance if enabled
   - Enforce rate limiting (max 5 requests per 90 seconds)
   - Apply randomized delay (10-20 seconds) since last request
3. Track and enforce visit, time, and concurrency budgets.
4. Handle 429 (Too Many Requests) responses:
   - Parse Retry-After header if present
   - Apply exponential backoff (double delay, max 5 minutes)
   - Surface warning to user if repeated 429s occur
5. Bot detection countermeasures:
   - Rotate user agents between requests
   - Randomize viewport sizes
   - Simulate human-like mouse movements and scrolling
   - Add random pauses during page interactions
6. Stop gracefully with partial results if limits exceeded.
7. Save updated allow/deny lists back to files if modified during runtime.

Errors

- E1: Domain blocked → report blocked domain with reason (allow/deny list or robots.txt).
- E2: 429 Too Many Requests → backoff and retry; report if persistent.
- E3: Rate limit exceeded → pause task and wait for rate limit window to reset.
- E4: Hard stop with clear explanation and partial artifacts when limits trigger.

Acceptance

- No more than 5 requests in any 90-second window.
- Minimum 10 seconds, maximum 20 seconds between consecutive requests.
- Domain lists persist across sessions and can be updated via config files.

- E4: Hard stop with clear explanation and partial artifacts when limits trigger.

Acceptance

- No more than 5 requests in any 90-second window.
- Minimum 10 seconds, maximum 20 seconds between consecutive requests.
- Domain lists persist across sessions and can be updated via config files.

## UC-04: Error Handling and Recovery Scenarios

Scenarios

- S1: CAPTCHA/Bot challenge → backoff, slower actions, different UA; escalate to manual review.
- S2: Selector not found → retry with fuzzy selector or heuristic re-locate; capture DOM snapshot.
- S3: Page content empty → JS-heavy; increase wait, run evaluate() to extract text, or fallback to HTML-only.
- S4: Network flakiness → retry with exponential backoff; switch DNS/egress if supported.
- S5: Malformed HTML → use robust parser and sanitization; skip broken nodes.

Outputs

- Structured error objects, retry counts, and snapshots for debugging.

## UC-05: Accessibility-Aware Extraction (Feature)

Goal

- Prefer accessible content by leveraging the accessibility tree and ARIA roles.

Flow

1. Fetch accessibility tree for the page.
2. Bias extraction toward labeled/semantic elements.
3. Improve robustness on complex, interactive UIs.

Acceptance

- Higher extraction accuracy on dynamic apps; fewer selector failures.

## UC-06: Safe Execution Sandbox for Custom JS (Feature)

Goal

- Allow controlled evaluation of custom JavaScript for extraction when needed.

Constraints

- Strict time and memory limits; allowlist exposed globals.
- No network from within the sandbox.

Acceptance

- JS helpers can run without compromising security or stability.

---

## Future Enhancements

### UC-FUTURE-01: RAG-Accelerated Search (Vector DB)

Goal

- Use local vector search over previously scraped content to answer faster; only browse when needed.

**Note**: This requires committing to a vector database solution (ChromaDB or Qdrant).

Flow

1. Generate embedding for the user query.
2. Search vector DB (recent content, within TTL).
3. If sufficient confidence, answer from local corpus with citations to stored pages.
4. If not, fall back to UC-01/02 browsing; store new pages back into vector DB.

Acceptance

- Reduces external browsing for repeated/related queries; preserves answer quality.

Benefits

- Faster responses for related queries
- Lower bandwidth usage
- Better context retention across sessions
- Semantic search across historical data

Tradeoffs

- Additional infrastructure (vector DB container)
- Storage requirements for embeddings
- Maintenance of embedding model and collections
- Complexity in cache invalidation logic

### UC-FUTURE-02: Caching and Idempotency

Goal

- Avoid redundant work for repeated queries and pages.

Flow

1. Hash (normalized) URLs and store normalized content + metadata.
2. On revisit within TTL, use cached content unless forced refresh.
3. Expose cache status in results.

Acceptance

- Reduced browsing time for repeated tasks; correctness preserved.

Implementation Notes

- Can be implemented with simple file-based cache initially
- Can upgrade to vector DB when UC-FUTURE-01 is implemented
- Consider using Redis or similar for distributed caching
