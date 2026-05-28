---
title: "Quality Gates"
status: approved
created: 2026-03-10
---

# Quality Gates

Gates are checkpoints where work must meet defined criteria before proceeding. They prevent defects from propagating downstream where they become more expensive to fix.

## Gate 1: Specification Approval

**When:** After the Planner produces a design document from interactive brainstorming.
**Evaluator:** Human.
**Pass criteria:**
- The problem is clearly defined.
- The proposed solution addresses the stated problem.
- Architecture is described with enough detail to derive tasks.
- Exclusions are explicitly stated.
- No unresolved open questions.

**On failure:** Return to Planner with feedback for revision.

## Gate 2: Task Plan Preflight

**When:** After the Planner writes the task plan, before the development loop starts.
**Evaluator:** Architect.
**Scope:** Gate 2 focuses on **technical task-plan readiness**. The Architect evaluates dependencies, file conflicts, architectural consistency with existing decisions, atomicity, and verifiability. Gate 2 does not reopen product or spec approval questions that were already settled at Gate 1. If the Architect finds a product-scope concern that does not block technical readiness, it is noted as follow-up feedback rather than a Gate 2 failure. Only a contradiction against the approved spec or existing ADRs causes a Gate 2 failure or escalation.
**Pass criteria:**
- Task dependencies are correct and complete.
- File conflict risks are identified and resolved through dependencies or task changes.
- Task plan is architecturally consistent with existing decisions.
- Tasks are atomic, independently verifiable, and ready for implementation.

**On failure:** Architect returns a correction request to the Planner. The Planner revises the task plan and resubmits it to Gate 2.

## Gate 3: Code Review

**When:** After a Developer completes a task or bug fix.
**Evaluator:** Reviewer role (two stages).
**Output:** Review Verdict entry committed to the canonical task or bug file on `dev-agent`.

### Stage 1: Spec Compliance
**Pass criteria:**
- All acceptance criteria from the task are met.
- No functionality is missing.
- No unspecified behavior was added.

### Stage 2: Code Quality
**Pass criteria:**
- Code follows the coding standards: `ai-process/guidelines/coding-standards.md` (general) and `project/docs/coding_guidelines.md` (project-specific tech-stack rules, if present).
- Relevant tests exist for the changed behavior.
- The Developer's Work Log records local test evidence or explains why a local test run was not possible.
- No security vulnerabilities introduced.
- No performance regressions.
- Code is readable and maintainable.

### Bug Fix Criteria
For bug fixes, the Reviewer also verifies:
- The Diagnosis Log records reproduction status, captured evidence, isolated fault, and root cause or fault hypothesis.
- The fix targets the isolated cause rather than masking the symptom downstream.
- A regression test exists when the defect can be tested automatically, or the Work Log explains why only manual verification is possible.
- The Fix Verification steps from the bug report were run or a clear reason is recorded.

**On failure:** The Reviewer records specific feedback in the canonical work item. The active loop returns the work item to the Developer for another implementation cycle. After the third failed review or any `ESCALATE` verdict, the active loop consults the Architect before stopping for human action.

## Gate 4: Integration Tests

**When:** After each task or bug fix passes code review (Gate 3), during integration by the active loop.
**Evaluator:** Automated test suite, run by the integration procedure.
**Pass criteria:**
- All unit tests pass on the source branch (pre-merge).
- All unit and integration tests pass on the destination branch after the merge (regression check).
- No unresolved merge conflicts remain.

**On failure:** The integration procedure reverts the merge commit, files a bug report for each regression on `dev-agent`, and stops the active loop. The source branch is preserved for fixing.
Regression bug reports must record the preserved source branch as `source_branch` so the bug-fix loop can branch from and merge back into that branch before integration is retried.

## Development Loop Baseline Guard

Before the development loop claims its first task it reads the documented baseline test command from the `## Test` section of the root `CLAUDE.md`. If that section is absent, empty, or still contains the placeholder from `ai-team init`, the loop escalates to the human rather than guessing. If the command is present but fails, the loop stops and reports the output. This is an operational startup check, not a numbered quality gate — it is distinct from Gate 4 (integration test suite), which runs after each task merge.

## Gate 5: Final Merge Sign-off

**When:** After the task queue is empty and all tasks are in `completed/`.
**Evaluator:** Human.
**Pass criteria:**
- Integration tests are green.
- No open bugs with severity `critical` or `high`.
- The status summary matches the approved specification.
- The status summary lists completed tasks, unresolved bugs by severity, and latest integration-test result.

**On failure:** Human provides feedback. New tasks are created to address issues.

> This is a sign-off, not a code review. The human reviews the status summary and confirms the outcome matches the spec intent — not individual diffs. Detailed code quality was already verified at Gates 3 and 4.
