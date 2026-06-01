---
id: T-056
title: Prefix new spec filenames with S-NNN- identifier
status: completed
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

### Session 1 — 2026-06-01

This session implemented all five acceptance criteria for T-056 in four TDD cycles.

**What was done:**

Cycle 1 (AC-1): Updated `cli/src/ai_team/commands/spec.py` to construct the destination path as `S-NNN-<slug>.md` instead of `<slug>.md`. All existing spec_new tests were updated to expect the new path format. The overwrite-protection test required a monkeypatch of `next_spec_id` because the new naming scheme makes natural collisions impossible in sequential single-process runs (the allocator always increments past any `S-NNN-*.md` file it sees), so the test now simulates the race-condition edge case by forcing a fixed allocated ID.

Cycle 2 (AC-2 + AC-3): Replaced the single-pattern filename check in `cli/src/ai_team/core/validate.py` with a new `_check_spec_filename` helper. The helper accepts both `S-NNN-<slug>.md` (new style, with prefix-vs-frontmatter id verification) and `<slug>.md` (legacy, always valid). Three new tests were added covering: new-style valid, new-style with mismatched prefix, and legacy valid.

Cycle 3 (AC-4): Updated the `specs` subcommand in `cli/src/ai_team/commands/list.py` to read the spec id from `spec._source_map["id"]` rather than `path.stem`. Existing tests were updated (SPEC_TEMPLATE gained an `id` field; the table and JSON assertions were updated from `"ai-team-cli"` to `"S-001"`). A new dedicated test verifies the frontmatter-id-over-stem behaviour with an `S-007-my-spec.md` file.

Cycle 4 (AC-5): Ran the full `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` suite — all green (290 passed). Applied a minor ruff formatting fix to `validate.py`. Updated `cli/docs/usage.md` to describe the new `S-NNN-<slug>.md` convention and updated `cli/src/ai_team/init/sources/skills/new-spec/body.md` to note the filename format in step 3. Ran `sync_init_scaffolds.py` to propagate the skill source change.

**What was tried and rejected:** Initially attempted to test the overwrite-protection case by pre-seeding specs so the allocator would produce a colliding path — structurally impossible because any `S-NNN-*.md` file is picked up by the ID scanner and the allocator increments past it. Monkeypatching the allocator was the correct solution.

**What remains:** Nothing — all acceptance criteria are implemented, tested, and committed on `task/T-056-prefix-spec-filenames` (5 commits). Ready for review.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-01

PASS

Both stages passed.

**Stage 1 — Spec compliance:**
- AC-1: `commands/spec.py` builds `dest = root.specs / f"{spec_id}-{slug}.md"`. Four tests confirm path ends in `S-NNN-<slug>.md`. Met.
- AC-2: `_check_spec_filename` in `core/validate.py` accepts `S-NNN-<slug>.md` with matching frontmatter id and emits no finding. Test covers the valid case. Met.
- AC-3: `_check_spec_filename` falls through to `SLUGGED_FILENAME_RE` for legacy `<slug>.md` filenames — always accepted without a finding. Test covers the legacy case. Met.
- AC-4: `commands/list.py` reads `spec._source_map["id"]` for the ID column with fallback to `path.stem`. Tests updated to assert `"S-001"` rather than filename stem; dedicated prefixed-filename test added. Met.
- AC-5: 290 tests pass; `ruff check .` and `ruff format --check .` both clean. Verified locally on the task branch. Met.
- Scope constraint: No existing spec files in `project/specs/` or `project/specs/archive/` were renamed. `spec_slugs` construction and `_spec_reference_exists` are unchanged — task→spec reference resolution is untouched. Met.
- Files touched: All within the stated scope. Generated scaffolds regenerated via `sync_init_scaffolds.py`. `commands.md` confirmed up-to-date (no output change, no regeneration needed). Met.

**Stage 2 — Code quality:**
- Correctness: `split("-", 2)[:2]` correctly extracts the `S-NNN` prefix from new-style filenames. The fallback path in `_check_spec_filename` for neither-pattern filenames reports a clear error. The overwrite-protection test monkeypatches `next_spec_id` — justified by the allocator's design and documented in the Work Log.
- Tests: New tests cover all three validation cases (new-style valid, new-style prefix mismatch, legacy valid) and are independent using `tmp_path`.
- Security: No hardcoded credentials, no unvalidated external input, no queries.
- Readability: `_check_spec_filename` is focused, clearly named, and carries a docstring explaining both accepted forms.
- Performance: No concerns.

No minor observations.
