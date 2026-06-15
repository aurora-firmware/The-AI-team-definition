---
id: B-011
title: Accepted ADR changes can leave approved specs stale without validation 
  findings
severity: medium
status: resolved
created: '2026-06-14'
---

# Accepted ADR changes can leave approved specs stale without validation findings

## Summary

`ai-team validate` cannot detect when an accepted ADR changes decisions that
approved specs still describe the old way. ADRs can only declare an optional
ADR-to-ADR `supersedes` reference; they cannot name affected specs, and
validation has no amendment-freshness check. As a result, accepted decisions and
their dependent source-of-truth specs can silently contradict one another until
manual review finds the drift.

## Reproduction Status

Status: confirmed

Confirmed from the reported ADR-005 incident and from current source inspection.
The current ADR model and validator support only `supersedes`, and the validator
only checks that the referenced ADR exists.

## Evidence

- Logs / stack traces / failing assertions: In the consuming project, accepted
  ADR-005 made socket filesystem permissions the sole connection gate, while
  approved specs S-002, S-003, and S-005 continued to describe a
  `perms + SO_PEERCRED` gate and removed uid/gid configuration. `ai-team
  validate` emitted no finding.
- Screenshots or recordings: n/a
- Failing command or test: `ai-team validate --all` does not report an accepted
  ADR whose affected approved specs lack a post-ADR amendment record.
- Source inspection:
  `cli/src/ai_team/core/models.py` defines only optional ADR `supersedes`;
  `cli/src/ai_team/core/validate.py` only validates that reference resolves.

## Reproduction Steps

1. Create approved specs that document a decision.
2. Accept a later ADR that changes that decision without updating every affected
   spec.
3. Run `ai-team validate --all`.
4. Observe that validation succeeds despite the accepted ADR and approved specs
   contradicting one another.

## Expected Behavior

An accepted ADR that changes a decision must not be able to leave a dependent
approved spec silently contradicting it. The framework guarantees this through a
review duty rather than a metadata cross-check: whenever a spec or an ADR
changes, the Architect reviews the change for compatibility with every other
approved spec and accepted ADR, names any drift, and routes the amendments
(Planner amends specs; Architect amends or supersedes ADRs), escalating to the
human when reconciling the drift requires a spec change.

## Actual Behavior

ADRs cannot identify affected specs. Validation checks ADR identifier format and
whether `supersedes` resolves to another ADR, but emits no finding for stale
dependent specs.

## Environment

- OS / platform: Linux
- Language / runtime version: Python `ai-team` CLI
- Relevant dependencies: ADR/spec frontmatter models and `ai-team validate`
- Branch / commit: `dev-agent`, inspected 2026-06-14

## Related

- Task: n/a
- Specification: n/a
- External evidence: `/home/daneel/projects/the-intern/ai-process-cli-reported-issues.md`,
  entry dated 2026-06-13

## Suspected Area

Framework contract for ADR amendments, plus
`cli/src/ai_team/core/models.py`, ADR creation/template sources, and
`cli/src/ai_team/core/validate.py`.

## Fix Verification

The resolution is a process duty, not an automated rule, so verification is
documentary:

- `ai-process/processes/quality-gates.md` defines the **Architecture Consistency
  Review** as a standing Architect duty triggered on any spec or ADR change.
- `ai-process/processes/escalation-procedure.md` routes an amended spec into that
  review.
- The Architect role (`agents/.../architect`) lists the review among its
  responsibilities and decision authority.
- `uv run pytest` stays green with no ADR/spec freshness validation rule present.

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

**Reproduction status:** Confirmed. A minimal temporary project containing an
approved spec that states an old connection-gate rule and an accepted ADR that
replaces that rule produced no validation findings.

**Evidence captured:** Running `validate --all --json` against the fixture
returned exit code 0 and `[]`. Source inspection confirmed that ADR metadata and
creation support only `supersedes`, while `validate_project()` checks spec IDs
and filenames plus ADR IDs and unresolved `supersedes` references. The existing
validation tests pass without covering accepted-ADR-to-spec freshness.

**Isolated fault:** The ADR/spec validation contract and implementation have no
data path that correlates accepted ADRs with affected specs or their amendment
records.

**Root cause or fault hypothesis:** Root cause confirmed. Validation was
originally scoped to artifact shape, lifecycle state, and direct-reference
resolution. ADR references were restricted to `supersedes`, leaving no
machine-readable affected-spec relationship and no freshness rule.

