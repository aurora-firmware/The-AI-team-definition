---
id: T-060
title: Add no-routine-forced-branch-deletion rule to git-conventions guideline
status: pending
priority: medium
assigned-role: unassigned
created: '2026-06-04'
---

# Add no-routine-forced-branch-deletion rule to git-conventions guideline

## Description

Source: `full_skills_review.md` issue I15 (doc side). Add a hard rule to
`ai-process/guidelines/git-conventions.md` prohibiting routine forced branch deletion:
integration deletes merged branches with `git branch -d` (safe) only; if `-d` is refused, it
stops and reports rather than forcing `git branch -D`. The `integrate` skill body is aligned in
T-063.

## Acceptance Criteria

AC-1: The git-conventions guideline Hard Rules SHALL prohibit routine forced branch deletion
      (`git branch -D`) during integration.
AC-2: WHEN safe deletion (`git branch -d`) is refused, THE guideline SHALL require stopping and
      reporting instead of forcing deletion.

## Dependencies

- None

## Files to Touch

- `ai-process/guidelines/git-conventions.md` — Hard Rules: no routine forced branch deletion

## Verification

```bash
grep -niE "branch -D|forced|force.delete" ai-process/guidelines/git-conventions.md
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-04

Added a new Hard Rule to `ai-process/guidelines/git-conventions.md` covering AC-1 and AC-2. The rule reads: "No routine forced branch deletion (`git branch -D`) during integration. Use safe deletion (`git branch -d`) only. If `-d` is refused, stop and report instead of forcing deletion." The word "routine" was chosen deliberately to avoid contradicting the narrow audited fallback in the `integrate` skill (which allows `git branch -D` only after confirming the merge commit exists in the destination log and documenting it in the report) — T-063 will align the `integrate` skill body separately.

The guideline file contains a comment (line 63) noting that `.claude/skills/git-conventions/SKILL.md` must be updated atomically. That file and the CLI source `cli/src/ai_team/init/sources/skills/git-conventions/body.md` were not touched because: (1) the task explicitly restricts scope to `ai-process/guidelines/git-conventions.md` only, and (2) project memory confirms `.claude/skills/` files are stale hand-copies, not the source of truth. Syncing the canonical git-conventions skill body to source is owned by T-064.

Committed on the task branch as `docs(guidelines): prohibit routine forced branch deletion in Hard Rules` (commit `2568182`).

Nothing remains for this task — the verification grep passes and both acceptance criteria are met.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-04

PASS

Stage 1 (spec compliance): Both acceptance criteria are met. AC-1 is satisfied by the new Hard Rules bullet "No routine forced branch deletion (`git branch -D`) during integration." AC-2 is satisfied by the same bullet's continuation "If `-d` is refused, stop and report instead of forcing deletion." The change is scoped exactly to `ai-process/guidelines/git-conventions.md` as required. The Work Log correctly explains why the git-conventions skill body files were not touched (T-064 owns that; project memory confirms `.claude/skills/` files are stale hand-copies). No unspecified behavior was added.

Stage 2 (code quality): The new rule follows the existing Hard Rules bullet format, is concise, and uses "routine" deliberately to remain reconcilable with the integrate skill's audited `git branch -D` fallback (which requires confirming the merge commit in the destination log and documenting the forced deletion — not routine use). No dead content, no contradictions introduced. Pure-docs change; no tests required or applicable.
