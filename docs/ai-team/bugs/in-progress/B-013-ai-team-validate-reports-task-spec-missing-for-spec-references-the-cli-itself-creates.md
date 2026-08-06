---
id: B-013
title: ai-team validate reports task-spec-missing for spec references the CLI 
  itself creates
severity: high
status: in-progress
created: '2026-08-05'
---

# ai-team validate reports task-spec-missing for spec references the CLI itself creates

## Summary

`ai-team validate` emits `task-spec-missing` for tasks whose `spec:` reference
resolves perfectly well, because the validator indexes specs by **filename stem**
rather than by frontmatter `id`. Since `ai-team spec new` names spec files
`S-NNN-<slug>.md`, neither of the two natural reference forms — the spec id
(`S-002`) nor the plain slug (`coordinated-process-and-cli-workflow-improvements`)
— matches the index. Only the full stem `S-002-coordinated-process-and-cli-workflow-improvements`
resolves. The check therefore fires on the CLI's own happy path, and its findings
cannot be trusted to mean "this task references a spec that does not exist".

## Reproduction Status

Status: confirmed

Reproduced twice: in this repository (`ai-team validate` → 12 findings, all
`task-spec-missing`) and in a clean scratch project built entirely with
`ai-team init` / `ai-team spec new` / `ai-team task new`, where the false
positive appears on the first task ever created.

## Evidence

- Logs / stack traces / failing assertions:

  ```
  $ ai-team spec new --json "First architecture spec"
  {"id": "S-001", "path": ".../project/specs/S-001-first-architecture-spec.md"}

  $ ai-team task new "Implement thing one" --spec S-001 --json
  {"id": "T-001", "path": ".../project/tasks/pending/T-001-implement-thing-one.md"}

  $ ai-team validate --tasks --json
  [{"path": "project/tasks/pending/T-001-implement-thing-one.md",
    "level": "error", "code": "task-spec-missing",
    "message": "Task spec reference 'S-001' does not resolve to an existing spec file."}]
  ```

  Rewriting the reference to the legacy slug `first-architecture-spec` produces
  the same finding. `ai-team show S-001` resolves the spec without issue.

- Screenshots or recordings: n/a
- Failing command or test: `ai-team validate --tasks` in any project whose specs
  use the `S-NNN-<slug>.md` filename convention.
- Source inspection:
  - `cli/src/ai_team/core/validate.py:189` builds the index as
    `spec_slugs = {path.stem for path in _iter_markdown_files(root.specs) ...}`.
  - `cli/src/ai_team/core/validate.py:167` `_spec_reference_exists` matches a
    reference only against a stem, or a stem plus a stripped `.md` suffix. The
    spec frontmatter `id` is never consulted.
  - `root.specs / "archive"` is not indexed either, so any reference to an
    archived spec is also reported missing.

## Reproduction Steps

1. `ai-team init --no-interactive --tools claude` in an empty directory.
2. `ai-team spec new --json "First architecture spec"` → creates
   `project/specs/S-001-first-architecture-spec.md` with `id: S-001`.
3. `ai-team task new "Implement thing one" --spec S-001 --json`.
4. `ai-team validate --tasks`.
5. Observe a `task-spec-missing` finding for `S-001`.

## Expected Behavior

A task whose `spec:` value names an existing spec must not produce a
`task-spec-missing` finding. Resolution should accept at least:

- the spec frontmatter `id` (`S-001`),
- the full filename stem (`S-001-first-architecture-spec`), with or without `.md`,
- the legacy bare slug (`first-architecture-spec`) for specs created before the
  `S-NNN-` filename prefix existed.

Specs under `specs/archive/` should resolve as well, since tasks completed
against a since-archived spec are otherwise permanently flagged.

## Actual Behavior

Only the exact filename stem resolves. Both `spec: S-001` (the form `ai-team
task new --spec` records) and `spec: first-architecture-slug` (the legacy form)
are reported as:

