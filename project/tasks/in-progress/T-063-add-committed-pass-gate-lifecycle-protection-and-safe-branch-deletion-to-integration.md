---
id: T-063
title: Add committed-PASS gate, lifecycle protection, and safe branch deletion
  to integration
status: pending
priority: medium
assigned-role: unassigned
created: '2026-06-04'
---

# Add committed-PASS gate, lifecycle protection, and safe branch deletion to integration

## Description

Source: `full_skills_review.md` issues I3, I15. Edit the shared source bodies of `integrate`,
`dev-loop`, and `bug-loop`:

- **I3 (integration evidence):** `integrate` must verify the latest committed canonical PASS
  verdict on `dev-agent` before merging, require committed Developer handoffs, and reject
  lifecycle-file edits arriving on implementation branches; the loops must record committed
  handoffs and verdicts on `dev-agent` before integration.
- **I15 (safe deletion):** replace `integrate`'s routine forced-delete (`git branch -D`)
  fallback with stop-and-report (aligns with the guideline in T-060).

## Acceptance Criteria

AC-1: BEFORE merging, `integrate` SHALL verify that the latest committed canonical Review
      Verdict on `dev-agent` is PASS.
AC-2: The existing lifecycle-file guard (integrate stops when an implementation branch edits a
      canonical lifecycle file — already present in source) SHALL be retained and verified.
AC-3: WHEN `git branch -d` is refused, `integrate` SHALL stop and report instead of running
      `git branch -D`.
AC-4: dev-loop and bug-loop SHALL record committed Developer handoffs and Review Verdicts on
      `dev-agent` before invoking integration.

## Dependencies

- `T-059` — Gate 4 committed-PASS precondition defined in quality-gates first
- `T-060` — git-conventions guideline forbids forced deletion first
- `B-010` — also edits `dev-loop/body.md` and `bug-loop/body.md`; land first to avoid conflict

## Files to Touch

- `cli/src/ai_team/init/sources/skills/integrate/body.md` — committed-PASS gate, lifecycle guard, safe delete
- `cli/src/ai_team/init/sources/skills/dev-loop/body.md` — committed-evidence precondition
- `cli/src/ai_team/init/sources/skills/bug-loop/body.md` — committed-evidence precondition

## Verification

```bash
grep -niE "committed.*(pass|verdict)" cli/src/ai_team/init/sources/skills/integrate/body.md
grep -niE "lifecycle" cli/src/ai_team/init/sources/skills/integrate/body.md
! grep -nE "branch -D" cli/src/ai_team/init/sources/skills/integrate/body.md
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
