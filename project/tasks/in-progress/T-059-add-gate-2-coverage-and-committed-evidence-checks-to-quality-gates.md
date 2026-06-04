---
id: T-059
title: Add Gate 2 coverage and committed-evidence checks to quality-gates
status: pending
priority: medium
assigned-role: unassigned
created: '2026-06-04'
---

# Add Gate 2 coverage and committed-evidence checks to quality-gates

## Description

Source: `full_skills_review.md` issues I7, I2, I3 (gate side). Update
`ai-process/processes/quality-gates.md` so the gate definitions match the reviewed skills:
Gate 2 must verify the task plan covers the spec before dependency/file-conflict checks (I7);
Gate 3 (code review) must include a bug-fix addendum requiring the diagnosis→fix evidence chain
(I2); Gate 4 (integration) must require the latest committed canonical PASS verdict on
`dev-agent` before merge (I3). Documentation only — the skill bodies are aligned in T-061,
T-063, and B-010.

## Acceptance Criteria

AC-1: The Gate 2 definition SHALL list spec-coverage verification as a check performed before
      dependency and file-conflict checks.
AC-2: The Gate 3 definition SHALL require, for bug fixes, a complete diagnosis→fix evidence
      chain (diagnosis fix-contract, regression test or justification, Fix Verification).
AC-3: The Gate 4 definition SHALL require the latest committed canonical PASS verdict on
      `dev-agent` before a branch is merged.

## Dependencies

- None

## Files to Touch

- `ai-process/processes/quality-gates.md` — Gate 2 coverage, Gate 3 bug addendum, Gate 4
  committed-PASS precondition

## Verification

```bash
grep -niE "coverage" ai-process/processes/quality-gates.md
grep -niE "committed.*(pass|verdict)" ai-process/processes/quality-gates.md
grep -niE "diagnosis|evidence chain|fix contract" ai-process/processes/quality-gates.md
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
