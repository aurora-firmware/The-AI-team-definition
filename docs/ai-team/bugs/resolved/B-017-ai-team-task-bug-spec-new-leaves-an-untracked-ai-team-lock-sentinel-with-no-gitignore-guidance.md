---
id: B-017
title: ai-team task/bug/spec new leaves an untracked .ai-team.lock sentinel with
  no gitignore guidance
severity: low
status: resolved
created: '2026-08-06'
---

# ai-team task/bug/spec new leaves an untracked .ai-team.lock sentinel with no gitignore guidance

## Summary

B-014's fix (project-local `allocation_lock`) creates a sentinel file
`<project_dir>/.ai-team.lock` the first time any of `ai-team task new`,
`bug new`, or `spec new` runs, and intentionally leaves it on disk forever
(the design note in B-014's fix contract calls this "harmless to leave on
disk indefinitely" since `flock` locks are released by the kernel on process
exit, so there is nothing to clean up). Nothing in `ai-team init`'s scaffold
or documentation tells a consuming project to ignore this file, so every
consuming project's `git status` will show an untracked `.ai-team.lock`
under its project directory (e.g. `project/.ai-team.lock` or
`docs/ai-team/.ai-team.lock`) the first time an artifact is created after
adopting the fixed CLI. This is not a functional defect — confirmed during
B-014 review that no scanner (`validate`, `status`, `report`,
`check-layout`) globs the project directory root or matches non-`.md`
files, so nothing trips over the sentinel — but it is a persistent,
unexplained git-status hygiene rough edge with no first-party mitigation.

## Reproduction Status

Status: confirmed

Reproduced directly during B-014 code review.

## Evidence

- Logs / stack traces / failing assertions: n/a (not a crash; a hygiene gap)
- Screenshots or recordings: n/a
- Failing command or test: n/a — reproduced manually
- Source inspection:
  - `cli/src/ai_team/core/lock.py` `allocation_lock` creates
    `<project_dir>/.ai-team.lock` via `os.open(lock_path, os.O_CREAT | os.O_RDWR)`
    and never removes it.
  - `cli/src/ai_team/init/sources/` and `cli/src/ai_team/init/scaffolds/`
    contain no `.gitignore` template for scaffolded consuming projects at
    all (grep for `gitignore` under `cli/src/ai_team/` returns nothing), so
    there is no existing mechanism this fix could have extended.
  - Manual repro: `ai-team init` a scratch project, run `ai-team task new
    "X" --json` once, then `git status --short` inside the scratch project
    shows `?? project/.ai-team.lock` alongside the new task file, and the
    lock file remains after the command exits successfully.

## Reproduction Steps

1. `ai-team init --no-interactive --tools claude` in an empty git repo.
2. `git add -A && git commit -m init` (or just note the clean `git status`).
3. Run `ai-team task new "Anything" --json` once.
4. Run `git status --short` and observe `?? project/.ai-team.lock` in
   addition to the expected new task file.

## Expected Behavior

Running `ai-team task new` / `bug new` / `spec new` should not leave
unexplained untracked files in a consuming project's working tree. Either
the sentinel file should be excluded from version control by a
first-party mechanism (e.g. a scaffolded `.gitignore` entry, or `ai-team
init` writing/appending one), or the CLI should document that this file is
expected, safe to ignore, and how to exclude it.

## Actual Behavior

`.ai-team.lock` appears as an untracked file in `git status` after the
first artifact creation and is never removed or documented, with no
supplied `.gitignore` entry anywhere in the framework's `init` scaffold.

## Environment

- OS / platform: Linux
- Language / runtime version: Python 3.14, `ai-team` CLI (post-B-014 fix,
  branch `bug/B-014-concurrent-id-allocation`)
- Relevant dependencies: `cli/src/ai_team/core/lock.py`,
  `cli/src/ai_team/init/sources/`, `cli/src/ai_team/init/scaffolds/`
