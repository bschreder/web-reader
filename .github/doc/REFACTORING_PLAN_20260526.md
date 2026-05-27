# Web Reader Monorepo Refactoring Plan (2026-05-26)

## Executive Summary

This repository should be refactored to a single, conventional polyglot monorepo with:

- One source of truth for environment variables.
- One Docker Compose entrypoint with profiles/overrides instead of split infra/app stacks.
- One developer command surface (single task runner + VS Code tasks that call it).
- One debug story that works the same way in local host and devcontainer.
- Python development remaining devcontainer-first (no local Python required).

Short answer to "can these be merged?": yes. They should be merged.

## Current Pain Points (Observed)

1. Duplicate orchestration layers.

- Root scripts, `container/` scripts, `docker/` compose files, and VS Code tasks all overlap.
- VS Code tasks reference `container/start.sh` and `container/stop.sh`, but only `.ps1` scripts exist there.

2. Configuration drift.

- `.env.example` uses API port `5000`, while many runtime defaults and docs use `8000`.
- FastMCP defaults vary between `3000` and `3100` depending on file.
- Hostnames differ by context (`localhost`, service names, `ws-playwright`, etc.).

3. Inconsistent docs and developer UX.

- Debug/test docs contain contradictory or malformed sections.
- Multiple ways to start the stack make onboarding and debugging unpredictable.

4. Debug attach inconsistency.

- `.vscode/launch.json` mixes container-host and localhost attach targets.
- Debugging behavior differs across local vs devcontainer without a stable contract.

5. Monorepo ergonomics are incomplete.

- No root-level workspace task runner standard for all services.
- Per-service scripts exist but no single canonical command matrix enforced everywhere.

## Refactoring Goals

1. Keep Python development in devcontainer only.
2. Keep Node development possible both locally and in devcontainer.
3. Standardize startup, testing, and debugging commands.
4. Keep all URL configuration in `.env` (no hardcoded URL defaults in code).
5. Make deployment path clean (prod profile, dev profile, CI profile).
6. Remove duplicated config and compose logic.

## Target Monorepo Architecture

## Directory Layout

```text
web-reader/
  apps/
    frontend/              # current frontend
    backend/               # current backend
    langchain/             # current langchain
    fastmcp/               # current fastmcp
  infra/
    compose/
      compose.yaml         # single base compose
      compose.dev.yaml     # dev overrides (hot reload/debug)
      compose.prod.yaml    # prod overrides
    env/
      .env.example         # single canonical env template
    scripts/
      wr                   # cross-platform entrypoint (bash)
      wr.ps1               # powershell wrapper
  config/
  data/
  logs/
  .devcontainer/
  .vscode/
  package.json             # root workspace scripts (Node task facade)
  pyproject.toml           # optional uv workspace root
  README.md
```

Notes:

- Service folders are now relocated under `apps/`; keep wrappers and compose files aligned to `apps/*` paths.
- If minimizing churn initially, keep current folders and still introduce `infra/compose/*` and unified commands first.

## Runtime Topology

Required chain remains unchanged:
`frontend -> backend -> langchain -> fastmcp -> playwright` and `langchain -> ollama`.

Only the wiring and developer workflow changes.

## Compose Consolidation Strategy

## Replace Split Compose With One Compose Family

Create:

- `infra/compose/compose.yaml` (all services, baseline)
- `infra/compose/compose.dev.yaml` (bind mounts, debug ports, watch/reload)
- `infra/compose/compose.prod.yaml` (hardened production settings)

Use Compose profiles to avoid maintaining separate stacks:

- `infra` profile: `ollama`, `playwright`, `model-loader`
- `app` profile: `frontend`, `backend`, `langchain`, `fastmcp`

Examples:

- Full dev: `docker compose -f infra/compose/compose.yaml -f infra/compose/compose.dev.yaml --profile infra --profile app up -d --build`
- Infra only: same command with `--profile infra`
- Prod-like: `docker compose -f infra/compose/compose.yaml -f infra/compose/compose.prod.yaml --profile infra --profile app up -d`

## Network Simplification

- Use one project network by default (Compose-managed).
- Avoid manual `docker network connect` in scripts.
- Use explicit service DNS names internally (`backend`, `langchain`, `fastmcp`, `ollama`, `playwright`).

## Environment and URL Contract

## Single Env Contract

Define one canonical env template in `infra/env/.env.example` and sync root `.env.example` to it.

Standards:

- All service URLs (public and internal) are defined in `.env` keys.
- Internal service-to-service URLs always use container DNS names + internal ports.
- Host-published ports are only for developer/browser access.
- No fallback defaults in code that disagree with `.env.example`.

Required URL keys (minimum):

- `FRONTEND_PUBLIC_URL`
- `BACKEND_PUBLIC_URL`
- `BACKEND_INTERNAL_URL`
- `LANGCHAIN_INTERNAL_URL`
- `FASTMCP_INTERNAL_URL`
- `PLAYWRIGHT_WS_URL`
- `OLLAMA_BASE_URL`
- `VITE_API_URL`
- `VITE_WS_URL`
- `INTERNAL_API_URL`