**Planned verification:** Add a regression fixture containing an accepted ADR
that declares affected approved specs and a spec whose amendment record omits
the ADR-driven change. Verify `validate --all --json` emits a finding for the
stale spec, then run the focused and full CLI test suites.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-06-14

Read the canonical bug file and Diagnosis Log before making code changes.
Reproduced the contract first with a new validation regression test: an accepted
ADR naming an affected approved spec with no later Amendment Log entry produced
no finding on the old code.

Implemented the fix in two TDD cycles. Extended ADR frontmatter with optional
`affected-specs`, then taught `validate` to cross-check accepted ADRs against
approved specs and emit `adr-affected-spec-stale` when the spec has no Amendment
Log row on or after the ADR date that references the ADR ID. Added model
round-trip coverage and `ai-team adr new --affects-spec`, so new ADRs can record
affected specs without manual frontmatter edits.

Updated the spec template and authoring guide to require ADR-driven Amendment
Log rows to include the ADR ID. Updated the `new-adr` skill source, regenerated
Claude and Codex scaffolds, and regenerated `cli/docs/commands.md`.

Focused regression and metadata tests passed, followed by full repository
checks from `cli/`: `uv run pytest` reported 374 passing tests, and both
`uv run ruff format --check .` and `uv run ruff check .` passed. Commands used
`UV_CACHE_DIR=/tmp/uv-cache` because the default cache was not writable.

### Session 2 — 2026-06-15

Revised the resolution during PR review. The `affected-specs` field is a
denormalised pointer that only catches drift an ADR author remembered to
declare, so it cannot *guarantee* spec/ADR consistency — it only spot-checks the
cases someone already noticed. The team decided the real guarantee is a review
duty, not a validation rule.

Reverted the entire B-011 mechanism: removed the `affected-specs` ADR field and
its helper from `models.py`, the `--affects-spec` CLI option from `adr.py`, the
`adr-affected-spec-missing`/`adr-affected-spec-stale` rule and amendment-scan
helpers from `validate.py`, the matching tests, the `new-adr` skill mention, and
the ADR-ID-in-row recipe lines from the spec template and authoring guide.

Added the replacement: an **Architecture Consistency Review** standing duty in
`ai-process/processes/quality-gates.md`, referenced from
`escalation-procedure.md` (spec-amendment path) and from the Architect role
(Claude `architect.md` and Codex `architect.toml`). Regenerated scaffolds and
`cli/docs/commands.md`. Full checks from `cli/` rerun with
`UV_CACHE_DIR=/tmp/uv-cache`.

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

Stage 1 passed. The Diagnosis Log evidence chain is complete and matches the
implemented fix: ADR frontmatter now supports `affected-specs`, `validate`
cross-checks accepted ADRs against approved specs and their Amendment Log
entries, and the ADR CLI/docs/templates were updated so the contract is
recordable and reviewable.

Stage 2 passed. Reviewed `cli/src/ai_team/core/models.py`,
`cli/src/ai_team/core/validate.py`, `cli/src/ai_team/commands/adr.py`, the
regression tests, and the spec-authoring/template updates. Regression coverage
exercises the stale-spec finding path and the new ADR metadata/CLI round-trip.
Verification on the implementation branch passed with `UV_CACHE_DIR=/tmp/uv-cache
uv run pytest tests/test_validate.py tests/test_models.py tests/test_adr_new.py`,
full `UV_CACHE_DIR=/tmp/uv-cache uv run pytest` (374 passed), and both Ruff
checks from `cli/`.

### Review Verdict — 2026-06-15
PASS

Resolution revised during PR review (see Work Log Session 2). The validation
mechanism was the wrong tool for this invariant — a declared-only cross-check
cannot guarantee spec/ADR consistency — so it was reverted in full and replaced
with the Architecture Consistency Review, a standing Architect duty that fires on
any spec or ADR change. The duty is owned once in `quality-gates.md` and
referenced from `escalation-procedure.md` and the Architect role, matching the
framework's "own a shared rule in one place" convention. Verified the mechanism
is fully removed (no `affected-specs`/`adr-affected-spec-*` remnants), scaffolds
and `cli/docs/commands.md` regenerate with no diff, and the full suite plus both
Ruff checks pass from `cli/`.
