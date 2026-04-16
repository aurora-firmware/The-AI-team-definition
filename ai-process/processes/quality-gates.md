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

---

> **Architect Preflight (automated — not a human gate)**
>
> After the planner writes the task plan, the Architect reviews it before dev-loop starts.
> The Architect checks: dependency correctness, file conflict risks, architectural consistency with existing decisions, and task atomicity.
> If issues are found, the Architect creates corrective tasks or flags problems back to the Planner for revision.
> No human approval is required — this is an agent-to-agent quality step.
> See `ai-process/processes/workflow-overview.md` and `.claude/agents/architect.md` for details.

---

## Gate 2: Code Review

**When:** After an implementer completes a task.
**Evaluator:** Reviewer agent (two stages).

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

**On failure:** Task returns to implementer with specific feedback. The reviewer must provide actionable notes, not vague criticism.

## Gate 3: Integration Tests

**When:** After each task passes code review (Gate 2), during per-task integration within `/dev-loop`.
**Evaluator:** Automated test suite, run by the `integrate` skill.
**Pass criteria:**
- All unit tests pass on the feature branch (pre-merge).
- All unit and integration tests pass on `dev` after the merge (regression check).
- No unresolved merge conflicts remain.

**On failure:** The `integrate` skill reverts the merge commit, files a bug for each regression via `/new-bug`, and stops the `/dev-loop`. The feature branch is preserved for fixing.

## Gate 4: Final Merge Sign-off

**When:** After the task queue is empty and all tasks are in `completed/`.
**Evaluator:** Human.
**Pass criteria:**
- Integration tests are green.
- No open bugs with severity `critical` or `high`.
- The `/status-report` summary matches the approved specification.

**On failure:** Human provides feedback. New tasks are created to address issues.

> This is a sign-off, not a code review. The human reviews the status summary and confirms the outcome matches the spec intent — not individual diffs. Detailed code quality was already verified at Gates 2 and 3.

