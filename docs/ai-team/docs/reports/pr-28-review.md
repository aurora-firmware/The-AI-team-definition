# PR Review: aurora-firmware/The-AI-team-definition#28 — Relocate project artifacts to docs/ai-team and file B-013 through B-017

## Summary

This PR relocates `project/` to `docs/ai-team/` (pure renames), files and resolves
five bugs (B-013 through B-017), adds the `flock`-based artifact-ID allocation lock,
extends spec-reference resolution in `validate`, tightens the Developer lifecycle-file
boundary and the `integrate` destination-branch regression check, and adds a framework
comparison document.

Review was run with three parallel scoped agents (source, framework contract,
documentation), each at `full` tier with repository context. **8 findings**: 6 `warning`,
2 `suggestion`. All 8 were triaged as real and addressed on the branch — 2 were code
defects, 5 were stale or inaccurate documentation, 1 was a framework-convention
violation. A second review round over the fix commit is recorded under
"Review notes" below.

| Scope | Files | Lines changed | Tier | Findings |
|---|---:|---:|---|---:|
| Source | 19 | ~1330 | full | 2 |
| Framework contract | 14 | ~120 | full | 1 |
| Documentation | 8 | ~2620 | full | 5 |

## Findings

### Source

#### [warning] `_SPEC_FIELDS` omits the new `id` field, breaking `dump_frontmatter`'s round-trip contract — `cli/src/ai_team/core/models.py:329`

`Spec` gained `id: str | None = None`, but `_SPEC_FIELDS` — the list `dump_frontmatter`
walks to sync model fields into the YAML map — was not updated. Task, Bug, Adr, and
ChangeRequest all mirror their full field set; Spec became the exception.

**Maintainer response — real bug, fixed.** Reproduced before fixing: `dump_frontmatter`
on a hand-built `Spec(..., id="S-002")` silently omitted `id` from the output entirely.

Fixing this exposed a second, deeper defect the reviewer had only partly diagnosed.
Adding `("id", "id")` to `_SPEC_FIELDS` immediately broke four `spec_new` tests, because
`spec.py` injected `source_map["id"] = spec_id` into the `CommentedMap` **without** ever
setting the model's `id` attribute. Once `id` was in the field list, the sync loop read
`model.id is None` and *popped* the injected key — so `ai-team spec new` stopped writing
`id` at all. The real defect was that the field was never wired through the model.

Fix applied in three parts:
- `models.py` — added `("id", "id")` to `_SPEC_FIELDS`, ordered **last** (after `author`)
  to match the layout the CLI actually produces, verified against `S-002` and `S-004`.
  The reviewer suggested placing it first; that would have been wrong for round-tripping
  hand-built specs.
- `commands/spec.py` — dropped the `source_map["id"]` injection and passed `id=spec_id`
  to the `Spec` constructor, so serialisation flows through the normal field path.
- `commands/list.py` — replaced the `spec._source_map["id"]` private reach-in with
  `spec.id or path.stem`, now that the field is populated.

Two regression tests added (`test_dump_frontmatter_spec_optional_id_present_when_set`,
`..._omitted_when_none`), confirmed failing before the fix. Output verified end-to-end:
`ai-team spec new` emits `id: S-001` after `author`, byte-identical in layout to the
existing spec files, with the inline `status` comment preserved.

#### [warning] Unanchored `pr-*-review.md` pattern silently ignores future PR review reports — `.gitignore:12`

Without a leading slash the pattern matches at any depth. Confirmed with
`git check-ignore --no-index`: it matches `docs/ai-team/docs/reports/pr-999-review.md`,
the exact path and naming convention this repo already uses for committed reports
(`pr-23-review.md`, `pr-25-review.md`).

**Maintainer response — real bug, fixed.** Already-tracked files were unaffected, but any
*future* report at the established location would have been silently excluded from
`git add -A`. Anchored to `/pr-*-review.md` (repo root only) with a comment explaining
why. This report is itself the first file that would have hit the bug.

### Framework contract

#### [suggestion] Destination-branch discovery order is paraphrased inline instead of referenced — `cli/src/ai_team/init/sources/skills/integrate/body.md:47`

Item 8b pointed at `dev-loop`'s Step 2 Baseline Test Guard but then restated its
four-step discovery order in parentheses. Accurate today, with no mechanism to catch
drift if `dev-loop`'s list changes.

**Maintainer response — real convention violation, fixed.** `CLAUDE.md` states: "If a
rule is shared, own it in one place and reference it elsewhere." A paraphrased copy in an
exported skill body is exactly what that rule forbids. Verified the cross-reference
resolves before trimming: `dev-loop/body.md:34` is titled "Step 2: Baseline Test Guard"
and carries a `#### Discovery Order` subsection with the four steps as described.

Trimmed to a pure pointer instructing the reader to read `dev-loop`'s **Discovery Order**
and apply it directly. Scaffolds regenerated for both the `claude` and `codex` exports.

