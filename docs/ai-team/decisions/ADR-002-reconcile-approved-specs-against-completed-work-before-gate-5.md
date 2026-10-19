---
id: ADR-002
title: Reconcile approved specs against completed work before Gate 5
status: accepted
created: '2026-10-19'
---

# ADR-002: Reconcile approved specs against completed work before Gate 5

## Context

Approved specs stay true while work is in flight: the Amendment Log records scope changes
during execution, and `architecture-consistency-review` runs whenever a spec, ADR, or
change-request changes. Nothing reconciles a spec against what was actually built once the
work is done.

Gate 5's pass criterion is that "the status summary matches the approved specification" — a
human comparing a summary to a spec, not a check of the completed work against the spec. A
spec can therefore be approved, implemented with undocumented deviations, and signed off while
no longer describing the system. The framework's central promise is that specs and ADRs are
always true; today that holds by planning-time discipline, not by a gate at the end.

The comparison report in `docs/ai-team/docs/superpowers_comparison.md` (section 7) identified
this gap, and issue #31 tracks closing it.

## Decision

Add a standing duty, **spec-truth reconciliation**, that runs after the task queue drains and
before the human gives Gate 5 sign-off.

The Architect re-reads each approved spec touched by the completed work against the completed
task and bug Work Logs, any ADRs created while the work was in flight, and the deferred-Minor
roll-up, then either confirms the spec is still true or routes amendments to the Planner.

It reuses `architecture-consistency-review` rather than adding a skill: same binding set, same
findings block, same routing rules (the Planner amends approved specs and records the change
in the Amendment Log; the Architect amends or supersedes ADRs), same escalation path. Only the
trigger differs — completion of the work instead of change to an artifact.

Gate 5 gains a pass criterion: the latest reconciliation returned `PASS`, or every amendment
it routed has been applied.

## Consequences

### Positive

- "Specs and ADRs are always true" becomes a property enforced by a gate, not only by planning
  discipline.
- Deviations discovered during implementation are surfaced as spec amendments before sign-off.
- No new skill, role, or routing rule to maintain.

### Negative

- One more Architect pass per release, which costs time and tokens on large specs.
- Gate 5 can be delayed while amendments are applied.

### Neutral

- The Architect still never edits specs; the Planner owns amendments, as before.
- The reconciliation is triggered by the human or the loop's suggested next action, because the
  loops end with a short run summary and do not invoke reviews on their own.

## Alternatives Considered

### Alternative A: A separate reconciliation skill

**Description:** Author a `spec-reconciliation` skill with its own procedure and output.
**Rejected because:** It would duplicate the binding-set reading, findings format, and routing
rules of `architecture-consistency-review`, and the two copies would drift.

### Alternative B: Keep the human comparison at Gate 5

**Description:** Leave the status-summary-versus-spec comparison as the only check.
**Rejected because:** It compares a summary to a spec, not completed work to a spec, and relies
on the human noticing deviations that no artifact records.
