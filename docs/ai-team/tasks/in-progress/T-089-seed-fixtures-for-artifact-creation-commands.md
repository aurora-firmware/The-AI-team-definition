---
id: T-089
title: Seed fixtures for artifact-creation commands
status: pending
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Seed fixtures for artifact-creation commands

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 1**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P12 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- spec new (every status, author); task new (every priority, assignedRole, spec); bug new (every severity, task); adr new (every status, supersedes); change-request new; Unicode/punctuation titles; a long title exercising YAML folding; ID gaps and archived/completed-only IDs; artifact-exists errors where reachable. [G2 ruling 1c] One task-new case whose before-tree contains .ai-team.lock (pins ADR-003: TS is not blocked by the Python sentinel).

## Acceptance Criteria

AC-1: every creation command has a case (SC-3).
AC-2: every enum value appears (SC-3).
AC-3: Unicode/punctuation, folding title, ID gaps, archived IDs (SC-4).
AC-4: Python runner passes (SC-5).

## Dependencies

- `T-088` — Parity fixture format and Python fixture runner

## Files to Touch

- case dirs spec-new--
- task-new--
- bug-new--
- adr-new--
- change-request-new--

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

### Session 1 — 2026-09-30
I read the empty Work Log, the task and `fixtures/parity/README.md`. I wrote a coverage guard test first, `cli/tests/test_parity_creation_fixtures.py`, and watched it fail 22 of 22. The guard checks that each creation command has success and error cases, that every enum value appears, and that optional references are covered both present and absent. It also checks the Unicode, punctuation and long YAML-folding titles, and the ID-gap, archived/completed/resolved-only, frontmatter-ID and `.ai-team.lock` before-tree scenarios. I then seeded the cases with `seed_parity_fixture.py`, one command group per commit (77de7d2 spec + guard, fe1a4c5 task, 17743d5 bug, 189fe8e adr, 5eb235d change-request), and inspected the recorded payloads, messages and after-trees. In total that is 62 new cases (spec 16, task 21, bug 11, adr 9, change-request 6), bringing the suite to 63 cases including the existing `status--empty`.

The artifact-exists cases are reachable only by placing a directory named like the artifact file, because ID scanning counts files only. The first `adr new supersedes` case superseded itself, so I deleted and re-seeded it with an existing ADR-001 in the before-tree. A throwaway scratchpad script built the before-trees, since the helper takes one tree at a time.

Recorded quirks for the TS port to match: the ADR body keeps the `ADR-000: [Decision Title]` placeholder heading, and Unicode slugs are transliterated (e.g. `ri-ben-yu`).

Scope deviation: the guard test is outside the task's Files to Touch, and the reviewer should confirm that is acceptable. Full pytest (653 passed), `ruff format --check` and `ruff check` are green. Nothing remains for this task. Case names and content are now the reviewed contract and should be edited by hand only.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-09-30
PASS

Stage 1 (acceptance): met.
- AC-1: spec, task, bug, adr and change-request new each have success cases and an artifact-exists error case (62 new cases, 63 total).
- AC-2: every enum value is covered. Spec status (4) and author (4), task priority (4) and assignedRole (6), bug severity (4) and adr status (3) match the CLI `Literal` definitions. Optional spec, task and supersedes references are covered both present and absent.
- AC-3: Unicode, punctuation and a 180-character YAML-folding title are covered, as are ID gaps, archived-only (spec), completed-only and blocked-only (task) and resolved-only (bug) IDs. The task-new case with `.ai-team.lock` in the before-tree is present. The lock is correctly absent from the after-tree comparison per `lock-sentinels.json`.
- AC-4: from `cli/`, `uv run pytest` gives 653 passed, and `ruff format --check` and `ruff check` are clean.

Spot-checked fixtures (task-new defaults, role-unassigned, long-title-folding, adr unicode and supersedes, spec artifact-exists, blocked-only-ids, lock sentinel). Payloads, messages, IDs, slugs and after-tree file content are consistent with the CLI templates. The ADR `ADR-000: [Decision Title]` placeholder heading and the transliterated Unicode slug are real current behaviour, recorded faithfully and noted by the Developer for the TS port.

Scope deviation (`cli/tests/test_parity_creation_fixtures.py`): accepted. It is a test-only file with 131 lines and no production code. It only reads the fixtures, and fixtures are edited by hand rather than regenerated from either implementation, so the guard is the only thing that keeps AC-1 to AC-3 from regressing silently. It uses the existing `parity_support` helpers and is independent and deterministic. Risk is low.

Non-blocking observations:
- The guard hard-codes the enum sets, so a new CLI enum value will not fail the guard until someone updates it by hand.
- The task file `status:` frontmatter still reads `pending`. This is a lifecycle matter for the loop.