### Documentation

#### [warning] Key-conventions table still points at `project/` — `CLAUDE.md:59`

**Maintainer response — real, fixed.** The relocation moved this repo's artifacts to
`docs/ai-team/` (per `[project] dir` in `.ai-team.toml`); no `project/` directory exists
at the repo root anymore. Table row updated to `docs/ai-team/`.

#### [warning] Repository Structure tree and Contributing section still show `project/` — `README.md:229`, `README.md:252`

**Maintainer response — real, fixed.** The tree documents *this* repo's top-level layout
alongside `ai-process/`, `guides/`, and `cli/`, so the stale entry is genuinely wrong.
Updated to `docs/ai-team/` with a note pointing at `[project] dir`, and corrected the
Contributing line to `docs/ai-team/decisions/`.

The reviewer correctly did **not** flag `README.md` lines 194/199/208: those describe a
*consuming* project's default `[project] dir`, which is still `project/`. Verified before
editing — changing those would have been wrong.

#### [warning] Skill count is wrong: claims 18, repo has 19 — `superpowers_comparison.md:6`

**Maintainer response — real, fixed.** `ls -d .../sources/skills/*/` returns 19, and the
document's own category table sums to 19, contradicting its header. Both occurrences
corrected. Also verified the adjacent "5 role agents" claim in the same sentence — that
one is accurate and was left alone.

#### [suggestion] 448-line analysis document dropped at repo root with no cross-reference — `superpowers_comparison.md:1`

**Maintainer response — real structural issue, fixed.** Confirmed orphaned (no references
from `README.md`, `CLAUDE.md`, or anywhere else in the repo). `docs/ai-team/docs/` is the
established home for this repo's analysis documents and is where the progress report in
this same PR correctly lives. Moved via `git mv` to
`docs/ai-team/docs/superpowers_comparison.md`, preserving rename history.

#### [warning] PR title and description contradict the actual state of the branch — `docs/ai-team/bugs/resolved/B-013-*.md:6`

The PR body claimed "All four new bugs are `status: open` with empty Diagnosis and Work
Logs; none are fixed here." At head, five bugs (B-013 through B-017) are in
`bugs/resolved/` with `status: resolved`, complete Diagnosis and Work Logs, and committed
PASS verdicts. The title also named only "B-013 through B-016", omitting B-017.

**Maintainer response — real, fixed.** The description was written early and never
refreshed as the branch grew. Title and body both updated to describe five filed *and
fixed* bugs, and the stale verification numbers were corrected (the body claimed 433
tests; the branch had 459 before this review's fixes, 461 after).

## Skipped files

- 130 pure renames from `project/` to `docs/ai-team/` (0 additions, 0 deletions). Content
  unchanged; reviewed only for inbound references that the move would break.
- No lock files, vendored code, minified assets, or binaries were present in the diff.

## Review notes

- Existing PR review comments fetched before reviewing: 0. No findings were suppressed as
  duplicates of prior human comments.
- Three scoped agents ran in parallel at `full` tier, each reading surrounding repository
  context rather than the bare diff. The repository was checked out at the PR head
  (`9d9e5b4`), so agents read files directly instead of fetching blobs.
- No CI files changed, so no `ci` scope was created. No files were security-flagged
  (no auth/crypto/secret paths, no dependency manifest changes, no workflow permission
  changes), so no dedicated security agent was spawned; instead the security reference
  was applied as a secondary lens to `core/lock.py` by the source agent.
- Findings explicitly investigated and **dismissed** as non-issues, all verified rather
  than assumed: fd leaks and `LockTimeout` behaviour at `timeout <= 0` in `lock.py`;
  `ArtifactExists` propagation through the lock; `mkdir` in `allocation_lock` altering
  missing-project error semantics; an `IndexError` in `_spec_index_entries`' `split("-", 2)[2]`
  (the regex guarantees ≥2 dashes); redundancy of the `specs/archive/` scan (`_iter_markdown_files`
  is non-recursive, so it is required); positional-argument breakage from the new `Spec.id`
  field (all construction sites use keywords); `os.open` without `O_NOFOLLOW` (theoretical,
  local-only, no writes through that fd); source/scaffold drift (none — byte-identical);
  the `dev-loop` cross-reference being dangling (it resolves); and the Developer "Never
  touch" line contradicting Work Log duties (it does not — the Developer returns the Work
  Log as a handoff, and the active loop commits it).
- Verification after fixes, from `cli/`: `uv run pytest -q` — **461 passed**;
  `uv run ruff format --check .` — 65 files already formatted; `uv run ruff check .` —
  all checks passed; `python scripts/sync_init_scaffolds.py` — no drift;
  `bash cli/scripts/gen_docs.sh` — `commands.md` unchanged.
- Round 2: pending — three fresh agents re-review the fix commit against the round-1
  findings. Result to be recorded here.
