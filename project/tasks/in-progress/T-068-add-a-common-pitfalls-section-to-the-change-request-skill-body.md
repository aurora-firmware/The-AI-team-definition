---
id: T-068
title: Add a Common Pitfalls section to the change-request skill body
status: pending
priority: low
assigned-role: unassigned
created: '2026-06-04'
---

# Add a Common Pitfalls section to the change-request skill body

## Description

Source: `full_skills_review.md` (I9 follow-up — improvement, not a defect). The `change-request`
source body (`cli/src/ai_team/init/sources/skills/change-request/body.md`) has Input
Requirements, Procedure, Quality Criteria, and Output Format but lacks a **Common Pitfalls**
section — unlike the sibling artifact-creation skills (`new-spec`, `new-task`), which have one.
The Claude skills review already wrote suitable Common Pitfalls content in the export
(`claude_skills/skills/change-request/SKILL.md`); port it into the source body so it renders to
both platforms on the next sync (T-067). Pure quality improvement.

## Acceptance Criteria

AC-1: The `change-request` skill body SHALL include a Common Pitfalls section, consistent in
      shape with the `new-spec` and `new-task` skills.
AC-2: The Common Pitfalls section SHALL cover the common misuses — using a change-request when a
      full spec is warranted, vague change descriptions, missing affected-artifact or risk
      notes, and inventing details instead of marking `[TODO]`.

## Dependencies

- None

## Files to Touch

- `cli/src/ai_team/init/sources/skills/change-request/body.md` — add Common Pitfalls section

## Verification

```bash
grep -niE "common pitfalls" cli/src/ai_team/init/sources/skills/change-request/body.md
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
