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

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
