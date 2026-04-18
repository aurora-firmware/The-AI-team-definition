---
id: "T-005"
title: "Task template — numbered EARS acceptance criteria with pattern reference"
status: pending
priority: high
assigned-role: implementer
created: 2026-04-18
spec: project/specs/ears-acceptance-criteria.md
---

# Task template — numbered EARS acceptance criteria with pattern reference

## Description

Per spec `ears-acceptance-criteria.md` (8.1), replace the checkbox bullet list in `TEMPLATE-task.md`'s Acceptance Criteria section with a numbered `AC-N` list and embed the five EARS patterns as a template comment inside the same section.

Section shape after the change:

```markdown
## Acceptance Criteria

<!-- EARS pattern reference. Every criterion must match one pattern:
  1. Ubiquitous            — The system shall [outcome]
  2. Event-driven          — WHEN [trigger] THE SYSTEM SHALL [outcome]
  3. Unwanted-behaviour    — IF [fault] THEN THE SYSTEM SHALL [outcome]
  4. State-driven          — WHILE [state] THE SYSTEM SHALL [outcome]
  5. Optional              — WHERE [feature included] THE SYSTEM SHALL [outcome]

Examples:
  AC-1: WHEN the user submits valid credentials THE SYSTEM SHALL
        redirect to /dashboard within 200ms.
  AC-2: IF the password is incorrect THEN THE SYSTEM SHALL return 401
        and display "Invalid credentials".
  AC-3: The system shall log every authentication attempt with user id
        and outcome.
-->

AC-1: ...
AC-2: ...
AC-3: ...
```

The current `- [ ]` checkbox format is removed. No other section of the template is modified.

## Acceptance Criteria

AC-1: The `TEMPLATE-task.md` file Acceptance Criteria section shall use a numbered `AC-N` list format, not the `- [ ]` checkbox format.
AC-2: The Acceptance Criteria section shall contain an HTML comment listing all five EARS patterns (Ubiquitous, Event-driven, Unwanted-behaviour, State-driven, Optional) with one syntactic example each.
AC-3: The Acceptance Criteria section shall contain at least three example `AC-N` lines demonstrating different EARS patterns (at minimum one Event-driven, one Unwanted-behaviour, and one Ubiquitous example).
AC-4: No other top-level section of `TEMPLATE-task.md` (Description, Dependencies, Files to Touch, Verification, Notes, Review) shall be modified by this task.
AC-5: WHEN `/new-task` generates a new task file THE SYSTEM SHALL produce an Acceptance Criteria section with the numbered `AC-N` format and the embedded EARS pattern reference comment.

## Dependencies

- None

## Files to Touch

- `.claude/skills/new-task/assets/TEMPLATE-task.md` — restructure Acceptance Criteria section

## Verification

```bash
# Template no longer uses checkbox criteria
! grep -nE '^- \[ \] Criterion' .claude/skills/new-task/assets/TEMPLATE-task.md
# EARS pattern reference comment present
grep -n 'EARS pattern reference' .claude/skills/new-task/assets/TEMPLATE-task.md
# All five pattern names listed
for p in Ubiquitous Event-driven Unwanted-behaviour State-driven Optional; do
  grep -q "$p" .claude/skills/new-task/assets/TEMPLATE-task.md || { echo "MISSING: $p"; exit 1; }
done
# Numbered AC placeholders present
grep -nE '^AC-[0-9]+:' .claude/skills/new-task/assets/TEMPLATE-task.md
```

## Notes

Reference: spec 8.1, Component 1.
This task precedes T-007 (spec 8.7 replaces the Notes section with Work Log in the same file). T-007 depends on this task.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->
