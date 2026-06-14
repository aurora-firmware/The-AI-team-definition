---
id: B-012
title: Integrate task completion can leave the in-progress path tracked
severity: medium
status: resolved
created: '2026-06-14'
---

# Integrate task completion can leave the in-progress path tracked

## Summary

The `integrate` skill tells the integrator to move a completed task, update its
status, stage, and commit, but it does not require a deletion-aware git operation
or verify that the old in-progress path is no longer tracked. An integration can
therefore commit the completed copy while leaving the in-progress copy in HEAD,
making one task appear in two lifecycle states and leaving an unexpected dirty
working tree.

## Reproduction Status

Status: confirmed

Observed during integration of T-084 in the consuming project. Current
`integrate` source still describes a generic move followed by staging and has no
post-commit tracked-path or working-tree check for the old path.

## Evidence

- Logs / stack traces / failing assertions: Commit `c416916`
  (`chore(tasks): move T-084 to completed`) added the completed task copy but did
  not delete the tracked in-progress copy. Follow-up commit `2a4b4c9` was needed
  to remove it.
- Screenshots or recordings: n/a
- Failing command or test: after the completion commit,
  `git status --porcelain project/tasks/in-progress/` showed the deletion as an
  unstaged change while HEAD still tracked the old path.
- Source inspection:
  `cli/src/ai_team/init/sources/skills/integrate/body.md`, Step 7, says to move,
  update, stage, and commit without requiring `git mv`/equivalent or checking the
  old path.

## Reproduction Steps

1. Integrate a task branch and reach Step 7 of the `integrate` skill.
2. Physically move the task from `project/tasks/in-progress/` to
   `project/tasks/completed/`, update its status, and stage only the completed
   path.
3. Commit the lifecycle update.
4. Observe that HEAD contains both paths and the working tree contains an
   unstaged deletion for the in-progress path.

## Expected Behavior

The completion commit must atomically record both deletion of the in-progress
path and addition of the completed path. Before reporting success, integration
must verify that the old path is neither tracked nor dirty and that the
destination branch is clean.

## Actual Behavior

The procedure allows the completion commit to add the completed copy without
recording deletion of the in-progress copy. The duplicate lifecycle state may
persist in git history and interfere with the next loop iteration.

## Environment

- OS / platform: Linux
- Language / runtime version: n/a
- Relevant dependencies: `integrate` skill and git
- Branch / commit: `dev-agent`, inspected 2026-06-14

## Related

- Task: surfaced while integrating T-084 in the consuming project
- Specification: n/a
- External evidence: `/home/daneel/projects/the-intern/ai-process-cli-reported-issues.md`,
  entry dated 2026-05-28

## Suspected Area

`cli/src/ai_team/init/sources/skills/integrate/body.md`, Step 7, and generated
Claude/Codex integrate scaffolds.

## Fix Verification

```bash
# Source and generated integrate skills must require a deletion-aware move and
# verify the old path/working tree before success.
uv run pytest
uv run ruff format --check .
uv run ruff check .
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

### Diagnosis 1 — 2026-06-14

**Reproduction status:** Confirmed.

**Evidence captured:** Current integrate source and both generated scaffolds
instruct the integrator to move the task file, update status, stage, and commit,
but do not require `git mv` or `git rm` plus `git add`. A minimal git
reproduction moved an in-progress task, staged only the completed path, and
committed; `git ls-tree` then showed both paths in HEAD and
`git status --porcelain project/tasks/in-progress/` showed an unstaged deletion.
The reported T-084 incident has the same commit history: the completion commit
contained both paths and a follow-up commit removed the stale copy.

**Isolated fault:** Integrate Step 7.1 permits a plain filesystem move plus
staging only the destination. Step 7.4 reports success without verifying that
the old path is absent from the index and working tree.

**Root cause or fault hypothesis:** Root cause confirmed. The integration
procedure omits a required deletion-aware git operation and a defensive
post-move invariant check.

**Planned verification:** Require `git mv` or `git rm` plus `git add` in the
integrate source and generated scaffolds. Add an explicit check that
`git status --porcelain project/tasks/in-progress/` is empty before success,
then run the full repository test and lint checks.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-14

Read the canonical bug file and Diagnosis Log as the implementation contract.
Added regression tests that require the integrate source plus both generated
scaffolds to mention a deletion-aware task completion move (`git mv`, or repair
via `git rm` plus `git add`) and an explicit
`git status --porcelain project/tasks/in-progress/` emptiness check before
success. Verified the new tests failed against the existing procedure.

Updated only the source-of-truth integrate procedure in Step 7. The task-file
move now requires a git-aware operation that records deletion and addition, and
the success path requires the old in-progress path to be clean before reporting
success. Regenerated the Claude and Codex integrate scaffolds from source.

The focused regression tests passed after the change. Full checks from `cli/`
also passed: `uv run pytest` reported 376 passing tests,
`uv run ruff format --check .` reported all files formatted, and
`uv run ruff check .` passed. Commands used `UV_CACHE_DIR=/tmp/uv-cache`.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-06-14

PASS

Stage 1 passed. The Diagnosis Log documents confirmed reproduction, isolated Step
7 as the fault, and ties the fix to the root cause by requiring a deletion-aware
task-file move plus an explicit old-path cleanliness check before success. The
submitted diff is limited to the integrate source, both generated integrate
scaffolds, and regression tests.

Stage 2 passed. `cli/tests/test_t063_integration_guards.py` now covers the
required `git mv` / `git rm` + `git add` wording and the
`git status --porcelain project/tasks/in-progress/` emptiness check across the
source text and both generated scaffolds. Verification rerun on the source
branch succeeded with `UV_CACHE_DIR=/tmp/uv-cache uv run pytest`
(`376 passed`), `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_t063_integration_guards.py`
(`12 passed`), `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .`, and
`UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .`.
