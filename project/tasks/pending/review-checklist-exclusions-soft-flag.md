---
id: "T-003"
title: "Review checklist — soft flag when Exclusions section missing"
status: pending
priority: medium
assigned-role: implementer
created: 2026-04-18
spec: project/specs/out-of-scope-first-class.md
---

# Review checklist — soft flag when Exclusions section missing

## Description

Per spec `out-of-scope-first-class.md` (8.3), add one line to the Stage 1 checklist in `ai-process/guidelines/review-checklist.md` that instructs the reviewer to soft-flag (not fail) when a spec's Exclusions section is absent or empty.

Exact wording to add: "Exclusions section is present and contains at least the human-confirmed answer (either concrete exclusions or an explicit 'no exclusions apply')."

The flag is advisory — reviewer surfaces the issue; Gate 1 does not auto-reject on it. Do not change any existing checklist line.

## Acceptance Criteria

AC-1: The `review-checklist.md` file Stage 1 section shall contain a line stating that the Exclusions section must be present and contain at least the human-confirmed answer.
AC-2: The new line shall be advisory wording (not phrased as an auto-reject condition).
AC-3: No existing Stage 1 checklist line shall be removed or reworded by this task.
AC-4: WHEN a reviewer runs Stage 1 on a spec THE SYSTEM SHALL expose the Exclusions-present check as one of the Stage 1 items.

## Dependencies

- None

## Files to Touch

- `ai-process/guidelines/review-checklist.md` — add one Stage 1 line for the Exclusions soft-flag

## Verification

```bash
grep -n "Exclusions section is present" ai-process/guidelines/review-checklist.md
```

## Notes

Reference: spec 8.3, Component 3.
T-013 (spec 8.7) will later reword a different line in this same file (handoff-note → Work Log). T-013 depends on this task to avoid conflicts.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->
