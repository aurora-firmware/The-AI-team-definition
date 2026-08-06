---
id: B-014
title: Concurrent ai-team task new calls allocate duplicate IDs
severity: high
status: in-progress
created: '2026-08-05'
---

# Concurrent ai-team task new calls allocate duplicate IDs

## Summary

ID allocation is a scan-then-write with no mutual exclusion, so two `ai-team
task new` processes running concurrently both observe the same highest existing
ID and both claim `N+1`. The existing `write_artifact(overwrite=False)` guard
does not catch this, because it only rejects an identical *filename* — two tasks
with different titles produce different slugs and both writes succeed. The result
is two task files carrying the same `id:`, which makes every downstream
reference (`ai-team show`, dependency lists, branch names) ambiguous and requires
manual renumbering. `bug new` and `spec new` share the same allocation shape and
the same exposure.

## Reproduction Status

Status: confirmed

Reproduced on the first attempt with three concurrent `ai-team task new` calls
in a clean scratch project; two of the three claimed `T-003`.

## Evidence

- Logs / stack traces / failing assertions:

  ```
  $ ai-team task new "Parallel alpha" --json &
    ai-team task new "Parallel beta"  --json &
    ai-team task new "Parallel gamma" --json &
    wait
  {"id": "T-002", "path": ".../T-002-parallel-gamma.md"}
  {"id": "T-003", "path": ".../T-003-parallel-alpha.md"}
  {"id": "T-003", "path": ".../T-003-parallel-beta.md"}

  $ ls project/tasks/pending
  T-001-implement-thing-one.md
  T-002-parallel-gamma.md
  T-003-parallel-alpha.md
  T-003-parallel-beta.md
  ```

- Screenshots or recordings: n/a
- Failing command or test: any batch of `ai-team task new` invocations issued in
  parallel (the natural pattern when a Planner creates a decomposed task set).
- Source inspection:
  - `cli/src/ai_team/core/ids.py:23` `next_task_id` → `_max_matching_number`
    iterates the four task state folders and returns `max + 1` with no lock held
    across the subsequent write.
  - `cli/src/ai_team/commands/task.py:167-185` computes `task_id`, derives the
    slug, then calls `write_artifact(dest, ..., overwrite=False)`. The
    `ArtifactExists` guard keys on the full path, so distinct slugs sharing an ID
    never collide.
  - Same shape in `cli/src/ai_team/commands/bug.py:118-135` and
    `cli/src/ai_team/commands/spec.py:58-78`.

## Reproduction Steps

1. `ai-team init --no-interactive --tools claude` in an empty directory.
2. Run three `ai-team task new "<distinct title>" --json` commands concurrently
   (background them and `wait`).
3. Inspect the returned JSON and `project/tasks/pending/`.
4. Observe at least two files sharing one `T-NNN` identifier.

## Expected Behavior

Concurrent artifact creation must allocate distinct identifiers. Each successful
`ai-team task new` (and `bug new`, `spec new`) returns an ID no other process has
been given, regardless of how many run at once.

## Actual Behavior

Two processes read the same maximum and both write `T-003`, leaving two pending
task files with the same `id:` frontmatter. One must be renumbered by hand, and
any reference recorded before the collision is noticed points at two files.

## Environment

- OS / platform: Linux
- Language / runtime version: Python 3.14, `ai-team` CLI 0.10.1
- Relevant dependencies: `cli/src/ai_team/core/ids.py`,
  `cli/src/ai_team/commands/{task,bug,spec}.py`, `cli/src/ai_team/core/fs.py`
- Branch / commit: `dev-agent`, inspected 2026-08-05

## Related

- Task: n/a
- Specification: n/a
- External evidence: `/home/daneel/projects/the-intern/ai-process-cli-reported-issues.md`,
  entry dated 2026-06-30
- Prior art: B-005 fixed duplicate spec IDs for the *sequential* case by scanning
  frontmatter ids; this bug is the concurrent case, which that fix does not cover.

## Suspected Area

`cli/src/ai_team/core/ids.py` allocation helpers and their call sites in
`cli/src/ai_team/commands/task.py`, `bug.py`, and `spec.py` — the scan and the
create need to happen under one project-local lock, or creation needs to retry
on collision with a re-scan.

