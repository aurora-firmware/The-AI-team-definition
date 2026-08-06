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
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
