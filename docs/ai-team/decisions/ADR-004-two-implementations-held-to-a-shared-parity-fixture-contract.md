---
id: ADR-004
title: Two implementations held to a shared parity-fixture contract
status: accepted
created: '2026-09-30'
---

# ADR-004: Two implementations held to a shared parity-fixture contract

## Context

S-005 (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`,
approved v1.0) gives the pi coding agent an in-process `ai_team` tool backed by a TypeScript
artifact core, so pi needs no Python at runtime. The human chose to keep the Python CLI as
the implementation for Claude Code and Codex rather than retire it. The framework now has
two implementations of every deterministic action: creating artifacts, lifecycle moves,
listing, validation, reporting, archive, check-layout and init.

Two implementations drift unless one contract binds them. That contract can't be either
codebase, and it can't be prose alone. Future work inherits this decision: S-005
sub-projects 3 to 5, and every later CLI change.

The framework version needs its own rule. S-003 Level 4 requires `[init].framework_version`
to equal the running distribution version exactly. The Python version comes from git
through hatch-vcs (`cli/pyproject.toml`) and changes on every commit.

## Decision

The Python CLI and the TS core are co-equal implementations: Python for Claude Code and
Codex, TS for pi. Both are held to one shared, repo-level contract:

- **Parity fixtures are the behavioural contract.** Each case in `fixtures/parity/` pins the
  command, clock, version, before tree, after tree, exit status and structured result. For
  errors and structured results, fixtures compare the message field and not the
  remediation hint. The fixtures are seeded once from the amended Python CLI and are then
  maintained as the source of truth. They are never regenerated from either implementation.
  One pytest runner and one vitest runner both auto-discover every case, and a fixture diff
  fails both.
- **A behaviour change starts with a fixture change.** Changing fixtures is a reviewed
  maintainer decision. Both runners must then pass. Neither implementation may diverge
  first and have the fixtures follow it.
- **The command map is the single definition of the command surface.** It lists commands,
  arguments, flags, defaults and tool-field names. The sync, the `ai_team` tool schema and
  the rendered-skill marker checks all consume it. A CLI command change is made there and
  enforced by the sync and schema checks.
- **The version is never committed.** The distribution version comes from the source tree
  through hatch-vcs. The sync writes it into a git-ignored version file in the pi package,
  the same way hatch writes the untracked `_version.py`. The command map holds no version.
  Fixtures use a test-only version override shared by both implementations. A pi package
  and a Python CLI built from different commits report an S-003 Level 4 mismatch on each
  other's projects, and that is expected.
- **Python's user surface stays the same.** Python gains internal structured results only
  for the fixture runner. There are no new public `--json` flags, and S-003's deferral of a
  machine-readable `check-layout` contract still stands.

## Consequences

### Positive

- Claude/Codex users and pi users get byte-identical artifacts and the same structured
  results for the same inputs (S-005 SC-5).
- Drift is caught mechanically in both test suites, not at review.
- Later sub-projects have a stable, implementation-neutral contract to build on.

### Negative

- Every behaviour change costs a fixture update plus two implementations.
- Python command modules need an internal structured-result layer that exists only for the
  fixtures.
- Building the pi package from a checkout needs a one-time sync, and therefore Python, to
  produce the version file.

### Neutral

- Absolute root paths are the only normalisation fixtures allow.
- Hints can differ between implementations. For example, the pi adapter rewrites "Run
  'ai-team init'" into the equivalent tool instruction.

## Alternatives Considered

### Alternative A: Retire the Python CLI and use the TS core everywhere

**Description:** Replace the Python CLI with the TS core for all three targets.
**Rejected because:** The human chose to keep the Python CLI for Claude Code and Codex, and
a rewrite is out of S-005's scope.

### Alternative B: Semantic-only parity

**Description:** Compare parsed artifacts and results rather than bytes.
**Rejected because:** It lets formatting and serialisation drift go unnoticed, and it can't
guarantee that artifacts written by either implementation are identical.

### Alternative C: TS tests shell out to the Python CLI as the oracle

**Description:** Make the Python CLI the reference by running it from the TS test suite.
**Rejected because:** It makes Python a test dependency of the pi package and leaves no
implementation-neutral contract.

### Alternative D: Commit the version into the command map or generated resources

**Description:** Write the hatch-vcs version into committed pi resources.
**Rejected because:** The version changes on every commit, so the committed file would be
out of date as soon as it was committed, and a clean checkout followed by a sync would never
give an empty diff.
