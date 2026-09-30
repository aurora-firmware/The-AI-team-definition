---
id: T-092
title: Seed fixtures for validate and archive
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Seed fixtures for validate and archive

<!--
Task Quality Rules (see the new-task skill for full details):
  - Atomic — one clear outcome.
  - One-shottable — ≤ 3–4 files touched, ≤ 5 ACs, Description ≈ 20 lines.
  - Verifiable — concrete Verification command or explicit manual steps.
  - Self-contained — Description is enough to start without follow-up questions.
  - EARS — every AC matches one of the five EARS patterns below.
  - Dependency-honest — list every prior task this one reads from or modifies.
-->

## Description

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P15 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- validate each flag alone, combined, all, none; malformed frontmatter (missing fence, missing required key, invalid ID pattern); archive various olderThan values and dryRun; archive age boundary (one day before, on, one day after the cut-off, fixed clock).

## Acceptance Criteria

AC-1: every flag covered (SC-3).
AC-2: malformed frontmatter (SC-4).
AC-3: age boundary both sides and at cut-off (SC-4).
AC-4: Python runner passes (SC-5).

## Dependencies

- `T-088` — Parity fixture format and Python fixture runner

## Files to Touch

- case dirs validate--
- archive--

## Verification

```bash
# V-PY.
# V-PY: cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .   # set UV_CACHE_DIR under /tmp if uv cannot write its cache
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-10-01
Read the task, S-005 fixture format and the T-091 pattern. I wrote the coverage-contract tests first in `cli/tests/test_parity_validate_archive_fixtures.py` and confirmed all 17 failed. I then seeded the cases from the Python CLI with a throwaway scratchpad builder that calls `parity_support.record_case`.

For validate, one "broken" tree has a single error in each scope. A status/folder mismatch is the task error, a dangling task reference is the bug error, a bad id (`S-2`) is the spec error, a dangling `supersedes` is the ADR error, and a bad id (`CR-2`) is the change-request error. Each flag alone, the combined, `all` and no-flag runs use that tree, so scope isolation is visible in the findings. Clean-tree cases cover the exit-zero path. The malformed-frontmatter cases cover a missing fence, a missing required key (`title`) and an invalid id pattern (`T-3`).

For archive, a shared "aged" tree drives the 7d, 2w, 6m, 1y, 90d-default, 30d dry-run and explicit `dryRun` false, nothing-old-enough, invalid-value, empty-project and `0d` cases. `age-boundary` and `age-boundary-dry-run` pin the cut-off, with today at 2026-03-01 and `30d`: a day before is moved, and on the cut-off and a day after are kept. They do this for both completed tasks and resolved bugs, and they include a month-bucket crossing.

Tried and rejected: my first boundary dates assumed a cut-off of 01-31. The coverage test showed the real cut-off is 01-30, so I corrected the data and reseeded. I also narrowed the duration-unit test to successful cases, because the invalid `soon` value was being counted as a unit. No fixture uses task blocks without a Work Log heading, so B-018 does not affect them. Nothing remains for this task beyond review. The TS runner (later tasks) must match the recorded messages, including the `<ROOT>`-normalised frontmatter error text.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
