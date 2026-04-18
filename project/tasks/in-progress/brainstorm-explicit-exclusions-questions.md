---
id: "T-002"
title: "Brainstorm skill — explicit exclusions question in Step 2 and Step 6"
status: pending
priority: high
assigned-role: implementer
created: 2026-04-18
spec: project/specs/out-of-scope-first-class.md
---

# Brainstorm skill — explicit exclusions question in Step 2 and Step 6

## Description

Per spec `out-of-scope-first-class.md` (8.3), update `brainstorm/SKILL.md` so exclusions are actively elicited during the clarification round and reaffirmed during the confirmation round.

In Step 2 (Clarification Round), add a named, standalone question: "What is explicitly NOT included in this feature?" The question must not be buried as a sub-bullet inside the "ask about" list; it is a named prompt of its own.

In Step 6 (Confirm the Approach), require that the confirmation summary include an exclusions line — either one or more concrete exclusions, or an explicit statement "no exclusions apply" when the human confirms there are none.

Do not alter the other steps.

## Acceptance Criteria

AC-1: The `brainstorm/SKILL.md` file Step 2 shall contain a standalone, named question asking the human what is explicitly NOT included in the feature.
AC-2: The standalone exclusions question in Step 2 shall not be represented as a sub-bullet inside the existing "ask about" list.
AC-3: The `brainstorm/SKILL.md` file Step 6 shall require the confirmation summary to contain an exclusions line with either concrete exclusions or the explicit statement "no exclusions apply".
AC-4: WHEN the Planner runs the brainstorm skill THE SYSTEM SHALL present the exclusions question as a named prompt during Step 2.
AC-5: IF the human answers "no exclusions apply" THEN THE SYSTEM SHALL accept that statement verbatim in the Step 6 summary without requiring a concrete list.

## Dependencies

- None

## Files to Touch

- `.claude/skills/brainstorm/SKILL.md` — add Step 2 standalone exclusions question; add Step 6 exclusions line requirement

## Verification

```bash
# Step 2 contains the standalone exclusions question
grep -n 'NOT included' .claude/skills/brainstorm/SKILL.md
# Step 6 mentions exclusions line / no exclusions apply
grep -nE 'exclusions (line|apply)' .claude/skills/brainstorm/SKILL.md
```

## Notes

Reference: spec 8.3, Component 2.
This task precedes T-004 (spec 8.2 restructures Step 2 into a six-category block that absorbs this exclusions question).

### Handoff Note — 2026-04-18

## What Was Done

- Updated `.claude/skills/brainstorm/SKILL.md` Step 2 to include a standalone named prompt: "What is explicitly NOT included in this feature?"
- Kept the Step 2 exclusions prompt outside the existing "Ask about" list so it is presented as its own prompt.
- Updated Step 6 to require an exclusions line with concrete exclusions or the exact statement "no exclusions apply" when the human confirms there are none.
- Verified the task acceptance checks with command-line inspections.

## What Remains

- [ ] Reviewer should review the two brainstorm skill edits against AC-1 through AC-5.
- [ ] Integrator should move the task file according to the project workflow after review approval.

## Current State of Files

| File | State | Notes |
|---|---|---|
| `.claude/skills/brainstorm/SKILL.md` | modified | Step 2 now actively elicits explicit exclusions; Step 6 now requires an exclusions line and accepts "no exclusions apply" verbatim. |
| `project/tasks/in-progress/brainstorm-explicit-exclusions-questions.md` | modified | Added this handoff note under Notes. |

## Known Issues

- None known.

## Context for the Next Agent

- This task intentionally makes the minimal T-002 update only; T-004 is expected to restructure Step 2 later and should preserve this exclusions prompt.
- There is an unrelated untracked `.codex/skills` path in the working tree that was not touched.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->
