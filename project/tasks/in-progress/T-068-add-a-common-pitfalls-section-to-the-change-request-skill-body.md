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

### Session 1 — 2026-06-05

Picked up T-068 with an empty Work Log (first session). The task is a pure quality improvement: add a `## Common Pitfalls` section to `cli/src/ai_team/init/sources/skills/change-request/body.md`, matching the shape of the `new-spec` and `new-task` sibling skills.

The `claude_skills/` directory referenced by the task description did not exist in the working tree (the export path was stale), so I derived the Common Pitfalls content from the task's AC-2 specification and the established prose style of the `new-task` skill's existing Common Pitfalls section. The five bullets cover all four required misuses: using a CR when a full spec is warranted, vague change descriptions, missing affected-artifact list, missing risk notes, and inventing details instead of marking `[TODO]`.

TDD cycle followed:
1. Wrote `cli/tests/test_t068_change_request_common_pitfalls.py` with five tests — one for the `## Common Pitfalls` heading (AC-1) and four for the specific content requirements (AC-2, one per misuse). Initial versions of the AC-2 tests passed vacuously because the existing body already contained words like "spec", "description", "risk", and "TODO" in other sections; tightened them to extract and check only the `## Common Pitfalls` section using a helper function, making all five fail correctly.
2. Added the section to `body.md` between `## Quality Criteria` and `## Output Format` — the same placement pattern used by the `new-task` skill structure.
3. All five new tests turned green.

An unanticipated scaffold-parity test (`test_package_owned_skill_sources_include_body_and_required_metadata` in `test_init_scaffolds.py`) failed because it asserts the source body and the generated claude scaffold are byte-for-byte equal. The precedent from T-064 is to update both source and scaffold in the same commit rather than leave the suite broken. Updated both `scaffolds/claude/skills/change-request/SKILL.md` and `scaffolds/codex/skills/change-request/SKILL.md` with the same Common Pitfalls section. This is a justified deviation from the literal `Files to Touch` list — it maintains an existing green test that enforces a repo-wide integrity invariant, and it follows the pattern established by every prior task that edited a skill body.

Final state: 371/371 tests pass, ruff format and lint clean, task verification `grep -niE "common pitfalls"` returns line 38. Committed as a single cycle on the task branch.

Nothing remains for a follow-on session. T-067 (scaffold re-render) can proceed independently.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
