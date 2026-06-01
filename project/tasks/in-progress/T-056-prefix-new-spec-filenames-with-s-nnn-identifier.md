---
id: T-056
title: Prefix new spec filenames with S-NNN- identifier
status: pending
priority: medium
assigned-role: developer
created: '2026-06-01'
---

# Prefix new spec filenames with S-NNN- identifier

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

Today `ai-team spec new` writes spec files as `<slug>.md` (see
`cli/src/ai_team/commands/spec.py`), while tasks/bugs/CRs use an
`<ID>-<slug>.md` filename. Specs already carry an `id: S-NNN` field in
frontmatter, so the filename is inconsistent with the rest of the artifacts.

Change new spec creation to write `S-NNN-<slug>.md`, mirroring
`commands/task.py` (`dest = root.tasks_pending / f"{task_id}-{slug}.md"`).

Scope is **new specs only** — do NOT rename existing files in
`project/specs/` or `project/specs/archive/`, and do NOT change task→spec
reference resolution. Because legacy `<slug>.md` specs remain on disk,
`validate` must accept BOTH the legacy `<slug>.md` form and the new
`S-NNN-<slug>.md` form so existing specs keep passing. `next_spec_id` in
`core/ids.py` already understands the `S-NNN-` filename pattern, so ID
allocation needs no change. `show` already matches `S-NNN` as a stem
substring, so it needs no change.

Update `list specs` to report the real `S-NNN` id from frontmatter rather
than `path.stem`, since the stem now contains the slug too.

## Acceptance Criteria

AC-1: WHEN `ai-team spec new "<title>"` runs THE SYSTEM SHALL create the
      file at `project/specs/S-NNN-<slug>.md`, where `S-NNN` is the
      allocated spec id, and print/emit that path.
AC-2: WHEN `ai-team validate --specs` runs over a spec named
      `S-NNN-<slug>.md` whose frontmatter `id` matches the prefix THE
      SYSTEM SHALL report no filename or id finding for it.
AC-3: WHILE a legacy `<slug>.md` spec (no id prefix) exists on disk THE
      SYSTEM SHALL still validate it without a filename-pattern finding.
AC-4: WHEN `ai-team list specs` runs THE SYSTEM SHALL show the `S-NNN`
      frontmatter id in the ID column, not the filename stem.
AC-5: The system shall keep `uv run pytest`, `uv run ruff check .`, and
      `uv run ruff format --check .` green from `cli/`.

## Dependencies

- None

## Files to Touch

- `cli/src/ai_team/commands/spec.py` — build `dest` as `S-NNN-<slug>.md`.
- `cli/src/ai_team/core/validate.py` — accept both legacy `<slug>.md` and
  new `S-NNN-<slug>.md` spec filenames; when an `S-NNN-` prefix is present
  verify it matches the frontmatter `id`.
- `cli/src/ai_team/commands/list.py` — derive the ID column from the spec
  frontmatter `id` instead of `path.stem`.
- `cli/tests/test_spec_new.py`, `cli/tests/test_validate.py`,
  `cli/tests/test_list.py` — update expected spec paths/ids and add a
  legacy-filename validation case.
- `cli/docs/usage.md` and
  `cli/src/ai_team/init/sources/skills/new-spec/body.md` — note the new
  `S-NNN-<slug>.md` filename; regenerate `cli/docs/commands.md` via
  `bash cli/scripts/gen_docs.sh` if command output changed.

## Verification

```bash
cd cli
uv run pytest
uv run ruff check .
uv run ruff format --check .
# Manual smoke: in a scratch project root, `ai-team spec new "Demo Spec" --json`
# should report a path ending in /specs/S-001-demo-spec.md
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