```
error  task-spec-missing  Task spec reference 'S-001' does not resolve to an existing spec file.
```

In this repository the check produces 12 findings, 100% of them false positives.
The reporting project observed 112 of 114 total findings from this one code,
rendering `ai-team validate` unusable as a signal.

## Environment

- OS / platform: Linux
- Language / runtime version: Python 3.14, `ai-team` CLI 0.10.1
- Relevant dependencies: `cli/src/ai_team/core/validate.py`
- Branch / commit: `dev-agent`, inspected 2026-08-05

## Related

- Task: n/a
- Specification: n/a
- External evidence: `/home/daneel/projects/the-intern/ai-process-cli-reported-issues.md`,
  entry dated 2026-08-01

## Suspected Area

`cli/src/ai_team/core/validate.py` — the `spec_slugs` index built in
`validate_project` and the `_spec_reference_exists` matcher.

## Fix Verification

```bash
# In a scratch project created with `ai-team init`:
ai-team spec new --json "First architecture spec"
ai-team task new "Implement thing one" --spec S-001 --json
ai-team validate --tasks --json   # must return []

# Regression coverage in the CLI test suite:
cd cli && uv run pytest
```

Additionally, `ai-team validate` from this repository root must report zero
`task-spec-missing` findings.

## Diagnosis Log

<!-- Mandatory before implementation. Append one entry before changing production code. Format:
### Diagnosis N — YYYY-MM-DD
Reproduction status:
Evidence captured:
Isolated fault:
Root cause or fault hypothesis:
Planned verification:
-->

### Diagnosis 1 — 2026-08-06

Reproduction status: confirmed. Reproduced directly against this repository's
configured project directory (`docs/ai-team`, per `.ai-team.toml`), which is the
canonical project artifact set for this repo.

Evidence captured:

- `uv run --project cli ai-team validate --tasks --json` (from the repo root)
  returned 12 `task-spec-missing` findings, all against tasks T-044 through
  T-055, each with message: "Task spec reference
  'coordinated-process-and-cli-workflow-improvements' does not resolve to an
  existing spec file."
- The referenced spec exists:
  `grep -n "^spec:" docs/ai-team/tasks/completed/T-044-update-spec-breakdown-docs-and-test-planning.md`
  returns `spec: coordinated-process-and-cli-workflow-improvements`, and
  `docs/ai-team/specs/S-002-coordinated-process-and-cli-workflow-improvements.md`
  exists with frontmatter `id: S-002`.
- Archive exclusion confirmed: a non-recursive `Path('docs/ai-team/specs').glob('*.md')`
  yields only S-002, S-003, and S-004 — `docs/ai-team/specs/archive/*.md` is
  excluded because the glob is scoped to a single directory.
- `cli/src/ai_team/core/validate.py:189-191` builds
  `spec_slugs = {path.stem for path in _iter_markdown_files(root.specs) if path.suffix == ".md"}`,
  producing only full stems — neither the frontmatter `id` nor the bare slug is a
  member.
- `cli/src/ai_team/core/validate.py:167-172` `_spec_reference_exists` only checks
  `reference in spec_slugs`, or the same with a stripped `.md` suffix. Frontmatter
  `id` is never consulted.
- `cli/src/ai_team/commands/spec.py:58-64` (`ai-team spec new`) sets
  `source_map["id"] = spec_id` and names the file `f"{spec_id}-{slug}.md"`, so
  every CLI-created spec has stem `S-NNN-<slug>` — never the bare id or bare slug.
- `cli/src/ai_team/commands/task.py:162,181` (`ai-team task new --spec`) records
  the literal `--spec` value verbatim, so `--spec S-001` records `spec: S-001`,
  which can never be a member of `spec_slugs` as currently built.
- `cli/src/ai_team/core/models.py:231-235` — the `Spec` dataclass has no `id`
  field at all (docstring states "specs have no id in their frontmatter"), even
  though `ai-team spec new` writes one. Any fix matching on frontmatter `id` must
  read it from raw frontmatter rather than the current `Spec` model.
