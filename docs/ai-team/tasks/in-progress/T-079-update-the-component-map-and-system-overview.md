---
id: T-079
title: Update the component map and system overview
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Update the component map and system overview

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 0**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P2 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- add pi/ package and adapter, TS core, command map, sync pi target and generated pi/resources/ (incl. git-ignored version file), fixtures/parity/ contract and two runners, per-implementation locks (ADR-003), co-equal implementations (ADR-004); map CLI commands to ai_team tool commands. Out of scope: guides, CLAUDE.md, code.

## Acceptance Criteria

AC-1: each new component with owning path and interface (SC-1).
AC-2: flow sync→pi resources→adapter→TS core, fixtures bind both implementations (SC-1, ADR-004).
AC-3: own locks, mixed concurrency unsupported (ADR-003).
AC-4: pi/resources generated never hand-edited; claude/codex exports unchanged.

## Dependencies

- None

## Files to Touch

- ai-process/architecture/component-map.md
- ai-process/architecture/system-overview.md

## Verification

```bash
# grep for pi/ / parity / command map; V-PY.
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

I read the task, the S-005 spec (system diagram, responsibility table, tool contract, lock and version configuration) and ADR-003, and confirmed that neither architecture doc mentioned `pi/`. I added a "Pi Extension Components" table, a "Generation Flow" diagram and a "Pi Tool Command Mapping" table to `ai-process/architecture/component-map.md`. I also added a "Pi Extension Layer" section and a design decision 7 to `ai-process/architecture/system-overview.md`, and extended the existing decision 6 to note that the `pi` target reads the same sources. Committed on `task/T-079-component-map-system-overview` as `b97549d`.

I kept the statements about generated resources, the unchanged claude/codex exports, per-implementation locks and unsupported mixed concurrency explicit. The edits are docs only, and the existing CLI Command Mapping table is unchanged. I rejected adding a new pytest doc-check file because it is outside Files to Touch. The paths `pi/src/` and the runner locations (pytest runner under `cli/tests/`, vitest runner under `pi/`) are my best reading of the spec, which leaves the layout open. The Phase 2 and 3 tasks should confirm or correct them. Verification: grep for `pi/` was 0 before and 17/6 hits after; pytest 461 passed, ruff format and check clean. Nothing else remains for this task.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-09-30
FAIL

Reviewed `b97549d` on `task/T-079-component-map-system-overview` against `feat/pi-extension`, S-005 and ADR-001..004. Stage 1 fails on one point; Stage 2 was skipped per the skill.

Verified as correct:
- The "Pi Tool Command Mapping" table matches the S-005 Tool contract row for row. Every command, required and optional field, and camelCase flag name agrees, and so do the `init` omissions (`--tools`, `--no-interactive`) and the "no `json` field" rule.
- The table also matches the actual CLI (`ai-team <cmd> --help`). Flags, positionals, `task block --reason`, and the `validate`, `archive` and `init` flags are all covered.
- AC-1 to AC-3 content agrees with the S-005 system diagram, ADR-003 (separate locks, mixed concurrent allocation unsupported) and ADR-004 (co-equal, shared fixtures, two runners).
- AC-4: generated `pi/resources/` is stated as never hand-edited. The claude/codex exports are unchanged apart from the deliberate TS lock `.gitignore` entry, which S-005 and ADR-003 sanction.
- Only the two files in "Files to Touch" were changed in the docs.

Failed check:
- **Provisional paths asserted as settled.** S-005 never names `pi/src/` or the runner locations. It says only "a `pi/` npm package beside `cli/`", "One pytest runner and one vitest runner", and `fixtures/parity/`. The Developer's Work Log admits these are a "best reading" that later tasks should confirm. The docs nonetheless present them as fact.
  - `ai-process/architecture/component-map.md`, "Pi Extension Components" table, rows "Pi adapter" (`pi/src/ (extension entry)`) and "TS artifact core" (`pi/src/ (pure core modules)`).
  - Same table, row "Fixture runners": `pytest runner under cli/tests/; vitest runner under pi/`.
  - The intro sentence "All paths are repo-relative" adds further authority to these paths.
  - The TS lock row is already correctly left unspecified, so these rows are inconsistent with it.
  - What should change: either drop the unspecified sub-paths and use spec-level owners (`pi/` for the adapter and TS core, "one pytest runner and one vitest runner" with no location), or keep them but mark them explicitly as provisional and not spec-binding (for example "provisional layout, to be confirmed by the Phase 2/3 tasks"). Put the marker in the table itself or in the sentence directly above it, not only in the Work Log.

Non-blocking: the Generation Flow block is fine as is. No Verification rerun was needed for a docs-only change; the Developer reported pytest 461 passed and ruff clean.

Next owner: Developer (via the Development Loop).
