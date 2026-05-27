# Phase 4 Layout Decision

Date: 2026-05-26

Phase 4 is now implemented with physical relocation completed:

- Root workspace task runners are added (`package.json` and optional root `pyproject.toml`).

- Canonical service paths are:
  - `apps/frontend/`
  - `apps/backend/`
  - `apps/langchain/`
  - `apps/fastmcp/`

Operational references (compose, wrappers, VS Code launch, CI, root workspace metadata) are updated to the `apps/` layout.