- Branch / commit: discovered reviewing `bug/B-014-concurrent-id-allocation`
  against `dev-agent`, 2026-08-06

## Related

- Task: n/a
- Specification: n/a
- Prior art: B-014 (`Concurrent ai-team task new calls allocate duplicate
  IDs`) introduced the sentinel file as part of its fix; this bug is a
  follow-up hygiene gap noted during that fix's code review, deliberately
  scoped out of B-014 since it does not affect ID-allocation correctness.

## Suspected Area

`cli/src/ai_team/init/` scaffold sources (no `.gitignore` template exists
for consuming projects) and/or `cli/src/ai_team/core/lock.py` (the sentinel
file itself). Fix could scaffold a `.gitignore` entry, document the file in
a guide, or both.

## Fix Verification

```bash
# In a scratch project created with `ai-team init`, run one artifact
# creation and confirm no untracked, unexplained files remain:
ai-team task new "Anything" --json
git status --short
# .ai-team.lock must either not appear, or be covered by a tracked
# .gitignore entry so it never shows as untracked.
```

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

Reproduction status: confirmed (fresh repro against a locally built copy of
the CLI on this branch, not just B-014-era evidence).

Evidence captured:
- Built and ran the branch's CLI via
  `uv run --project cli ai-team` (UV_CACHE_DIR pointed at the scratchpad;
  version reported: `0.7.1.dev17+g93bcd8735`).
- Repro A (default `project/` dir, in
  /tmp/.../scratchpad/b017/repo1): `ai-team init --no-interactive --tools
  claude .` -> committed clean tree -> `ai-team task new "Anything" --json`
  -> `git status --short` shows:
    ?? project/.ai-team.lock
    ?? project/tasks/pending/T-001-anything.md
  `project/.ai-team.lock` is a 0-byte file created by `os.open(...,
  O_CREAT|O_RDWR)` in `cli/src/ai_team/core/lock.py::allocation_lock` and is
  never removed, exactly as B-014's design note states.
