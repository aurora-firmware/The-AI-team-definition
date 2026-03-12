---
title: "Quality Gates"
status: approved
created: 2026-03-10
---

# Quality Gates

Quality gates are checkpoints where work must meet defined criteria before proceeding. They prevent defects from propagating downstream where they become more expensive to fix.

## Gate 1: Specification Approval

**When:** After the planner produces a design document from brainstorming.
**Evaluator:** Human.
**Pass criteria:**
- The problem is clearly defined.
- The proposed solution addresses the stated problem.
- Architecture is described with enough detail to derive tasks.
- Exclusions are explicitly stated.
- No unresolved open questions.

**On failure:** Return to planner with feedback for revision.

## Gate 2: Task Plan Review

**When:** After the planner breaks the spec into tasks.
**Evaluator:** Human.
**Pass criteria:**
- Every task is atomic (one clear outcome).
- Every task has acceptance criteria and a verification command.
- Dependencies between tasks are correct and complete.
- No two tasks modify the same files (prevents merge conflicts during integration).
- The full set of tasks covers the entire specification.

**On failure:** Return to planner with feedback for revision.

## Gate 3: Code Review

**When:** After an implementer completes a task.
**Evaluator:** Reviewer agent (two stages).

### Stage 1: Spec Compliance
**Pass criteria:**
- All acceptance criteria from the task are met.
- No functionality is missing.
- No unspecified behavior was added.

### Stage 2: Code Quality
**Pass criteria:**
- Code follows the project's coding standards (`ai-process/guidelines/coding-standards.md`).
- Tests exist and pass.
- No security vulnerabilities introduced.
- No performance regressions.
- Code is readable and maintainable.

**On failure:** Task returns to implementer with specific feedback. The reviewer must provide actionable notes, not vague criticism.

## Gate 4: Integration Tests

**When:** After all tasks are reviewed and approved, during integration.
**Evaluator:** Automated test suite, managed by the integrator agent.
**Pass criteria:**
- All unit tests pass.
- All integration tests pass.
- No merge conflicts remain.

**On failure:** Integrator bisects to identify the breaking change, then creates a fix task or escalates.

## Gate 5: Final Merge Approval

**When:** After integration tests pass.
**Evaluator:** Human.
**Pass criteria:**
- Integration tests are green.
- No open bugs with severity `critical` or `high`.
- The merged code matches the approved specification.

**On failure:** Human provides feedback. New tasks are created to address issues.
