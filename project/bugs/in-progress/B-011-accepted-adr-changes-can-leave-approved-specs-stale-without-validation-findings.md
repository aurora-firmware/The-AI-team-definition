---
id: B-011
title: Accepted ADR changes can leave approved specs stale without validation 
  findings
severity: medium
status: in-progress
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

Accepted ADRs must have a machine-readable way to identify the specs or prior
decisions they amend, and validation must report affected approved specs that
have not recorded a corresponding amendment after the ADR was accepted.

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

```bash
# A fixture containing an accepted ADR with an affected approved spec that lacks
# a post-ADR amendment record must produce a validation finding.
uv run pytest cli/tests/test_validate.py
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