## Fix Verification

```bash
# In a scratch project created with `ai-team init`, run N creations in parallel
# and assert N distinct IDs:
for t in alpha beta gamma delta epsilon; do
  ai-team task new "Parallel $t" --json &
done; wait
ls project/tasks/pending | grep -oE '^T-[0-9]{3}' | sort | uniq -d
# must print nothing

cd cli && uv run pytest
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

Reproduction status: confirmed. Reproduced deterministically on
`bug/B-014-concurrent-id-allocation` against a clean scratch project created with
`ai-team init --no-interactive --tools claude`, for all three allocation sites
named in the bug (`task new`, `bug new`, `spec new`).

Evidence captured:

- Three batches of 5 parallel `ai-team task new "Parallel <t>" --json &` / `wait`
  in one scratch project. Batches 2 and 3 collided; batch 2 returned:

  ```
  {"id": "T-007", "path": ".../T-007-parallel-delta-run2.md"}
  {"id": "T-007", "path": ".../T-007-parallel-epsilon-run2.md"}
  {"id": "T-008", "path": ".../T-008-parallel-alpha-run2.md"}
  {"id": "T-009", "path": ".../T-009-parallel-gamma-run2.md"}
  {"id": "T-009", "path": ".../T-009-parallel-beta-run2.md"}
  ```

  `ls project/tasks/pending | grep -oE '^T-[0-9]{3}' | sort | uniq -c | sort -rn`
  showed `2 T-012`, `2 T-011`, `2 T-009`, `2 T-007`. Frontmatter of the two
  colliding `T-007` files confirms distinct slugs and titles sharing one `id:`.
- Same shape confirmed for the other two sites in the same scratch project:
  5 parallel `ai-team bug new ... --severity low --json` produced three distinct
  files all carrying `id: B-002`; 5 parallel `ai-team spec new ... --json`
  produced two distinct files both carrying `id: S-001`.
- Regression baseline: no production code was modified during diagnosis
  (`git status --porcelain` clean throughout), and `cd cli && uv run pytest -q`
  passes 437/437 on the unmodified branch — the collision is a genuine untested
  gap, not an environment artifact.
- `grep -rn "flock|portalocker|filelock|Lock("` over `cli/src` returns nothing —
  no mutual-exclusion primitive exists anywhere in the CLI source.

Isolated fault: the composite "scan directory for max existing ID, then write a
new file at a slug-derived path" sequence performed by each of the three
artifact-creation commands has no mutual exclusion across processes:

- `cli/src/ai_team/core/ids.py:86-101` `_max_matching_number` (invoked via
  `_next_id` / `next_task_id` / `next_bug_id` / `next_spec_id`) does a plain
  `directory.iterdir()` scan with no lock held, and returns before any file is
  written.
- `cli/src/ai_team/commands/task.py:167-185` `new_task`:
  `task_id = next_task_id(root)` (167) → slug/`dest` computed (168-169) →
  `write_artifact(dest, ..., overwrite=False)` (185). No lock spans this sequence.
- `cli/src/ai_team/commands/bug.py:118-135` `new_bug`: identical shape.
- `cli/src/ai_team/commands/spec.py:58-78` `new_spec`: identical shape.
- `cli/src/ai_team/core/fs.py:194-197` `write_artifact`'s `ArtifactExists` guard
  (`if path.exists() and not overwrite: raise ArtifactExists(...)`) keys on the
  literal destination `path` only. Two concurrent processes with different titles
  compute different slugs (hence different `dest` paths) for the same allocated
  ID, so this guard never fires and both writes succeed.

Root cause or fault hypothesis: confirmed root cause, not a hypothesis. Classic
TOCTOU (time-of-check-to-time-of-use) race. `next_task_id` / `next_bug_id` /
`next_spec_id` compute "next ID" by reading current directory state without
reserving that ID, and the subsequent `write_artifact` call has no ID-aware
collision check — only a path-equality check. Two processes that interleave
between the scan and the write both observe the same max and both successfully
claim `N+1`, producing two artifact files with identical `id:` frontmatter but
distinct filenames. `bug new` and `spec new` share this exact code shape
independently (no shared helper currently), so the same race exists three times
over.

Planned verification / fix contract (all three allocation sites; deterministic
testing, no sleep-based races):

- Planned fix: add one project-local, process-safe lock (an exclusive-create
  lockfile acquired via `os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)` with
  bounded retry/backoff and release in a `finally`, or `fcntl.flock` given the
  stated Linux environment) and wrap the "scan for next ID → compute destination →
  `write_artifact`" sequence in that lock's critical section at all three call
  sites. Centralize lock acquisition + scan + write into one shared helper (in
  `ids.py` or a new `core/lock.py`) that all three commands call, rather than
  duplicating the lock usage three times, per this repo's "own it in one place"
  convention.
- Deterministic test plan for the TDD cycle:
  1. A focused unit test for the lock primitive using two real `threading` threads
     coordinated with `threading.Event`/`threading.Barrier` (never `time.sleep`
     for ordering) to prove mutual exclusion: thread A acquires and blocks on an
     `Event` before releasing; thread B's acquisition is asserted via a shared
     flag, not timing, to not succeed until A signals release. A bounded
     `Event.wait(timeout=...)` is used only as a hang safety-net.
  2. A call-site regression test per allocation site (`task`, `bug`, `spec`) using
     an injected/patched seam: monkeypatch the directory-scan step (or a small
     hook the fix introduces around it) so it blocks on a `threading.Barrier(2)`
     shared by two threads, forcing both threads' "read max ID" to interleave
     before either writes. Assert deterministically that the two IDs returned are
     distinct once the lock wraps the critical section.
  3. Optionally, a real subprocess-based end-to-end test: spawn N (>=5) real
     `ai-team task new` / `bug new` / `spec new` processes concurrently via
     `subprocess.Popen` against one scratch project, `wait()` on all, and assert
     `len(set(ids)) == N`. Because the lock guarantees no duplicate ID under any
     interleaving once the fix is in place, this assertion is deterministic.
  4. Full regression: `cd cli && uv run pytest` (with `UV_CACHE_DIR` pointed at a
     writable path) must remain green, plus a manual run of the bug's own Fix
     Verification script (parallel `task new` batch +
     `grep -oE '^T-[0-9]{3}' | sort | uniq -d` prints nothing).

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-08-06

Read the recorded Diagnosis Log (there is no on-branch copy of the canonical bug
file) and treated its fix contract as the implementation target: one
project-local lock wrapping "scan for next ID → write" at all three allocation
sites (`task new`, `bug new`, `spec new`), centralized in one shared helper rather
than duplicated three times, using only the standard library.

Confirmed the bug first, before writing any test: ran the bug's own Fix
Verification script (5 parallel `ai-team task new` calls against a scratch project
built with `ai-team init`) on the unmodified branch and got 2 collision pairs
(`T-001` shared twice, `T-003` shared twice out of 5 calls), matching the diagnosis
exactly.

Implemented `ai_team.core.lock`: `allocation_lock(project_dir, timeout=10.0)`, a
context manager built on `fcntl.flock(LOCK_EX | LOCK_NB)` against a sentinel file
`<project_dir>/.ai-team.lock`, polled with a bounded retry/backoff loop and
releasing in a `finally`. Chose `flock` over a create-exclusive lockfile
specifically for the staleness requirement: `flock` locks are owned by the open
file description, so the kernel releases them automatically when the holder's
process exits for any reason (including a crash), which means there is no stale
lock to detect, age-check, or clean up — the sentinel file itself is harmless to
leave on disk indefinitely. Bounded-wait behavior: acquisition never blocks
forever; after `timeout` seconds of contention it raises `LockTimeout` naming the
lock path, so a wedged or very slow holder cannot hang a caller indefinitely. On
top of that, added `create_artifact_with_lock(project_dir, allocate_id, build)` —
the single shared "scan+build+write" helper the diagnosis asked for, so `task.py`,
`bug.py`, and `spec.py` each supply only a zero-arg `allocate_id` callable and a
`build(id) -> (dest, model, body)` callable instead of holding the lock
themselves.

Wrote `cli/tests/test_lock.py` first: mutual-exclusion (two real threads,
`Event`-gated, asserted by call-order not timing), release-on-normal-exit,
release-on-exception (never leaves the lock held if the critical section raises),
and a bounded-timeout test proving `LockTimeout` fires rather than hanging when a
lock is already held. Also added a `create_artifact_with_lock`-specific test that
reproduces the exact diagnosed race shape (delayed "scan" step, forcing the second
caller to attempt entry mid-scan) and asserts the two calls are fully serialized
(`scan-start-1, scan-end-1, scan-start-2, scan-end-2`, never interleaved) and
produce distinct IDs. All 6 passed on first implementation; ran 5x to rule out
flakiness.

Then went call site by call site, task → bug → spec, each following red→green:
wrote a regression test that drives the command function directly (discovered along
the way that `CliRunner.invoke()` is not thread-safe — it patches global
`sys.stdout` per call, so concurrent `invoke()` calls in different threads corrupt
each other; switched to calling `new_task`/`new_bug`/`new_spec` directly), forcing
the race deterministically by monkeypatching each module's `slugify` (the
diagnosis's named gap between "id computed" and "write happens") to pause the first
caller on an `Event` with a bounded 5s safety-net wait. Verified each test failed
against the pre-fix command code (for `spec.py` the fix had been applied before its
test was written by mistake — caught this, used `git stash` to temporarily revert
just that file, reran the test to confirm red, then restored the fix, to keep the
red→green evidence honest). Refactored each command's `new_*` function to build a
`build(id)` closure and call `create_artifact_with_lock`, catching both
`ArtifactExists` and `LockTimeout` the same way the existing `ArtifactExists`
handling already did. All three passed immediately after wiring.

Ran the bug's full manual Fix Verification script (5-way parallel real
subprocesses, not just in-process threads) against a fresh scratch project for all
three commands post-fix: `task new` → `T-001..T-005`, `bug new` → `B-001..B-005`,
`spec new` → `S-001..S-005`, zero duplicates in every run.

One process hygiene incident worth flagging for the record: while running the
manual verification script, an early version did `cd cli && uv run ai-team ...`
which left the shell inside `cli/` — since `cli/` is nested under this repo's own
`.ai-team.toml` (pointing at `docs/ai-team`), `find_project_root` walked up and
resolved the *real* project directory instead of the intended scratch directory,
briefly creating 5 real (untracked) task files under `docs/ai-team/tasks/pending/`
plus a `.ai-team.lock` sentinel file under `docs/ai-team/`. Caught immediately via
`git status --short`, deleted all of them before anything was staged or committed,
and re-ran verification using subshells with explicit `cd "$SCRATCH"`.
`git status --short` is clean; nothing from this incident is in any commit.

Also caught and fixed a lint gap: the `bug.py` commit left an unused
`write_artifact` import (the pre-commit hook only runs `ruff format --check`, not
`ruff check`, so it didn't block the commit). Found it via `uv run ruff check .`
while finishing the `spec new` cycle, fixed it with `ruff check --fix` (also
normalized import ordering across all three command modules, which ruff's isort
flagged once the import lists changed), and folded it into the `spec new` commit.
Full suite (446 tests), `ruff format --check`, `ruff check`, and `uv build` are all
clean at the end of the session.

Nothing remains outstanding against the fix contract: all three allocation sites
are fixed, tested at both the lock-primitive and call-site levels, and manually
verified with real concurrent processes. Nothing in
`cli/src/ai_team/init/sources/`, `cli/src/ai_team/templates/`, or
`cli/docs/commands.md` needed changes — this fix is purely internal to the CLI's
command implementation and doesn't alter any documented command signature or
output format, so no scaffold sync or doc regeneration was needed. Flagged for the
reviewer specifically: the choice of `flock` over a stale-timestamp-based lockfile
(staleness handling is automatic/kernel-based rather than manually coded), the
default 10s lock-acquisition timeout in `allocation_lock`/`create_artifact_with_lock`
(not currently exposed as a CLI flag — judged out of scope for this bug), and the
decision to centralize the shared helper in `core/lock.py` rather than
`core/ids.py` (both were named as acceptable locations in the diagnosis; `lock.py`
was chosen since the helper's job is fundamentally "hold the lock across
scan+write", not id-computation itself).

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
