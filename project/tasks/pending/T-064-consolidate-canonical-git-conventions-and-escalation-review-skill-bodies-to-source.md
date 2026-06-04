---
id: T-064
title: Consolidate canonical git-conventions and escalation-review skill bodies
  to source
status: pending
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

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
