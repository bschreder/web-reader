# Prompt: Update Dependencies and Run Full Test Suite

You are GitHub Copilot working in the `web-reader` monorepo. Your task is to safely update dependencies for one or more services and then run the full test suite to ensure everything still passes.

## Scope

This prompt may be invoked for one or more of the following codebases:

- `#file:backend`   → Python project managed by Poetry
- `#file:langchain` → Python project managed by Poetry
- `#file:fastmcp`   → Python project managed by Poetry
- `#file:frontend`  → TypeScript/React project managed by npm

## High-Level Goals

1. Update dependencies for the selected project(s).
2. Run the shared test script `./scripts/test-all.sh` from the repo root.
3. Confirm that all tests pass after dependency updates.
4. If anything fails, capture the failures clearly and avoid making further changes.

## Instructions

Follow these steps carefully and **do not skip any**:

1. **Identify Target Project(s)**
   - Determine which of the following markers are present in the invocation:
     - `#file:backend`
     - `#file:langchain`
     - `#file:fastmcp`
     - `#file:frontend`
   - Treat each marker as a request to update dependencies for that specific project directory under `/workspaces/web-reader`.

2. **Update Python Dependencies (Poetry Projects)**
   - For each of `backend`, `langchain`, or `fastmcp` that is requested:
     - Change directory to the project folder (e.g. `/workspaces/web-reader/backend`).
     - Run `poetry update` to update all dependencies for that service.
       - Command:
         - `cd /workspaces/web-reader/backend && poetry update`
         - `cd /workspaces/web-reader/langchain && poetry update`
         - `cd /workspaces/web-reader/fastmcp && poetry update`
     - Wait for the command to finish and record whether it succeeded or failed.
     - If **any** `poetry update` fails, stop updating further projects, collect the error output, and surface a clear summary to the user.

3. **Update Frontend Dependencies (npm)**
   - If `#file:frontend` is requested:
     - Change directory to `/workspaces/web-reader/frontend`.
     - Run the following command to refresh dependencies while preserving compatibility:
       - `npm i --legacy-peer-deps`
     - Wait for the command to finish and record whether it succeeded or failed.
     - If the `npm` command fails, stop and surface the error clearly.

4. **Run the Full Test Suite**
   - After all requested dependency updates succeed, run the unified test script from the repo root:
     - Change directory to `/workspaces/web-reader`.
     - Run:
       - `./scripts/test-all.sh`
   - Wait for the script to complete.
   - Capture:
     - Exit code.
     - Any high-level failures (e.g., failing test suites, stack traces, or error summaries).

5. **Result Handling**
   - If **all commands** (dependency updates and `./scripts/test-all.sh`) succeed:
     - Report success with a concise summary, e.g.:
       - Which projects had dependencies updated.
       - Confirmation that `./scripts/test-all.sh` passed.
   - If **any command fails**:
     - Mark the overall task as not fully successful.
     - Provide a clear, structured summary including:
       - Which project and command failed (e.g., `backend: poetry update`, `frontend: npm i --legacy-peer-deps`, or `./scripts/test-all.sh`).
       - Key error messages or failing test names (do not paste excessively long logs).
       - Note that dependency updates may be partially applied and should be reviewed before commit.

6. **Safety and Consistency**
   - Do **not** modify source code files as part of this prompt; only dependency lockfiles and other files that are updated by `poetry update` or `npm i --legacy-peer-deps` should change.
   - Do **not** run any other commands besides those explicitly listed above unless they are required to enter the correct directory (`cd`) or inspect minimal status (like `ls` or `pwd`).
   - Respect the existing project structure and configuration; do not add or remove services.

## Summary Output Format

When you finish, respond with a short, structured summary:

- `Updated projects:` list of updated projects (subset of: backend, langchain, fastmcp, frontend)
- `Dependency update status:` success or failure per project
- `Test script:` status of `./scripts/test-all.sh` (pass/fail)
- `Notes:` any important follow‑ups (e.g., failing tests, manual review suggested)
