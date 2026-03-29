---
name: strict-developer-loop
description: "Implement a feature or bugfix in Web Reader using a strict remediation loop: build/lint/test, invoke review, fix findings, and repeat until all blockers are cleared."
argument-hint: "Describe the feature or bugfix, scope, and acceptance criteria."
agent: Web Reader Developer
---
Run the Web Reader strict developer automation loop for this request.

## Task
Implement the requested feature or bugfix with minimal, focused changes.

## Required Inputs
Provide these in your request or infer from repository context when omitted:
- Goal: what behavior should change
- Scope: files/services in or out of scope
- Acceptance criteria: explicit conditions that must be true
- Constraints: anything to avoid (refactors, dependency changes, API changes)

## Execution Contract
1. Implement the requested changes.
2. Run repository validation according to `.github/instructions/review-workflow.instructions.md`.
3. Invoke `Web Reader Review` in branch-diff mode.
4. Fix findings and failing validations in priority order:
   - Critical findings
   - High findings
   - lint/build/unit/integration/e2e failures
   - Medium and Low findings
5. Repeat until completion criteria are met or a hard stop condition is reached.

## Completion Criteria
- No Critical findings
- No High findings
- Lint passes
- Build passes
- Unit tests pass
- Integration tests pass
- E2E tests pass

## Output Requirements
For each iteration, report:
- Iteration number
- Changes made
- Validation status by stage
- Review finding counts by severity
- Remaining blockers

At the end, report:
- Final status: `completed` or `blocked`
- Final validation matrix
- Unresolved blockers or risks
- Short change summary
