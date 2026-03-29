# Prompt: Update Dependencies and Run Full Test Suite

You are an AI coding agent working in the `web-reader` monorepo. Your task is to safely update dependencies for one or more services and then run the full test suite to ensure everything still passes.

## Scope

This prompt may be invoked for one or more of the following codebases:

- `#file:backend` → Python project managed by uv
- `#file:langchain` → Python project managed by uv
- `#file:fastmcp` → Python project managed by uv
- `#file:frontend` → TypeScript/React project managed by npm

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

2. **Update Python Dependencies (uv Projects)**
   - For each of `backend`, `langchain`, or `fastmcp` that is requested:
     - Change directory to the project folder (e.g. `/workspaces/web-reader/backend`).
     - Update direct dependencies in `pyproject.toml` to the latest non-breaking versions (minor/patch only within current major), then refresh lockfile/env.
       - Keep standard PEP 440 ranges in `pyproject.toml`. The caret-style intent should be expressed as `>=1.2.0,<2.0.0` for stable packages and `>=0.128,<0.129` for `0.x` packages.
       - Required commands (run per requested Python project):
         - `cd /workspaces/web-reader/<service>`
         - Main dependencies (excluding python):
           - `python - <<'PY' | xargs -r uv add --upgrade --bounds major`
           - `import tomllib`
           - `from pathlib import Path`
           - `data = tomllib.loads(Path("pyproject.toml").read_text())`
           - `for dep in data.get("project", {}).get("dependencies", []):`
           - `    print(dep.split(";")[0].strip().split()[0].split("[")[0])`
           - `PY`
         - Optional groups (if present):
           - `python - <<'PY' | xargs -r uv add --group test --upgrade --bounds major`
           - `import tomllib`
           - `from pathlib import Path`
           - `data = tomllib.loads(Path("pyproject.toml").read_text())`
             - `for dep in data.get("dependency-groups", {}).get("test", []):`
             - `    print(dep.split(";")[0].strip().split()[0].split("[")[0])`
           - `PY`
           - `python - <<'PY' | xargs -r uv add --group debug --upgrade --bounds major`
           - `import tomllib`
           - `from pathlib import Path`
           - `data = tomllib.loads(Path("pyproject.toml").read_text())`
             - `for dep in data.get("dependency-groups", {}).get("debug", []):`
             - `    print(dep.split(";")[0].strip().split()[0].split("[")[0])`
           - `PY`
           - `python - <<'PY' | xargs -r uv add --group dev --upgrade --bounds major`
           - `import tomllib`
           - `from pathlib import Path`
           - `data = tomllib.loads(Path("pyproject.toml").read_text())`
             - `for dep in data.get("dependency-groups", {}).get("dev", []):`
             - `    print(dep.split(";")[0].strip().split()[0].split("[")[0])`
           - `PY`
         - Refresh lock and environment:
           - `uv lock`
           - `uv sync --all-groups`
     - Wait for the command to finish and record whether it succeeded or failed.
     - If **any** uv command fails, stop updating further projects, collect the error output, and surface a clear summary to the user.
     - If package update succeeds, ensure `pyproject.toml` and `uv.lock` reflect the updated constraints.

3. **Update Frontend Dependencies (npm)**
   - If `#file:frontend` is requested:
     - Change directory to `/workspaces/web-reader/frontend`.
     - Run the following commands to update dependency ranges in `package.json` with non-breaking updates only (minor/patch), then refresh lockfile:
       - `npx -y npm-check-updates --target minor --upgrade`
       - `npm i --legacy-peer-deps`
     - Wait for the command to finish and record whether it succeeded or failed.
     - If the `npm` command fails, stop and surface the error clearly.
     - If package update succeeds, ensure `package.json` and `package-lock.json` are updated.

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
       - Which project and command failed (e.g., `backend: uv add ...`, `frontend: npx npm-check-updates --target minor --upgrade`, or `./scripts/test-all.sh`).
       - Key error messages or failing test names (do not paste excessively long logs).
       - Note that dependency updates may be partially applied and should be reviewed before commit.

6. **Safety and Consistency**
  - Do **not** modify source code files as part of this prompt; only dependency files updated by uv/npm dependency commands (e.g., `pyproject.toml`, `uv.lock`, `package.json`, `package-lock.json`) should change.
   - Do **not** run any other commands besides those explicitly listed above unless they are required to enter the correct directory (`cd`) or inspect minimal status (like `ls` or `pwd`).
   - Respect the existing project structure and configuration; do not add or remove services.

## Summary Output Format

When you finish, respond with a short, structured summary:

- `Updated projects:` list of updated projects (subset of: backend, langchain, fastmcp, frontend)
- `Dependency update status:` success or failure per project
- `Test script:` status of `./scripts/test-all.sh` (pass/fail)
- `Notes:` any important follow‑ups (e.g., failing tests, manual review suggested)
