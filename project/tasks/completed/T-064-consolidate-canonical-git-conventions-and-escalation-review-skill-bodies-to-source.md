---
id: T-064
title: Consolidate canonical git-conventions and escalation-review skill bodies
  to source
status: completed
priority: medium
assigned-role: unassigned
created: '2026-06-04'
---

# Consolidate canonical git-conventions and escalation-review skill bodies to source

## Description

Source: `full_skills_review.md` issues I1, I5 (plus the content-boundary canonical from the
review). Bring the shared source bodies up to the reviewed canonical state:

- **I1 (git rules):** `git-conventions` body exposes stable, citable headings for branch model,
  commit format, the per-role commit table, and hard rules, so other skills reference rather
  than restate them.
- **I5 (escalation):** `escalation-review` body is the single impasse handler with a frozen
  four-field request block, an Escalation Verdict block, and the canonical Phase 2 Human
  Escalation Report template.
- **Content boundary:** port the canonical content-boundary rule into `new-spec` and trim the
  `brainstorm` restatement to a one-line pointer.

## Acceptance Criteria

AC-1: The `git-conventions` body SHALL expose stable headings for branch model, commit format,
      per-role commits, and hard rules that other skills can cite.
AC-2: The `escalation-review` body SHALL contain the frozen four-field request block, the
      Escalation Verdict block, and the canonical Phase 2 Human Escalation Report template as
      the single source.
AC-3: The `new-spec` body SHALL hold the canonical content-boundary rule, and the `brainstorm`
      body SHALL reference it rather than restate it.

## Dependencies

- `B-008` — also edits `escalation-review/body.md` (new-adr contract); land first to avoid conflict

## Files to Touch

- `cli/src/ai_team/init/sources/skills/git-conventions/body.md` — canonical headings
- `cli/src/ai_team/init/sources/skills/escalation-review/body.md` — frozen blocks + Phase 2 template
- `cli/src/ai_team/init/sources/skills/new-spec/body.md` — canonical content-boundary rule
- `cli/src/ai_team/init/sources/skills/brainstorm/body.md` — content-boundary pointer

## Verification

```bash
grep -nE "^## " cli/src/ai_team/init/sources/skills/git-conventions/body.md
grep -niE "phase 2|escalation request|verdict" cli/src/ai_team/init/sources/skills/escalation-review/body.md
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-04

Implemented T-064 in a single session. All three acceptance criteria were addressed.

**AC-1 (git-conventions stable headings):** The four citable headings (`## Branch Model`, `## Commit Message Format`, `## When Each Role Commits`, `## Hard Rules`) were already present in the source. The only missing change was removing `## Quality Criteria`, which the full_skills_review identified as a mere restatement of Hard Rules that undermined Hard Rules as the sole authority. Removed it; wrote a test that asserts the section is absent.

**AC-2 (escalation-review frozen block + verdict + Phase 2):** The Escalation Verdict block and Phase 2 Human Escalation Report template were already in the source. What was missing was an explicit `## Escalation Request Block (FROZEN)` top-level section with a copy-ready fenced block of the four field names. Added that section between Input Requirements and Procedure. The Input Requirements bullet for "Structured request" was updated to point to the new section. B-008's `description` (not `context`) fix for the new-adr invocation was already present and was preserved without regression.

**AC-3 (new-spec canonical; brainstorm pointer):** Both files were already in the correct state. `new-spec` holds the full `## Content-boundary rule (strict)` section including the `Rare exception` clause. `brainstorm` Step 7 carries a one-line inline reference ("It carries the **content-boundary rule**... apply them through that skill rather than re-deriving them here") and the Common Pitfalls reminder is a short two-sentence pointer, not the full four-paragraph rule. Tests confirmed this without requiring source changes.

**What was rejected:** Considered also trimming the brainstorm Common Pitfalls item ("Embedding the implementation in the spec...") to a literal one-line pointer. Decided against it: the item is already a brief two-sentence reminder that names the pitfall concisely, not a full rule restatement. The test suite confirms it passes the AC-3 criteria, and removing content from Common Pitfalls would reduce actionable guidance without benefit.

Scaffolds were regenerated with `python3 cli/scripts/sync_init_scaffolds.py`. All 353 tests pass; ruff format and check are clean.

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

Both stages passed.

**Stage 1 — Spec compliance:**

- AC-1: Confirmed. `git-conventions/body.md` exposes the four stable citable headings (`## Branch Model`, `## Commit Message Format`, `## When Each Role Commits`, `## Hard Rules`). The `## Quality Criteria` section — which merely restated Hard Rules — was removed, leaving Hard Rules as the sole authority. Scaffolds for both claude and codex match the source.

- AC-2: Confirmed. `escalation-review/body.md` now contains the `## Escalation Request Block (FROZEN)` top-level section with the copy-ready four-field fenced block. The Escalation Verdict block and Phase 2 Human Escalation Report template were already present and remain. B-008's `description` (not `context`) fix for the new-adr invocation was preserved without regression — verified by direct inspection and the test `test_escalation_review_new_adr_invocation_uses_description_not_context`. The `status: accepted` addition to the new-adr invocation is a correct preservation of B-008's fix (that fix added `status` in its own commit). Scaffolds for both tools match.

- AC-3: Independently verified. `new-spec/body.md` holds the full `## Content-boundary rule (strict)` section including the `Rare exception` clause. `brainstorm/body.md` contains a one-line inline pointer to `new-spec` at Step 7 and in Common Pitfalls, without restating the `Rare exception` clause or the full four-paragraph rule. No source changes were needed for AC-3, consistent with the Developer's claim. Scaffolds confirmed.

- Scope: The single implementation commit (884994c) touches only the six in-scope source/scaffold files plus the new test file. All other file changes visible in `git diff main...` are from prior merged tasks on this branch, not from T-064.

- Verification greps from the task both pass as expected.

**Stage 2 — Code quality:**

- Tests: `cli/tests/test_t064_skill_bodies_canonical.py` adds 18 tests covering each AC. Tests cover source bodies and both claude/codex scaffolds. All 353 tests pass. Tests are independent (no shared mutable state).
- Correctness: Logic is sound. Tests read source and scaffold files directly with no mocking gaps.
- Ruff format and lint checks both clean.
- No dead code, hardcoded secrets, or unrelated behavior introduced.
