---
id: "T-007"
title: "Task template — replace Notes with Work Log section"
status: pending
priority: high
assigned-role: implementer
created: 2026-04-18
spec: project/specs/handoff-progress-unification.md
---

# Task template — replace Notes with Work Log section

## Description

Per spec `handoff-progress-unification.md` (8.7), rename the `## Notes` section in `TEMPLATE-task.md` to `## Work Log` and insert a template comment describing the entry shape.

Section shape after the change:

```markdown
## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

```

The Review section remains unchanged (distinct from Work Log; Work Log is implementer-only, Review is reviewer-only).

## Acceptance Criteria

AC-1: The `TEMPLATE-task.md` file shall contain a `## Work Log` section in place of the former `## Notes` section.
AC-2: The `TEMPLATE-task.md` file shall not contain a `## Notes` heading.
AC-3: The `## Work Log` section shall contain an HTML comment instructing: one entry per session boundary, dated heading `### Session N — YYYY-MM-DD`, free-prose body, read-before-starting, final-entry-is-handoff.
AC-4: The `## Review` section shall remain present and unchanged in structure.
AC-5: No other section of the template shall be reordered or removed by this task.
AC-6: WHEN `/new-task` generates a new task file THE SYSTEM SHALL produce a document with a `## Work Log` section and no `## Notes` section.

## Dependencies

- `T-005` — prior EARS restructure of the same file must land first

## Files to Touch

- `.claude/skills/new-task/assets/TEMPLATE-task.md` — rename Notes → Work Log; add guidance comment

## Verification

```bash
# Work Log heading present, Notes heading absent
grep -q '^## Work Log' .claude/skills/new-task/assets/TEMPLATE-task.md
! grep -q '^## Notes' .claude/skills/new-task/assets/TEMPLATE-task.md
# Comment with session-entry guidance present
grep -n 'Append one entry per session' .claude/skills/new-task/assets/TEMPLATE-task.md
# Review section still present
grep -q '^## Review' .claude/skills/new-task/assets/TEMPLATE-task.md
```

## Notes

Reference: spec 8.7, Component 1.
Blocks T-009, T-012, T-015 (all consume the Work Log section shape).

## Review

<!-- Reviewer appends verdict here after each review cycle. -->
