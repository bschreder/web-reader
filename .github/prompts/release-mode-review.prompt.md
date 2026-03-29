---
name: release-mode-review
description: "Run a release-style full working-tree audit for Web Reader with lint/build/unit/integration/e2e validation and a human-readable report."
argument-hint: "Describe release scope, target branch/tag, and any high-risk areas to emphasize."
agent: Web Reader Review
---
Run a release-mode review for this repository.

## Mode
- Force full working-tree audit mode.
- Do not use branch-diff mode unless explicitly requested.

## Required Inputs
Provide these when available:
- Release scope: branch, tag, or milestone
- Areas of concern: services or files to prioritize
- Time constraints: optional review budget
- Known risks: optional list

## Required Workflow
1. Load `.github/instructions/review-workflow.instructions.md`.
2. Inventory the full working tree (tracked, staged, and untracked behavior-impacting files).
3. Apply the workspace command matrix for validation.
4. Run lint, type-check (where applicable), build, unit, integration, and e2e validation.
5. Perform security and performance checks with emphasis on secret exposure and secret logging.
6. Produce a readable release audit report for human review.

## Output Requirements
Return a markdown report with these sections in order:
1. Executive Summary
2. Findings (sorted by severity)
3. Validation Results
4. Testing Gaps
5. Residual Risks
6. Open Questions

## Release Gate Guidance
- Mark status as Not ready if any Critical or High findings exist.
- Mark status as Not ready if lint/build/unit/integration/e2e has failures.
- If checks are blocked by environment or infrastructure, report exactly what is blocked and why.