- `cli/tests/test_validate.py` `_seed_valid_project` (lines 96-98, ~106) only
  exercises the legacy filename case (`specs/roadmap-spec.md` with
  `spec: "roadmap-spec"`, where stem == reference by coincidence). No existing
  regression test covers an `S-NNN-<slug>.md` spec referenced by bare id or bare
  slug — exactly the false-positive path in this bug.
- Precedent for the fix shape lives in the same file: `_existing_task_ids`
  (`validate.py:380-393`) and `_existing_adr_ids` (`validate.py:396-403`) build
  ID-based indexes by parsing each artifact's `id` field, not by filename stem.

Isolated fault: `cli/src/ai_team/core/validate.py:189-191` (the `spec_slugs` index
built in `validate_project` from `path.stem` over a non-recursive, single-directory
glob of `root.specs`) and `cli/src/ai_team/core/validate.py:167-172`
(`_spec_reference_exists`, which matches only against that stem-only index, with
or without a `.md` suffix, and never consults frontmatter `id`).

Root cause or fault hypothesis: Root cause, evidence-backed. The spec
cross-reference index conflates three distinct identifiers that `ai-team` treats
as valid ways to name a spec — the frontmatter `id` (`S-002`), the full filename
stem (`S-002-coordinated-process-and-cli-workflow-improvements`), and the legacy
bare slug (`coordinated-process-and-cli-workflow-improvements`) — into a single
stem-derived value. Since `ai-team spec new` always produces `S-NNN-<slug>.md`
filenames and `ai-team task new --spec` records whatever the caller passes
(typically the bare `S-NNN` id), the stem index almost never matches the reference
form the CLI itself produces on its own happy path. The same root cause excludes
`root.specs / "archive"` entirely, because `_iter_markdown_files` performs a
non-recursive `*.md` glob scoped to one directory, so references to archived specs
are reported missing regardless of form. A secondary related gap: `Spec` and
`parse_spec` (`cli/src/ai_team/core/models.py:231-249`) do not model spec
frontmatter `id`, so an id-based index must either extend `Spec`/`parse_spec` or
read frontmatter directly in `validate.py`.

Planned fix contract (implementation target for the tdd cycle):

1. In `validate_project` (`cli/src/ai_team/core/validate.py`), replace the single
   `spec_slugs: set[str]` stem index with one that also captures (a) each spec's
   frontmatter `id` — read from raw frontmatter, closing the `Spec`/`parse_spec`
   id-modelling gap by either adding an `id: str | None` field to `Spec` populated
   in `parse_spec` via `data.get("id")`, or reading frontmatter directly in
   `validate.py` — and (b) the bare slug with any `S-NNN-` prefix stripped from
   the stem. Extend the scanned folders to include `root.specs / "archive"`,
   closing the archive indexing gap.
2. Update `_spec_reference_exists` (or its call site) to accept a reference
   matching any of: the frontmatter `id`, the full filename stem (with or without
   a trailing `.md`), or the bare legacy slug.
3. Add regression coverage in `cli/tests/test_validate.py` for (a) a task
   referencing a spec by frontmatter `id` (`S-001`) where the spec file uses the
   `S-NNN-<slug>.md` convention, (b) the same referenced by bare legacy slug, and
   (c) a task referencing a spec under `specs/archive/`.
4. Ensure `test_validate_emits_error_when_cross_references_do_not_resolve` (a
   genuinely missing spec, `spec: "missing-spec"`) still produces a
   `task-spec-missing` finding — the fix must widen acceptance without suppressing
   true negatives.

