---
id: "T-004"
title: "Brainstorm Step 2 — six-category structure with example pool and rules"
status: pending
priority: high
assigned-role: implementer
created: 2026-04-18
spec: project/specs/structured-brainstorm-categories.md
---

# Brainstorm Step 2 — six-category structure with example pool and rules

## Description

Per spec `structured-brainstorm-categories.md` (8.2), restructure `brainstorm/SKILL.md` Step 2 to scaffold the Planner's clarification questions around six named internal categories. The Planner uses the categories to plan coverage; categories are not exposed in the output.

Step 2 gains three blocks:

1. **Category list** — six named categories, one-line purpose each:
   1. Scope & Requirements (the exclusions question from spec 8.3 is the prominent item here)
   2. Technical Constraints
   3. Users & Surfaces
   4. Edge Cases & Error Handling
   5. Prior Decisions
   6. Verification
2. **Flat example question pool** — 12–15 illustrative questions, not grouped or labelled by category. A single question may draw on more than one category.
3. **Rules block** — replaces today's "Do not ask about" paragraph. Rules: (a) recommended ≤5 questions per round — recommendation, not a hard cap; (b) coverage of all six categories is required — ask more rounds if five cannot cover; (c) silent skip is acceptable when a category has no material unknown.

Questions the Planner asks the human must be plain prose — no `[Category]` tags.

Also cross-check `.claude/agents/planner.md` for references to Step 2 content that may drift (e.g. any reproduced "Ask about: …" list). Update any stale references found; if none, record that in the Notes section of this task.

## Acceptance Criteria

AC-1: The `brainstorm/SKILL.md` file Step 2 shall list exactly six internal categories with one-line purposes: Scope & Requirements, Technical Constraints, Users & Surfaces, Edge Cases & Error Handling, Prior Decisions, Verification.
AC-2: The Scope & Requirements category entry shall explicitly call out the exclusions question (from spec 8.3) as its prominent item.
AC-3: Step 2 shall contain a flat example question pool of 12–15 illustrative questions, with no per-category grouping and no `[Category]` labels.
AC-4: Step 2 shall state that five questions per round is a recommendation, not a cap, and that coverage of all six categories is the binding constraint.
AC-5: Step 2 shall state that silent skip of a category is acceptable when no material unknown exists for that category.
AC-6: The existing standalone "What is explicitly NOT included?" question introduced by T-002 shall remain present within (or clearly represented by) the Scope & Requirements category.
AC-7: WHEN `planner.md` contains a reference to the old Step 2 "Ask about:" list THE SYSTEM SHALL either update that reference to match the new structure or remove it.

## Dependencies

- `T-002` — Step 2 must already carry the standalone exclusions question, which this task absorbs into Scope & Requirements

## Files to Touch

- `.claude/skills/brainstorm/SKILL.md` — Step 2 restructure (categories + example pool + rules block)
- `.claude/agents/planner.md` — cross-check and update any stale Step 2 references

## Verification

```bash
# Six category names present in Step 2
for cat in "Scope & Requirements" "Technical Constraints" "Users & Surfaces" "Edge Cases & Error Handling" "Prior Decisions" "Verification"; do
  grep -q "$cat" .claude/skills/brainstorm/SKILL.md || { echo "MISSING: $cat"; exit 1; }
done
# Example pool size — at least 12 bullet items in Step 2 example block
grep -cE '^\s*-\s+' .claude/skills/brainstorm/SKILL.md
# No `[Category]` label tags leaked into output-facing text
! grep -nE '^\s*-\s*\[Category' .claude/skills/brainstorm/SKILL.md
# Standalone exclusions question preserved
grep -n 'NOT included' .claude/skills/brainstorm/SKILL.md
# Planner doc cross-check — no residual "Ask about:" list mirroring old Step 2
grep -n 'Ask about' .claude/agents/planner.md || true
```

## Notes

Reference: spec 8.2, Components 1–3.
Depends on T-002 being merged first. Both specs 8.3 and 8.2 modify `brainstorm/SKILL.md` Step 2; sequencing is load-bearing.

### Handoff Note — 2026-04-18

## What Was Done

- Restructured `.claude/skills/brainstorm/SKILL.md` Step 2 around the six required internal categories.
- Preserved the exclusions question as the prominent Scope & Requirements item and included it in the flat example question pool.
- Added a flat 14-question example pool with no category grouping or `[Category]` labels.
- Replaced the old "Ask about" / "Do not ask about" guidance with rules for recommended question count, six-category coverage, silent skip, and multi-round clarification.
- Cross-checked `.claude/agents/planner.md`; updated the stale hard "max five" reference to match the new recommended-count and coverage-first rule. No old "Ask about:" list remained there.
- Committed the implementation cycle as `ab48433` (`Update brainstorm clarification structure`).

## What Remains

- [ ] Reviewer pass for T-004.
- [ ] Integrate after review approval.

## Current State of Files

| File | State | Notes |
|---|---|---|
| `.claude/skills/brainstorm/SKILL.md` | modified | Step 2 now has six internal categories, a flat 14-question example pool, and coverage-first rules. |
| `.claude/agents/planner.md` | modified | Planner guidance no longer treats five questions as a hard cap. |
| `project/tasks/in-progress/brainstorm-step2-category-structure.md` | modified | Added this handoff note under Notes. |

## Known Issues

- No known implementation issues.
- The task verification command's bullet-count check counts bullets across the whole skill file, so I also ran a stricter local check that counted exactly 14 bullets inside the example question pool.

## Context for the Next Agent

- Categories are internal scaffolding only; Planner output should remain plain prose.
- Coverage of the six categories is the binding rule, but silent skip is acceptable when a category has no material unknown.
- The unrelated untracked `.codex/skills` path was present before this work and was not touched.

## Review

<!-- Reviewer appends verdict here after each review cycle. -->

### Review Verdict — 2026-04-18

PASS

Stage 1 spec compliance passed. `.claude/skills/brainstorm/SKILL.md` Step 2 lists exactly the six required internal categories with one-line purposes; Scope & Requirements prominently preserves "What is explicitly NOT included in this feature?"; the example pool is flat with 14 questions and no category labels; the rules make five questions a recommendation, make six-category coverage binding, and allow silent skip when no material unknown exists. `.claude/agents/planner.md` no longer preserves the stale hard "max five" guidance.

Stage 2 checklist review passed for this Markdown/process change. Visual diff inspection and command-line checks found no unexpected implementation behavior, no stale `Ask about:` list in `planner.md`, and no `[Category]` labels in output-facing question bullets.
