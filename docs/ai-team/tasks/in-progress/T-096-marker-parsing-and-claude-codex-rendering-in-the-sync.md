---
id: T-096
title: Marker parsing and claude/codex rendering in the sync
status: in-progress
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Marker parsing and claude/codex rendering in the sync

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P19 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- parse three marker kinds against the command map; reject unknown prefixes, unparseable content, flags undefined for the command; claude/codex render verbatim in bodies and [claude]/[codex] headers; wire into sync; test with synthetic bodies. [G2 B1] Update the fake-repo setup in test_init_scaffolds.py (it copies only the sync script, ~lines 171-175) to also copy the marker module and a minimal command map. Out of scope: pi rendering (T-098), skill source edits.

## Acceptance Criteria

AC-1: claude/codex render verbatim (marker contract).
AC-2: unknown kind/unparseable fails naming file and marker (SC-10).
AC-3: header markers rendered per target.
AC-4: unchanged sources pass V-GOLD (SC-2).

## Dependencies

- `T-087` — TS lock entry in skeleton .gitignore; update B-017 tests and usage guide
- `T-094` — Command map plus agreement test against the Typer CLI

## Files to Touch

- cli/scripts/sync_init_scaffolds.py
- new marker module in cli/scripts/
- new cli/tests/test_skill_markers.py
- cli/tests/test_init_scaffolds.py [G2 B1]

## Verification

```bash
# V-SYNC; V-GOLD; V-PY.
# V-SYNC: the sync command documented in CLAUDE.md's Build section (currently: cd cli && python scripts/sync_init_scaffolds.py)
# V-GOLD: git diff --exit-code "$(git merge-base HEAD main)" -- cli/src/ai_team/init/scaffolds/claude cli/src/ai_team/init/scaffolds/codex
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
Added `cli/scripts/skill_markers.py`. It parses `{{ai-team <argv>}}`, `{{ai-team-flag <command> <flags>}}` and `{{ai-team-cli|a|b}}` against the T-094 command map. The command is matched on the longest one- or two-word prefix.

Command markers reject flags not defined for the matched command. The check strips `[` and `]` and any `=value` first, so optional flags like `[--supersedes <ID>]` are validated too. Flag markers must name at least one flag, and every token must be a defined `--flag`. Noun markers need exactly two non-empty texts. Any other `{{...}}` prefix is an unknown kind. Errors are raised as `MarkerError` (a `ValueError`) naming the source file and the marker.

`sync_init_scaffolds.py` loads `command_map.json` from the sources directory, raising `FileNotFoundError` if it is missing. It renders each skill header (from `metadata.toml`) and body for claude and codex. `main` turns `ValueError` into `sys.exit("sync failed: ...")`, so a bad marker gives a clean non-zero exit.

Claude and codex render the marker content verbatim. The pi target raises an explicit error and is left for T-098. Tests use synthetic bodies and headers in a fake repo, so real sources needed no edits.

Command markers do not check positional counts or names. Call versus mention form is a pi-only distinction and belongs to T-098. Mixed-fence detection is also pi-only and not implemented here.

I rejected regex-level kind dispatch. Prefix checks run longest-first, because `ai-team-flag ` and `ai-team-cli|` both begin with `ai-team`.

Remaining: T-098 pi rendering, and converting skill bodies to markers, which is a separate task. The regenerated claude and codex scaffolds are unchanged.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-10-01
PASS

Stage 1: AC-1 met (claude/codex return marker content verbatim; parametrised tests over both targets). AC-2 met (MarkerError names source file and marker; sync exits non-zero with "sync failed"; tests cover body and header). AC-3 met (header and body both rendered per target in the sync). AC-4 met: after running the sync on the branch, `git status` shows no scaffold changes and V-GOLD diff against the merge-base with main is empty. Files changed match Files to Touch (plus no stray files); fake-repo setup updated per G2 B1.

Stage 2: `uv run pytest` 910 passed; `ruff format --check` and `ruff check` clean. Logic is sound (longest-prefix kind dispatch, flag validation incl. bracketed and `=value` forms), tests cover success and failure paths.

Non-blocking observations:
- `{{...}}` with a non-marker prefix is now always an error; fine today since no sources contain markers (test asserts this), but future skill text with literal `{{` will need care.
- Noun marker renders `parts[0]` only; pi text is validated but unused until T-098.