Planned verification: `uv run --project cli ai-team validate --tasks --json` from
the repo root must return `[]` (baseline before fix: 12 findings, captured above).
`cd cli && uv run pytest` must pass in full, including the new regression tests in
item 3. Additionally run the bug's own Fix Verification block: in a scratch
project, `ai-team spec new --json "First architecture spec"` →
`ai-team task new "Implement thing one" --spec S-001 --json` →
`ai-team validate --tasks --json` must return `[]`.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-08-06

Implemented the fix contract from the recorded Diagnosis Log. Root cause was that
`validate_project` in `cli/src/ai_team/core/validate.py` indexed specs only by full
filename stem (`{path.stem for path in _iter_markdown_files(root.specs) ...}`), so a
task's `spec:` reference had to match the entire `S-NNN-<slug>` stem exactly —
neither the bare frontmatter `id` (`S-001`) nor the bare legacy slug
(`first-architecture-spec`) ever matched, and `specs/archive/` was excluded entirely
because `_iter_markdown_files` globs a single non-recursive folder.

Followed TDD: first added five regression tests to `cli/tests/test_validate.py` —
resolution by frontmatter id, resolution by bare legacy slug of a new-style
filename, resolution of an archived spec, and a true-negative check (a genuinely
missing spec must still raise `task-spec-missing`). Ran the three new "resolves"
tests and confirmed they failed against the pre-fix code (exit_code 1 instead of 0),
establishing red. The true-negative test already passed pre-fix, as expected since
it doesn't touch the id/slug/archive gaps.

Implemented the minimal fix: added an optional `id: str | None = None` field to the
`Spec` dataclass (`cli/src/ai_team/core/models.py`), populated in `parse_spec` from
`data.get("id")`, since the dataclass previously had no way to carry the frontmatter
`id` that `ai-team spec new` already writes. In `validate.py`, added
`_spec_index_entries(path)` which returns the set of reference strings that should
resolve to a given spec file — filename stem, bare slug (stem with `S-NNN-` prefix
stripped, when the file matches the new-style filename pattern), and frontmatter `id`
(parsed via `parse_spec`, skipping enrichment on `FrontmatterError`) — and
`_build_spec_slugs(root)`, which unions these entries across both `root.specs` and
`root.specs / "archive"`. Replaced the old stem-only set comprehension in
`validate_project` with a call to `_build_spec_slugs(root)`. Left
`_spec_reference_exists` unchanged since its membership-check logic (including the
`.md`-suffix-stripping branch) already works correctly once the index itself is
enriched.

Considered and rejected: modifying `_spec_reference_exists` itself to accept a richer
lookup structure (e.g., a dict of alias -> canonical path) — rejected as unnecessary
complexity since a flat `set[str]` index satisfies the fix contract's three
acceptance forms (id, full stem, bare slug) with no need to distinguish which alias
matched. Considered reading frontmatter directly in `validate.py` instead of
extending the `Spec` model — rejected in favor of the model change, per the Diagnosis
Log's stated preference and because it keeps `Spec` consistent with what `ai-team
spec new` already writes.

Verified green: all 20 tests in `test_validate.py` pass, and the full suite (`cd cli
&& uv run pytest`) passes at 437/437. Ran `cd cli && uv run ruff format --check . &&
uv run ruff check .` — both clean. Ran the repo-level check `uv run --project cli
ai-team validate --tasks --json` from the repo root: returns `[]` (was 12
`task-spec-missing` findings before the fix). Also reproduced the bug's own Fix
Verification block end-to-end in a scratch project created with `ai-team init .
--no-interactive --tools claude` (the `--json` flag mentioned in the verification
snippet does not exist on `ai-team init`; used the documented non-interactive flags
instead) — `ai-team spec new --json "First architecture spec"` followed by `ai-team
task new "Implement thing one" --spec S-001 --json` followed by `ai-team validate
--tasks --json` returned `[]` as required. Scratch project was deleted after
verification.

Nothing remains outstanding for this bug's scope. No files outside
`cli/src/ai_team/core/models.py`, `cli/src/ai_team/core/validate.py`, and
`cli/tests/test_validate.py` were touched.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-08-06

PASS

Stage 1 (bug criteria):

- Diagnosis Log (`### Diagnosis 1 — 2026-08-06`) is complete: reproduction
  status is `confirmed` with a real reproduction against this repo's
  `docs/ai-team` project dir, evidence captured includes exact commands/output
  and source-line citations, the isolated fault names two precise locations
  (`validate.py` `spec_slugs` construction and `_spec_reference_exists`), the
  root cause is evidence-backed (three distinct valid reference forms
  conflated into one stem-only index, plus a non-recursive glob that excludes
  `specs/archive/`), and a planned fix contract + planned verification are
  both present.