Recommended baseline:

- Frontend host URL: `http://localhost:3000`
- Backend host URL: `http://localhost:8000`
- Backend internal URL: `http://backend:8000`
- LangChain internal URL: `http://langchain:8001`
- FastMCP internal URL: `http://fastmcp:3100/mcp`
- Playwright internal URL: `ws://playwright:3002`
- Ollama internal URL: `http://ollama:11434`
- Browser API base URL: `/api`
- Browser WS base URL fallback: `ws://localhost:3000`

## Frontend URL Strategy

For fewer environment branches:

- Browser and SSR URL resolution must come from `.env` keys only.
- If reverse proxy paths are used, they are still configured via env values (`VITE_API_URL=/api`, `VITE_WS_URL=ws://localhost:3000`) rather than hardcoded.
- SSR server functions use `INTERNAL_API_URL` from `.env` (container-aware), with no hardcoded localhost fallback.

## Devcontainer Strategy (Python Constraint Preserved)

This remains a first-class requirement.

1. Python tooling (`uv`, `pytest`, `ruff`, `debugpy`) is used inside devcontainer only.
2. Node tooling can run on host or in devcontainer.
3. Root scripts detect context and choose sensible defaults.

Recommended:

- Keep one devcontainer for full-stack development.
- Optionally add a lightweight frontend-only devcontainer profile for faster Node-only cycles.

## Unified Command Surface

## Introduce One Canonical CLI

Add `wr` command wrappers in `infra/scripts/` (bash + PowerShell) to encapsulate all lifecycle commands.

Required commands:

- `wr up` (full stack)
- `wr up --infra`
- `wr down`
- `wr logs [service]`
- `wr test [unit|integration|e2e|all]`
- `wr lint`
- `wr debug up`

Then make:

- root `start.ps1` and `stop.ps1` thin wrappers around `wr`.
- VS Code tasks call only `wr`.
- README and docs reference only `wr` commands.

## Workspace Task Runners

- Node: add root workspace scripts in `package.json` to orchestrate frontend and utility tasks.
- Python: either keep per-service `uv` environments or adopt a root `uv` workspace.

Recommendation:

- Phase 1: keep per-service `uv` to reduce migration risk.
- Phase 2: evaluate root `uv` workspace once commands are stabilized.

## Debugging Model

## Standardize Debug Ports and Attach Targets

- Reserve and document one stable debug port per Python service.
- Use a single attach mode in `.vscode/launch.json` for devcontainer and host scenarios.
- Prefer container DNS attach when debugging from devcontainer, localhost publish when debugging from host.

Add explicit launch profiles:

- `Debug (Devcontainer): Backend/LangChain/FastMCP`
- `Debug (Host): Backend/LangChain/FastMCP`
- `Debug Frontend (Node Inspect)`

## Testing and CI/CD Alignment

## Test Execution Standard

Replace fragmented test docs with one matrix and one command family:

- `wr test unit`
- `wr test integration`
- `wr test e2e`
- `wr test all`

Map each to existing service commands internally.

## CI Pipeline Shape

1. Lint + typecheck stage.
2. Unit tests (all services).
3. Integration tests (infra profile up).
4. E2E smoke (full profiles up).
5. Build images (prod profile).

Use the same compose files and env contracts as local development to reduce environment skew.

## Migration Plan (Phased)

## Phase 0: Baseline and Freeze (1 day)

1. Freeze new infra/script changes.
2. Capture current behavior and known pain points.
3. Define canonical port map and environment variable contract.

Deliverables:

- Approved env contract table.
- Approved command matrix.

## Phase 1: Orchestration Unification (2-3 days)

1. Create `infra/compose/compose.yaml` and `compose.dev.yaml` by merging existing `container/` and `docker/` compose files.
2. Implement Compose profiles (`infra`, `app`).
3. Introduce `wr` wrappers and update root scripts to delegate.
4. Update VS Code tasks to call `wr` only.

Deliverables:

- Single compose family operational.
- Old compose entrypoints marked deprecated.

## Phase 2: Config and URL Normalization (2-3 days)

1. Normalize `.env.example` and code defaults to one contract.
2. Remove contradictory hardcoded defaults (`5000` vs `8000`, `3000` vs `3100`).
3. Ensure every URL read by frontend/backend/langchain/fastmcp is loaded from `.env` keys.
4. If relative API/WS paths are desired, configure them in `.env` values instead of code defaults.

Deliverables:

- Zero known port/URL drift.
- Config validation checks at startup.

## Phase 3: Debug and Dev UX Cleanup (2 days)

1. Rewrite `.vscode/launch.json` profiles for clear host vs devcontainer modes.
2. Replace malformed/outdated debug docs with one canonical guide.
3. Ensure `wr debug up` path starts services with debug instrumentation consistently.

Deliverables:

- One documented debug flow with working breakpoints.

