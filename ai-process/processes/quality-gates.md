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
**Pass criteria:**
- Task dependencies are correct and complete.
- File conflict risks are identified and resolved through dependencies or task changes.
- Task plan is architecturally consistent with existing decisions.
- Tasks are atomic, independently verifiable, and ready for implementation.

**On failure:** Architect creates corrective tasks or returns the task plan to the Planner for revision.

## Gate 3: Code Review

**When:** After a Developer completes a task.
**Evaluator:** Reviewer role (two stages).

### Stage 1: Spec Compliance
**Pass criteria:**
- All acceptance criteria from the task are met.
- No functionality is missing.
- No unspecified behavior was added.

### Stage 2: Code Quality
**Pass criteria:**
- Code follows the coding standards: `ai-process/guidelines/coding-standards.md` (general) and `project/docs/coding-guidelines.md` (project-specific tech-stack rules, if present).
- Tests exist and pass.
- No security vulnerabilities introduced.
- No performance regressions.
- Code is readable and maintainable.

**On failure:** Task returns to the Developer with specific feedback. The Reviewer must provide actionable notes, not vague criticism.

## Gate 4: Integration Tests

**When:** After each task passes code review (Gate 3), during per-task integration within the development loop.
**Evaluator:** Automated test suite, run by the integration procedure.
**Pass criteria:**
- All unit tests pass on the feature branch (pre-merge).
- All unit and integration tests pass on `dev-agent` after the merge (regression check).
- No unresolved merge conflicts remain.

**On failure:** The integration procedure reverts the merge commit, files a bug report for each regression, and stops the development loop. The feature branch is preserved for fixing.

## Gate 5: Final Merge Sign-off

**When:** After the task queue is empty and all tasks are in `completed/`.
**Evaluator:** Human.
**Pass criteria:**
- Integration tests are green.
- No open bugs with severity `critical` or `high`.
- The status summary matches the approved specification.

**On failure:** Human provides feedback. New tasks are created to address issues.

> This is a sign-off, not a code review. The human reviews the status summary and confirms the outcome matches the spec intent — not individual diffs. Detailed code quality was already verified at Gates 3 and 4.