- The implemented fix matches the fix contract exactly: `Spec.id` was added
  (`cli/src/ai_team/core/models.py`) and populated in `parse_spec`;
  `_spec_index_entries` (per-file: stem, S-NNN-stripped bare slug, frontmatter
  id) and `_build_spec_slugs` (unions entries across `root.specs` and
  `root.specs / "archive"`) were added to `cli/src/ai_team/core/validate.py`,
  replacing the old stem-only set comprehension in `validate_project`.
  `_spec_reference_exists` was correctly left unchanged since its membership
  check already worked once the index was enriched.
- Fix Verification steps all reproduced independently on the fix branch
  (`bug/B-013-validate-spec-reference-index`, commit `500749d`):
  - `uv run --project cli ai-team validate --tasks --json` from the repo root
    returns `[]` (was 12 `task-spec-missing` findings pre-fix).
  - `cd cli && uv run pytest` → 437/437 passed.
  - `cd cli && uv run ruff format --check . && uv run ruff check .` → both
    clean.
- No unrelated behavior: `git show --stat 500749d` touches exactly
  `cli/src/ai_team/core/models.py`, `cli/src/ai_team/core/validate.py`, and
  `cli/tests/test_validate.py` — nothing outside the fix contract's scope.

Stage 2 (code quality) and Bug Fix Addendum:

- Fix is minimal — only the index-building and model-field code required by
  the isolated fault was changed; `_spec_reference_exists` was correctly left
  untouched.
- Regression tests exist and were independently verified red→green: using a
  worktree pinned to the pre-fix parent commit (`500749d~1`) with the
  post-fix `cli/tests/test_validate.py` copied in, the three "resolves" tests
  (`test_validate_resolves_task_spec_reference_by_frontmatter_id`,
  `..._by_bare_slug_of_new_style_filename`, `..._to_archived_spec`) fail with
  `exit_code == 1` against the pre-fix source and pass against the fix commit
  — confirming genuine red→green, not a test that never exercised the bug.
- True-negative coverage confirmed both by the added test
  (`test_validate_still_reports_task_spec_missing_for_genuinely_missing_spec`)
  and by independent re-verification: it passes both pre- and post-fix (as
  expected, since it doesn't touch the id/slug/archive gaps), and the widened
  index does not suppress a genuinely missing spec reference.
- Correctness / readability / no dead code: confirmed by reading
  `_spec_index_entries` and `_build_spec_slugs` in full; docstrings are
  accurate, `FrontmatterError` is the only exception `parse_spec` raises for
  malformed frontmatter (verified via `_require`), so the narrow except
  clause is correct and doesn't mask unrelated failures.
- Non-blocking observation: stripping the `S-NNN-` prefix means two specs
  with different ids but the same bare slug (e.g. `S-001-launch-plan.md` and
  `S-002-launch-plan.md`) would both contribute the same `"launch-plan"`
  entry to the flat existence set. This does not cause a false negative (a
  genuinely absent spec still fails, verified above) and `task-spec-missing`
  is an existence check only, not an identity/uniqueness check, so this
  isn't a defect relative to the bug's stated Expected Behavior (which
  explicitly requires bare-slug resolution for legacy specs). Flagging for
  awareness only — not blocking this fix.
