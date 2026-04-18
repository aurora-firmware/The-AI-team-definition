---
id: "T-006"
title: "Write-plan skill — EARS authoring rule in Step 3 and quality criteria"
status: pending
priority: medium
assigned-role: implementer
created: 2026-04-18
spec: project/specs/ears-acceptance-criteria.md
---

# Write-plan skill — EARS authoring rule in Step 3 and quality criteria

## Description

Per spec `ears-acceptance-criteria.md` (8.1), update `write-plan/SKILL.md` to instruct the Planner to author every acceptance criterion using one of the five EARS patterns, pointing at `TEMPLATE-task.md` as the pattern reference.

Three changes in this single file:

1. **Step 3 (Write Task Files)** — replace the current "Acceptance criteria: Specific, measurable, checkable outcomes" bullet with an explicit EARS instruction. The instruction must direct the Planner to `TEMPLATE-task.md` for the pattern reference (avoid duplicating the pattern list in the skill).
2. **Quality Criteria** — add one bullet: "Every AC uses one of the five EARS patterns".
3. **Common Pitfalls** — replace the existing "Vague acceptance criteria" entry with: "Criteria that do not match an EARS pattern — if a criterion resists EARS, the task is probably not atomic".

Do not duplicate the pattern list in the skill; link out to the template.

## Acceptance Criteria

AC-1: The `write-plan/SKILL.md` file Step 3 shall instruct the Planner to author every acceptance criterion using one of the five EARS patterns.
AC-2: The Step 3 instruction shall point at `TEMPLATE-task.md` as the pattern reference rather than listing the five patterns inline in the skill.
AC-3: The `write-plan/SKILL.md` Quality Criteria section shall contain a bullet stating that every AC uses one of the five EARS patterns.
AC-4: The `write-plan/SKILL.md` Common Pitfalls section shall replace the "Vague acceptance criteria" entry with a new entry covering criteria that do not match an EARS pattern.
AC-5: IF the skill file contains an inline enumeration of all five EARS patterns THEN THE SYSTEM SHALL be considered failing this task.
AC-6: WHEN the Planner runs `/write-plan` THE SYSTEM SHALL direct them to author acceptance criteria in EARS form with reference to the task template.

## Dependencies

- `T-005` — skill links to the template Acceptance Criteria section, which must already be in its EARS form

## Files to Touch

- `.claude/skills/write-plan/SKILL.md` — Step 3 rewrite + Quality Criteria addition + Common Pitfalls replacement

## Verification

```bash
# Step 3 mentions EARS and points at TEMPLATE-task.md
grep -n 'EARS' .claude/skills/write-plan/SKILL.md
grep -n 'TEMPLATE-task.md' .claude/skills/write-plan/SKILL.md
# Quality Criteria bullet present
grep -n 'five EARS patterns' .claude/skills/write-plan/SKILL.md
# Old pitfall wording replaced
! grep -n 'Vague acceptance criteria' .claude/skills/write-plan/SKILL.md
# Pattern list not duplicated in the skill (rough check: pattern keywords shouldn't all appear)
# If all five appear together, the skill is probably duplicating the reference.
count=$(grep -cE 'Ubiquitous|Event-driven|Unwanted-behaviour|State-driven|Optional' .claude/skills/write-plan/SKILL.md)
[ "$count" -le 1 ] || echo "WARN: possible pattern duplication ($count matches)"
```

## Notes

Reference: spec 8.1, Component 2.
Soft dependency on T-005 — the skill links out to the template, so the template must exist in its EARS form first.

### Handoff Note — 2026-04-18

## What Was Done

- Updated `.claude/skills/write-plan/SKILL.md` Step 3 so the Planner must author every acceptance criterion using one of the five EARS patterns.
- Pointed the Step 3 instruction to `.claude/skills/new-task/assets/TEMPLATE-task.md` as the pattern reference without duplicating the five patterns inline.
- Added the Quality Criteria bullet requiring every AC to use one of the five EARS patterns.
- Replaced the old "Vague acceptance criteria" pitfall with the required EARS-pattern atomicity pitfall.
- Ran the task's command-line acceptance checks as the adapted red/green verification for this Markdown/process repository.

## What Remains

- [ ] Reviewer should confirm the wording satisfies spec 8.1, Component 2.
- [ ] Reviewer should rerun the verification commands if desired.

## Current State of Files

| File | State | Notes |
|---|---|---|
| `.claude/skills/write-plan/SKILL.md` | modified | Step 3, Quality Criteria, and Common Pitfalls now enforce EARS authoring through the task template reference. |
| `project/tasks/in-progress/write-plan-ears-authoring-rule.md` | modified | Added this handoff note under Notes. |

## Known Issues

- None found.

## Context for the Next Agent

- The skill intentionally references `.claude/skills/new-task/assets/TEMPLATE-task.md` instead of listing the five EARS patterns inline.
- The task file's verification command for pattern duplication is a rough keyword check; it returns zero matches for the updated skill.
- Existing untracked `.codex/skills` content was present before this work and was left untouched.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->

### Review Verdict — 2026-04-18

PASS

Stage 1 passed: all six acceptance criteria are satisfied in `.claude/skills/write-plan/SKILL.md`, with Step 3 directing EARS authoring through `TEMPLATE-task.md`, the Quality Criteria bullet added, the Common Pitfalls entry replaced, and no inline enumeration of all five EARS patterns.

Stage 2 passed for this Markdown/process change using visual diff inspection and command-line checks. No blocking findings.
