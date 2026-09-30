---
id: T-094
title: Command map plus agreement test against the Typer CLI
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Command map plus agreement test against the Typer CLI

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P17 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- single map (hand-authored or generated from Typer; choice recorded in Work Log) listing per leaf command positionals, flags incl. --json, defaults, allowed values, camelCase tool-field names; CLI-only options (--json, init --tools, --no-interactive) have no tool field; no version. Test fails on any disagreement with Typer.

## Acceptance Criteria

AC-1: every tool-contract leaf command with fields (ADR-004).
AC-2: disagreement fails the test.
AC-3: no version string (ADR-004).
AC-4: CLI-only options marked with no tool field.

## Dependencies

- `T-078` — Update the skill guide for the pi target and the marker contract
- `T-079` — Update the component map and system overview
- `T-080` — CLAUDE.md pi checks and setup-guide pi install steps

## Files to Touch

- new command-map source under cli/src/ai_team/init/sources/
- new cli/tests/test_command_map.py

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
Chose a hand-authored map, stored as `cli/src/ai_team/init/sources/command_map.json`, over one generated from Typer. A generated map could not catch a CLI change, because the test would compare Typer with itself. A separate table can disagree with the CLI, and then the test fails. I first dumped the real Typer surface (leaf commands, params, defaults, choices) and used that to build the JSON. The test helper that walks the Typer app produced the initial file, and I committed the result as a static file.

Each command entry has `positionals` (`cliName`, `field`, `required`, `default`) and `flags` (`flag`, `field`, `cliOnly`, `required`, `default`, `choices`, `boolean`). `--json`, `init --tools` and `init --no-interactive` are `cliOnly` with a null field. The map holds no version.

`cli/tests/test_command_map.py` has four checks:
- **Agreement with Typer:** compares the map to the live Typer app.
- **Tool contract:** compares the required and optional tool fields per command to a hard-coded copy of the S-005 tool-contract table.
- **CLI-only options:** checks that they carry no tool field.
- **No version:** checks that the map file contains no version string.

I also added mutation tests to show that disagreements are actually detected. Nothing was rejected beyond the generated-map option. Nothing remains for this task. The later sync and TS schema tasks will consume the JSON file.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
