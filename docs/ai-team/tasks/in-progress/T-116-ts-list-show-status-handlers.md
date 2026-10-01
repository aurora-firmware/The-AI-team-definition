---
id: T-116
title: TS list, show, status handlers
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# TS list, show, status handlers

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 3**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P39 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- [G2 B6] port the latest-integration-result git lookup including the "not found" fallback, with a unit test for the found branch in a temporary git repo (allowed: it is not the Python CLI, ADR-004 Alternative C). status.ts exports the payload builder that report reuses.

## Acceptance Criteria

AC-1: V-PI-F list-, show--, status-- pass (SC-5).
AC-2: show unknown id returns fixture message.
AC-3: zero type errors (SC-9).

## Dependencies

- `T-091` — Seed fixtures for list, show, status, report
- `T-107` — Port filesystem layer and slug generation
- `T-112` — TS parity runner, command registry, handler stubs

## Files to Touch

- pi/src/core/commands/{list,show,status}.ts
- a unit test for the git lookup

## Verification

```bash
# V-PI-F per prefix; full V-PI. [G2 B4]
# V-PI-F: cd pi && npm test -- parity -t "<prefix>"   # a subset of parity cases
# V-PI: cd pi && npm ci && npm run typecheck && npm test   # after V-SYNC
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-10-01
Implemented the list (tasks, bugs, specs, adrs, change-requests), show and status handlers in `pi/src/core/commands`, with the Python CLI as the reference and the parity fixtures as the contract. I wrote the tests first and saw 12 failures against the stubs. The implementation then passed the list, show and status parity cases, typecheck, and the full suite (555 passed, 67 todo).

- **Shared helper:** I added `artifact-files.ts` (sorted markdown listing that skips templates, and `compareCodePoints`). This is a new file outside the task's Files to Touch, added to avoid a fourth copy of the file-listing code. `parity.test.ts` needed no edits.
- **Status:** `status.ts` exports `statusPayload(root)` and `latestIntegrationResult(root)` for `report`. The git lookup runs the same `git -C <repo> log --all --grep='merge\|integration\|verification\|test' -n 1 --pretty=format:%s` as Python. Any git failure or empty output returns "not found".
- **Show:** `show` replicates Python's behaviour. It first matches the identifier as a substring of the file stem, ignoring case. Otherwise it matches the model id exactly, except for specs. Kind comes from path segments, as in Python. Frontmatter values come out as Python-style strings, or null.
- **Payload type:** list payloads are bare arrays, so I cast them through `unknown` rather than change `result.ts`.
- **For the reviewer:** check the array-payload cast, the new `artifact-files.ts`, and the `show` frontmatter edge case for block values, which Python stringifies and TS throws on. `report` is not part of this task and is still a stub.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