- Repro B (customized `[project] dir`, in
  /tmp/.../scratchpad/b017/repo2): edited `.ai-team.toml` to
  `dir = "docs/ai-team"` (mirroring how this very repo is configured) and
  moved `project/` -> `docs/ai-team/` (the only documented mechanism per
  `cli/docs/usage.md` "You can change this key if your project uses a
  different folder name than `project`."). Ran `ai-team task new` again:
  the lock now lands at `docs/ai-team/.ai-team.lock` and shows untracked.
  This proves the sentinel's path is fully driven by the configurable
  `project_dir` argument passed into `allocation_lock`, not a fixed name.
- `git check-ignore -v` experiment: a single-line, slash-less `.gitignore`
  entry `.ai-team.lock` placed at any directory level matches the sentinel
  at every depth below that `.gitignore` file (confirmed:
  `.gitignore:1:.ai-team.lock  docs/ai-team/.ai-team.lock`), because git
  treats a pattern with no `/` as matching the basename at any depth under
  the `.gitignore`'s own location — it does not need to be re-anchored per
  `project_dir` value.
- Source inspection confirming no existing `.gitignore` mechanism anywhere:
  `grep -rn gitignore cli/src/ai_team/` (all variants) returns nothing;
  `cli/src/ai_team/commands/init.py` only ever writes the `project/`
  scaffold tree, `.claude`/`.codex`, `.ai-team.toml`, and (via
  `_handle_root_guidance`, skip-if-exists / interactive-prompt semantics)
  root `CLAUDE.md`/`AGENTS.md` — no `.gitignore` handling in any path.
- Source inspection of the scaffold generator,
  `cli/scripts/sync_init_scaffolds.py::_replace_project_skeleton`: the
  `scaffolds/project/` tree is NOT a generic copy of
  `sources/project/`. It is hand-curated: `.gitkeep` is synthesized per
  `PROJECT_LEAF_DIRS`, and only `CLAUDE.md`/`AGENTS.md` are copied from
  `sources/project/` by explicit filename loop
  (`for guidance_file in ("CLAUDE.md", "AGENTS.md")`). Dropping a new file
  into `sources/project/` alone would NOT propagate to `scaffolds/project/`
  without also extending this generator function.
- Confirmed the framework's own root `.gitignore`
  (`the-ai-team-definition/.gitignore`) is hand-authored (not produced by
  `ai-team init`) and already excludes `.ai-team.toml`, `.claude`, `.codex`
  — precedent for what a first-party ignore rule looks like, but not itself
  scaffolded output, and this repo's own `docs/ai-team/` has no
  `.gitignore` today, consistent with the bug being unfixed.
- Confirmed via `cli/src/ai_team/core/validate.py` (`_iter_markdown_files`
  uses `folder.glob("*.md")` per known subfolder only) and
  `check_layout.py`/`validate.py` command wrappers that no scanner would
  flag a new `project/.gitignore` file as unexpected — matches the bug
  report's own B-014-review finding, re-confirmed by direct source read.
- Confirmed `docs/ai-team/CLAUDE.md` in this repo is byte-identical to
  `cli/src/ai_team/init/sources/project/CLAUDE.md` (`diff` exit 0),
  evidencing that this repo's customized project dir originated by
  relocating the whole scaffolded `project/` tree (including its files),
  not by hand-building a parallel directory — the only pattern the docs
  describe and the only one observed in practice.
- Located existing test fixtures with a hardcoded expected-file list for
  the generated project skeleton:
  `cli/tests/test_init_scaffolds.py` (~lines 234-246, 745-747) enumerates
  `.gitkeep` files plus `CLAUDE.md`/`AGENTS.md` explicitly — this list will
  need a new entry if a `.gitignore` file is added to the skeleton.

Isolated fault: absence of any first-party ignore/documentation mechanism
for the `.ai-team.lock` sentinel. No single function is "wrong" — this is a
missing-scaffold gap spanning three coordinated points: (1)
`cli/src/ai_team/core/lock.py::allocation_lock` (creates the persistent,
by-design-never-deleted sentinel — confirmed correct per B-014, not to be
touched), (2) `cli/src/ai_team/init/sources/project/` (no `.gitignore`
source file exists), and (3)
`cli/scripts/sync_init_scaffolds.py::_replace_project_skeleton` (hand-curated
copy list that would need to know about a new `.gitignore` file — adding
the source file alone is insufficient).

Root cause: B-014 introduced a project-local, deliberately-persistent
sentinel file without a companion `.gitignore`/documentation update, and
`ai-team init` has never shipped any `.gitignore` scaffolding for consuming
projects (verified absent, not merely incomplete) — so there was no
existing mechanism for B-014 to extend at the time.

Fix-shape decision (candidates considered and evidence for the choice):

1. Scaffold `project/.gitignore` (new `sources/project/.gitignore` file
   containing the single line `.ai-team.lock`, wired into
   `_replace_project_skeleton` and copied by `init.py`'s existing strict,
   collision-checked `_plan_copies` flow used for the rest of the `project/`
   tree). CHOSEN.
   - Works under the default `project/` dir (repro A) and under a
     customized `[project] dir` (repro B), because a slash-less
     `.gitignore` pattern matches at any depth under wherever the
     `.gitignore` file itself lives, and the only documented/observed way
     to customize `project.dir` is to relocate the whole scaffolded tree
     (which carries the new `.gitignore` file along).
   - Fits the existing collision policy already governing every other file
     under `project/`: `init` refuses the whole batch without `--force` if
     any destination exists, which is normally only true on a genuine
     first-run `init` — unlike the repo root, `project/` is a directory
     `ai-team init` owns outright, so there is no pre-existing-file
     ownership conflict to resolve for this location.
   - Verified no validator/scanner is affected by the new file.
   - Known residual limitation (must be stated, not silently assumed away):
     consuming projects that already ran `ai-team init` before this fix
     ships will not retroactively receive `project/.gitignore` (same
     limitation every other scaffold file already has); and a project that
     set `[project] dir` to a hand-built directory that was never populated
     from the `project/` scaffold tree (undocumented but not technically
     prevented) would not receive the file either. Both are pre-existing
     properties of the scaffold model, not a new gap introduced by this fix.

2. Have `ai-team init` write/append an ignore entry to the repo ROOT
   `.gitignore`. REJECTED as the primary mechanism.
   - A root `.gitignore` already exists in the large majority of real
     repositories (confirmed by this very repo's own hand-authored root
     `.gitignore`). The only existing precedent for root-level files
     (`_handle_root_guidance`, used for CLAUDE.md/AGENTS.md) is strictly
     skip-if-exists/prompt — never append — so reusing that precedent as-is
     would silently do nothing for most consumers, which fails to close
     the bug for the common case. An append-to-existing-file capability has
     no precedent anywhere in `init.py` today and would be a new class of
     mutation (editing a file `init` does not own, outside its scaffold
     set) — a bigger contract change than this low-severity hygiene bug
     needs, and not clearly authorized by the bug's own scope.

3. Remove/relocate the sentinel file (change `lock.py`). REJECTED.
   - Deleting the lock file after release reopens the exact TOCTOU hole
     B-014 deliberately avoided by choosing `flock`-on-a-persistent-path
     semantics (a second process could recreate the file at a new inode
     while a third process still holds a lock via the stale inode).
     Relocating the lock outside `project_dir` entirely (e.g. an XDG cache
     dir) sidesteps that risk but changes the lock's storage contract and
     introduces new questions (keying by repo path, multi-checkout
     collisions) that are out of this bug's scope and were already settled,
     reviewed, and closed in B-014.

4. Documentation only. REJECTED as sole fix, RETAINED as a supplement.
   - Does not prevent the untracked-file noise from appearing for anyone
     who does not read the docs, so it is strictly weaker than option 1 on
     its own. Retained as a small addition (a short note in
     `cli/docs/usage.md`'s "Project Folder Structure" section referencing
     B-014, explaining the sentinel and pointing at the shipped
     `.gitignore` entry) specifically to cover the residual "already ran
     `init` before this fix shipped" and "hand-built custom dir" cases that
     option 1 cannot retroactively reach — this matches the bug's own
     Suspected Area wording ("scaffold ... or document ... or a
     combination").

Nothing here required guessing at an undocumented part of the framework
contract: `[project] dir` customization-via-relocation is documented in
`cli/docs/usage.md`, the collision policy for `project/` vs. root files is
already codified in `init.py`, and git's slash-less `.gitignore` matching
behavior was verified directly rather than assumed. No open question is
being deferred to the Architect.

Planned verification:
- `cli/tests/test_init_scaffolds.py`: extend the hardcoded expected-file
  list (~lines 234-246, 745-747) to include `.gitignore`, and add/extend a
  case asserting its content is exactly `.ai-team.lock` (mirroring the
  existing CLAUDE.md/AGENTS.md copy assertions at ~line 261).
- `cli/tests/test_init.py`: add a case that runs `ai-team init` into a
  scratch dir, then `ai-team task new`, then asserts
  `git status --short`-equivalent (or direct filesystem check via
  `git check-ignore`) shows `.ai-team.lock` is ignored, not untracked.
- Manual: the bug's own `Fix Verification` block —
  `ai-team task new "Anything" --json` in a scratch project created with
  `ai-team init`, then `git status --short` must not list `.ai-team.lock`
  as untracked (either absent or covered by the tracked `.gitignore`).
- `python cli/scripts/sync_init_scaffolds.py` followed by
  `uv run pytest` (with `UV_CACHE_DIR` pointed at a writable location if
  needed) from `cli/`, plus `uv run ruff format --check .` and
  `uv run ruff check .`, per this repo's CLAUDE.md.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-08-06

Read the existing Diagnosis Log (Diagnosis 1) as the fix contract and implemented
option 1 + supplement 4 (options 2/3 were not revisited, per instructions). Followed
TDD strictly, red before green, for every test file touched.

**Cycle 1 (`fix(init): scaffold project/.gitignore to cover .ai-team.lock sentinel`,
commit `4adfbdd`).** Wrote failing tests first: extended the hardcoded `expected_files`
set in `test_sync_script_replaces_project_with_empty_lifecycle_skeleton`
(`cli/tests/test_init_scaffolds.py`) to include `Path(".gitignore")`; added a fixture
write for `sources/project/.gitignore` in `_setup_fake_repo` (needed because
`_replace_project_skeleton`'s hand-curated copy loop would otherwise raise
`FileNotFoundError` against the synthetic fixture repo); added
`test_sync_script_copies_project_gitignore_ignoring_the_lock_sentinel` (fixture-based,
mirrors the existing CLAUDE.md/AGENTS.md copy-parity test) and
`test_package_owned_project_gitignore_source_ignores_the_lock_sentinel` (real,
non-fixture repo, asserts the actual shipped file content is exactly
`.ai-team.lock\n`). Confirmed all three failed for the expected reasons. Then added
`cli/src/ai_team/init/sources/project/.gitignore` (single line `.ai-team.lock`) and
extended `cli/scripts/sync_init_scaffolds.py::_replace_project_skeleton`'s copy loop
from `("CLAUDE.md", "AGENTS.md")` to `("CLAUDE.md", "AGENTS.md", ".gitignore")`,
renaming the loop variable/error message from "guidance_file"/"project guidance source"
to "root_file"/"project skeleton root file" since the tuple no longer only holds
guidance docs (refactor step). Regenerated scaffolds and confirmed all new tests plus
the full suite went green.

Also verified, per the diagnosis's item 3, that `init.py`'s existing
`_iter_files`/`_plan_copies` flow (`root.rglob("*")`) needed no code change to deliver
a dotfile — confirmed both by a standalone `rglob` probe and by two manual scratch-dir
runs of the actual built CLI (`uv run --project cli ai-team init` + `git
init`/`add`/`commit` + `ai-team task new --json` + `git status --short`/`git
check-ignore -v`) in `/tmp/.../scratchpad/b017-verify` (default `project/` dir) and
`/tmp/.../scratchpad/b017-verify-customdir` (relocated to `docs/ai-team` with
`[project] dir` updated, mirroring this very repo's layout). Both confirmed
`.ai-team.lock` no longer appears as untracked and `git check-ignore -v` reports the
match against the shipped `project/.gitignore` (or `docs/ai-team/.gitignore` in the
relocated case). Also built the wheel (`uv build`) and confirmed via `unzip -l` that
`ai_team/init/scaffolds/project/.gitignore` (14 bytes) is actually packaged — this
addressed a self-raised concern that hatchling's default VCS-based file selection might
silently drop a `.gitignore` file from the built artifact; it does not, because
`[tool.hatch.build] include = ["src/ai_team/**"]` already overrides VCS-based selection
for this project.

Added corresponding integration tests to `cli/tests/test_init.py`:
`test_init_scaffolds_project_gitignore_ignoring_the_lock_sentinel` (asserts `init`
delivers `project/.gitignore` with exact content `.ai-team.lock\n`) and
`test_ai_team_lock_sentinel_is_not_untracked_after_task_creation` (runs real `git
init`/`config`/`add`/`commit` then `task new --json`, then asserts `.ai-team.lock` does
not appear in `git status --porcelain`). The first attempt at the second test was a
false negative — without first committing a baseline, git collapses the whole untracked
`project/` directory into a single `?? project/` line, hiding the lock file regardless
of whether it's ignored, so the test passed even against the unfixed code. Fixed by
committing a baseline before the artifact-creation step, matching the bug's own
reproduction steps; re-verified this now fails against the pre-fix code and passes after
the fix.

**Cycle 2 (`docs(usage): document the .ai-team.lock sentinel and gitignore coverage`,
commit `89e2ce8`).** Added a new "### The `.ai-team.lock` sentinel" subsection to
`cli/docs/usage.md`'s "Project Folder Structure" section explaining why the file
persists (B-014's flock design), that the shipped `project/.gitignore` covers it, and
that projects which ran `ai-team init` before this fix must add the entry themselves.
Added `test_usage_md_describes_ai_team_lock_sentinel_and_gitignore_coverage` to
`cli/tests/test_usage_guide.py` first, verified it failed by temporarily stashing the
doc change (`git stash push -- cli/docs/usage.md`), confirmed the red failure, then
restored the doc change and confirmed green.

Final verification: full `uv run pytest` from `cli/` — 459 passed; `uv run ruff format
--check .` and `uv run ruff check .` — both clean (ruff format did reformat the two
touched test files to its style; re-ran the full suite afterward, still green); `python
scripts/sync_init_scaffolds.py` is idempotent against the committed scaffolds (`git
status --porcelain cli/src/ai_team/init/scaffolds` is empty). No changes were needed to
`cli/src/ai_team/core/lock.py` (untouched, per the contract) or to
`cli/src/ai_team/commands/init.py` (its existing copy flow already handled the new file
correctly). No changes to `cli/docs/commands.md` were needed since no command output or
release guidance changed. Nothing remains outstanding from the fix contract; all five
planned-verification items and the bug's own Fix Verification block were executed and
passed.

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

**Diagnosis→fix evidence chain (verified before Stage 1):** Diagnosis 1 records
confirmed reproduction status, evidence (fresh repro against a locally built
CLI, plus a second repro under a customized `[project] dir`), an isolated
fault spanning three coordinated points, a stated root cause, a fix-shape
decision with rejected alternatives and rationale, and a planned-verification
list. Complete; proceeded to Stage 1.

**Stage 1 (bug criteria):**
- Fix addresses the isolated fault/root cause exactly as diagnosed: adds
  `cli/src/ai_team/init/sources/project/.gitignore` (`.ai-team.lock`), wires
  it into `sync_init_scaffolds.py::_replace_project_skeleton`'s copy loop, and
  documents the sentinel + gitignore coverage + retroactive-gap caveat in
  `cli/docs/usage.md` — matches "option 1 CHOSEN + option 4 RETAINED as
  supplement" from the fix-shape decision. `cli/src/ai_team/core/lock.py` and
  `cli/src/ai_team/commands/init.py` are untouched (confirmed via
  `git diff 1b7a811..4adfbdd` on both paths — empty diff), matching the
  contract that lock.py stays out of scope per B-014 and that init.py's
  existing `rglob`-based copy flow needed no change.
- Fix Verification steps followed and independently reproduced (see Evidence
  below) — not taken on the Developer's word.
- No unrelated behavior added; diff is scoped to 7 files (source+scaffold
  `.gitignore`, sync script, 3 test files, 1 doc file), matching the fix
  contract's planned-verification list item-for-item.

**Stage 2 (code quality) + Bug Fix Addendum:**
- Correctness: independently confirmed via full test suite, ruff, and two
  manual scratch-project runs (default `project/` dir and a customized
  `docs/ai-team`-style dir) — `.ai-team.lock` no longer appears untracked in
  either case, and `git check-ignore -v` confirms the match against the
  shipped `.gitignore` in both.
- Regression test genuinely red→green: extracted
  `test_ai_team_lock_sentinel_is_not_untracked_after_task_creation` verbatim
  from the post-fix tree (`89e2ce8`) and ran it, unmodified, against the
  pre-fix tree (`1b7a811`) in an isolated git worktree — it fails there with
  a real, non-collapsed `?? project/.ai-team.lock` line (not the
  collapsed-directory false negative the Developer describes catching on
  their first attempt), and passes cleanly on `89e2ce8`. The Developer's
  claim is verified, not assumed.
- Tests are meaningful, not tautological: they assert exact file content
  (`.ai-team.lock\n`), source/scaffold parity, and a real git-status/
  check-ignore outcome rather than just presence of files. They follow
  existing repo conventions (fixture-based sync-script test mirroring the
  existing CLAUDE.md/AGENTS.md copy-parity test; a package-owned/non-fixture
  companion test mirroring the existing pattern for other package-owned
  sources; CLI-runner + real subprocess `git` integration test mirroring
  other `test_init.py` cases).
- The `_setup_fake_repo` fixture change is additive only (adds a
  `.gitignore` fixture write) — no existing fixture writes or assertions
  were removed or weakened; every existing test in the file still passes.
- The `_replace_project_skeleton` loop-variable/error-message rename
  (`guidance_file`/"project guidance source" → `root_file`/"project skeleton
  root file") is justified: the tuple no longer holds only guidance docs.
  Grepped the full pre-fix tree for the old error string and old variable
  name in `cli/tests/` and `cli/src/` — no test or other code asserts on
  that literal string, so the rename does not break any existing
  dependency.
- Fix is minimal: no unrelated refactoring or feature code bundled in; the
  rename above is the only "extra" and is directly necessitated by the fix,
  not scope creep.
- Scaffold regeneration discipline respected: confirmed
  `git status --porcelain cli/src/ai_team/init/scaffolds` is empty after an
  independent `python scripts/sync_init_scaffolds.py` run from a clean
  worktree checkout of the branch tip — the committed scaffold output is not
  hand-edited drift. Also independently ran `bash cli/scripts/gen_docs.sh`
  and confirmed `cli/docs/commands.md` has no diff, corroborating the
  Developer's claim that no command surface changed.

**Minor, non-blocking observations:**
- The Diagnosis Log's planned-verification note references "~lines 234-246,
  745-747" in `test_init_scaffolds.py` for lists that would need a new
  entry; the ~745-747 reference turned out to point at an unrelated
  `required_phrases` substring check in a dev-loop skill test, not an
  expected-files enumeration, so no change was needed there. The Developer
  correctly identified and updated the one location that actually mattered
  (~244-259); this is a minor imprecision in the diagnosis note, not a gap
  in the implemented fix.
- This repository's own `docs/ai-team/` (a pre-fix, already-`init`'d,
  customized-dir consumer of this very framework) still has no
  `.ai-team.lock` entry in its root `.gitignore` — this is the documented,
  accepted "already ran init before this fix shipped" residual case from
  the diagnosis and `usage.md`, correctly out of scope for this bug fix.

**Evidence:**
- `git diff 1b7a811..4adfbdd -- cli/src/ai_team/core/lock.py
  cli/src/ai_team/commands/init.py` → empty.
- Extracted-test red/green check in isolated `git worktree`s at `1b7a811`
  and `89e2ce8`: fails pre-fix (`1 failed`, real untracked
  `?? project/.ai-team.lock` line), passes post-fix (`1 passed`).
- Independent manual Fix Verification in
  `/tmp/.../scratchpad/b017-manual-verify/repo1` (default `project/` dir)
  and `.../repo2` (customized `docs/ai-team` dir, mirroring this repo's own
  layout): `git status --short` after `ai-team task new "Anything" --json`
  shows only the new task file, never `.ai-team.lock`, in both cases; `git
  check-ignore -v` in both cases resolves to the shipped `.gitignore`.
- `python scripts/sync_init_scaffolds.py && uv run pytest` from `cli/` in a
  clean worktree checkout of `89e2ce8` (with the repo's own gitignored
  `.ai-team.toml` copied in so the CLI's own project-root locator resolves
  correctly under `cli/`'s test suite) — 459 passed.
- `git status --porcelain cli/src/ai_team/init/scaffolds` from repo root →
  empty after regeneration.
- `uv run ruff format --check .` → "65 files already formatted"; `uv run
  ruff check .` → "All checks passed!".
- `bash cli/scripts/gen_docs.sh` → `git status --porcelain
  cli/docs/commands.md` → empty.

Next owner: Bug-Fix Loop.
