---
id: ADR-003
title: Each implementation owns its ID-allocation lock; mixed concurrent 
  allocation is unsupported
status: accepted
created: '2026-09-30'
---

# ADR-003: Each implementation owns its ID-allocation lock; mixed concurrent allocation is unsupported

## Context

S-005 (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`,
approved v1.0) adds a TypeScript artifact core for pi beside the Python CLI. Both allocate
artifact IDs (T-NNN, B-NNN, S-NNN, ADR-NNN) by scanning existing files and writing the next
one.

The Python CLI fixed the scan-then-write race in B-014 with `ai_team.core.lock`. It holds
`fcntl.flock` on a sentinel file `<project_dir>/.ai-team.lock` for the whole
allocate-and-write step. The kernel releases a `flock` when the holder's file descriptor
closes, including on a crash or `kill -9`, so no stale lock can exist. The sentinel file
stays on disk permanently. B-017 then added the project skeleton `.gitignore`
(`cli/src/ai_team/init/sources/project/.gitignore`) so that the sentinel is never reported
as untracked. Tests in `test_init_scaffolds.py`, `test_init.py` and `test_usage_guide.py`,
plus `cli/docs/usage.md`, pin that contract.

Node has no native `flock`. Sharing Python's lock would mean either a native addon or
changing Python to a create-exclusive lockfile, which would reverse B-014's crash-safety
rationale. The TS core also can't use `.ai-team.lock` with create-exclusive semantics.
Python never deletes that file, so the TS core would never get the lock in any project
Python had touched.

The human decided during S-005 review that each implementation keeps its own lock.

## Decision

Each implementation owns its ID-allocation lock:

- The Python CLI keeps `fcntl.flock` on `<project_dir>/.ai-team.lock`, unchanged.
- The TS core uses its own lock at a separate path inside the project artifact directory.
  Taking the lock is atomic. Holder liveness is detectable, so a dead holder's lock is
  reclaimed. The bounded wait and the core timeout message match the Python CLI.
- The project skeleton `.gitignore` gains the TS lock path, so both implementations' `init`
  output includes it. The parity fixtures record this, and the B-017 tests and
  `cli/docs/usage.md` are updated deliberately to match.

Within one implementation, concurrent allocations never produce the same ID. A Python
process and a pi session allocating concurrently in the same working tree is unsupported.
The pi package README and `guides/setup-guide.md` say so.

## Consequences

### Positive

- B-014's crash safety is preserved in Python without change, and the TS lock is held to the
  same crash-safety requirement (S-005 SC-7).
- Neither implementation needs a native addon or a cross-language lock protocol.
- Existing Python behaviour, stdout, stderr and exit codes stay unchanged (S-005 SC-6).

### Negative

- Mixed concurrent allocation in one working tree can produce duplicate IDs. Teams have to
  avoid running a Python allocation and a pi allocation at the same moment in the same tree.
- The TS lock has its own reclaim logic, which needs its own tests (S-005 SC-7).
- The project skeleton `.gitignore` changes, so the B-017 tests and docs have to be updated.

### Neutral

- Separate clones or worktrees never shared a lock anyway. Their ID collisions surface at
  merge, as they do today.
- If agent runners (S-005 sub-project 3) later mix implementations in one working tree, this
  decision has to be revisited.

## Alternatives Considered

### Alternative A: Shared cross-language lock protocol

**Description:** Replace Python's `flock` with a lockfile protocol, for example
create-exclusive plus a PID and stale detection, that both implementations follow.
**Rejected because:** It reverses B-014's "kernel releases the lock, no stale lock"
rationale for Python and adds stale-lock handling to a path that doesn't need it today, only
to support a mixed case the human chose not to support.

### Alternative B: Native `flock` addon for Node

**Description:** Call `flock` from the TS core through a native module, so it can share
`.ai-team.lock` with Python.
**Rejected because:** Native builds complicate installing from a local path. It also ties
the pure TS core to the platform, which goes against S-005's "the core is free of pi" and
portability goals.

### Alternative C: TS core reuses `.ai-team.lock` with existence semantics

**Description:** Treat the presence of `.ai-team.lock` as "locked".
**Rejected because:** Python never deletes the sentinel, so in any project Python had
touched, the TS core would wait until the timeout and never allocate.