## Phase 4: Repository Layout Modernization (optional, 3-5 days)

1. Move services under `apps/` (or keep existing layout if churn is not justified).
2. Introduce root workspace package scripts and optional `uv` workspace.
3. Update import paths, Docker build contexts, and docs.

Deliverables:

- Conventional monorepo layout (if adopted).
- Backward compatibility shims removed.

## Phase 5: Deployment Hardening (2-4 days)

1. Finalize `compose.prod.yaml` and production env schema.
2. Add image tagging/versioning and release docs.
3. Add CI gates and release smoke tests.

Deliverables:

- Repeatable deployment path from same monorepo workflow.

## Deprecation Plan

After Phase 1 stability window:

- Deprecate `container/` root scripts and legacy compose entrypoints.
- Keep temporary compatibility wrappers for one release cycle.
- Remove wrappers after documented cutover date.

## Risks and Mitigations

1. Risk: Service startup regressions during compose merge.
   Mitigation: keep old compose paths behind wrappers until parity tests pass.

2. Risk: Env changes break tests.
   Mitigation: add startup config validation and integration smoke tests for each service dependency edge.

3. Risk: Debug attach confusion persists.
   Mitigation: explicit host/devcontainer launch profiles and strict docs with one command path.

4. Risk: Large layout move increases merge conflicts.
   Mitigation: separate orchestration/config unification from folder moves; do layout move later.

## Definition of Done

1. One compose command family starts infra, app, or both.
2. One `.env.example` matches all runtime defaults.
3. One script surface (`wr`) is used by docs, tasks, and CI.
4. Python workflows fully functional in devcontainer without local Python.
5. Node workflows function both local and devcontainer.
6. Debugging works via documented profiles without manual network surgery.
7. Legacy orchestration paths removed or clearly deprecated.

## Immediate Next Actions (Recommended Order)

1. Approve canonical port and URL contract.
2. Implement Phase 1 compose/profile merge and `wr` wrappers.
3. Update VS Code tasks and root scripts to only call wrappers.
4. Normalize `.env.example` and code defaults.
5. Rewrite debug/test docs to match real commands.

## Recommendation

Proceed with a phased refactor that merges container orchestration first, then fixes env drift, then cleans debug UX, and only then considers physical folder relocation.

This sequencing gives the biggest reduction in day-to-day friction quickly while preserving your Python-in-devcontainer workflow and minimizing disruption risk.

## Decisions Locked (Interview Outcomes)

The following decisions are now locked for implementation:

1. Migration approach: hybrid.

- Stage runtime/config unification first.
- Do physical folder moves later.

2. Python workflow constraint:

- No Python on host machine.
- Python runs only in devcontainer or Docker containers.

3. Python runtime default:

- Hybrid default: devcontainer for inner-loop debugging, Docker for integration and e2e validation.

4. Frontend runtime default:

- Local Node on host is the default.
- Devcontainer frontend is optional.

5. URL config policy:

- Strict fail-fast.
- All URL configuration comes from root `.env`.
- No hardcoded localhost URL fallbacks in code.

6. Command surface policy:

- One canonical command surface.
- Remove legacy scripts immediately at cutover.

7. Compose consolidation policy:

- Keep old and new compose definitions briefly in branch for parity checks.
- Delete old compose paths before merge.

8. Folder layout timing:

- Postpone service moves into `apps/` until runtime and env stabilization is complete.

9. Startup defaults:

- Default startup brings full stack up.
- Optional partial flags for infra-only or app-only.

10. Frontend-to-Python default target:

- Frontend local dev targets Docker-hosted Python services by default.

11. Python debugging mode:

- Attach-only debugging standard.

12. Logging baseline:

- Structured JSON logs by default.
- Pretty console output optional via dev switch.

13. Observability scope now vs later:

- Current refactor includes baseline logging and correlation only.
- OTEL + Grafana stack is deferred to a follow-up phase.

14. Env file source of truth:

- Root `.env` is the only active source of truth.

15. Validation gates before merge:

- Frontend lint + typecheck.
- Unit tests for all services.
- Integration tests for services that have them.
- At least one end-to-end smoke path.
- Startup smoke in both devcontainer-Python mode and Docker-Python mode.

16. Deployment optimization target:

- Docker Compose first.
- Kubernetes remains a later option.

17. Shell UX preference:

- PowerShell-first command surface with bash wrapper.

18. Env variants policy:

- One active root `.env` only.
- Variant templates exist and are copied into root `.env` when switching context.

19. Secret handling now:

- Use root `.env` in development now.
- Keep `.env` out of version control.
- Move to secret manager in deployment-focused follow-up work.

20. Deferred browser network boundary hardening:

- End-state target: browser only communicates with the frontend SSR origin.
- Request chain target: browser -> SSR -> API -> backend/langchain/fastmcp.
- SSR must only communicate with API.
- Current migration accepts temporary direct browser URL usage where needed; complete this boundary hardening after migration stabilization.
