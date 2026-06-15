# Architecture Consistency Review

**Ownership boundary:** this skill owns the consistency check — whether a created or changed architecture artifact stays consistent with every approved spec and accepted ADR. It is the single definition of that check. Gate 2 (`spec-breakdown-review`) applies it to a task plan; the ADR, spec, and change-request flows apply it to a changed artifact. It does **not** own task-plan readiness (coverage, dependencies, atomicity) — that stays in `spec-breakdown-review`.

Approved specs and accepted ADRs are both binding sources of truth. A new or changed decision can silently contradict something an existing spec or ADR already records, leaving two authoritative artifacts that disagree until someone notices by hand. This review catches that drift at the moment of change.

The result is a Findings block; the Architect role envelope wraps it in its standard output format — do not duplicate `Result:` or `Summary:` fields here.

## When This Runs

Whenever an architecture artifact changes:

- **New or accepted ADR** — after `new-adr` records the decision (run by the Architect).
- **New or amended spec** — after a spec is created (`new-spec`, before Gate 1 sign-off settles) or amended (an Amendment Log entry added during spec revision or change-request intake).
- **Change-request** — before a change-request's proposed spec amendments are applied.

## Input Requirements

- **Changed artifact** — the ADR, spec, or change-request just created or amended, and which kind it is. If it was not provided, return `BLOCKED`.
- **Decision records** — all ADRs in `project/decisions/`; treat `accepted` ones as binding.
- **Specifications** — all specs in `project/specs/`; treat `approved` ones as binding.
- **Change scope** — for an amendment or change-request, the specific decision, section, or requirement that changed.

## Procedure

### Step 1: Isolate What Changed

Identify exactly what decision, requirement, or contract the changed artifact now asserts. For an amendment or change-request, isolate the delta — not the whole document.

### Step 2: Read the Binding Set

Read every accepted ADR in `project/decisions/` and every approved spec in `project/specs/`. These are the artifacts the change must not contradict.

### Step 3: Check for Contradiction

For each binding artifact, decide whether the changed artifact contradicts it — asserts a different decision for the same concern, removes a guarantee another artifact relies on, or restates a rule with different content. Record each contradiction with the specific artifact, the conflicting statements, and which one is now intended to be authoritative.

### Step 4: Route Corrections

For every contradiction found:

- **Affected spec** → the Planner amends the spec in place and records the change in its Amendment Log, naming the driving ADR ID when an ADR caused the change. The Architect does not edit specs.
- **Affected ADR** → the Architect amends or supersedes the ADR; use `new-adr` to record a superseding decision.
- **Reconciliation needs an approved-spec change beyond an in-flight amendment** → escalate to the human through the Planner per the escalation procedure.

### Step 5: Produce the Verdict

- No contradiction → `PASS`: the change is consistent with the binding set.
- Contradictions with a clear owner and routing → `FAIL` with the named corrections.
- A contradiction that requires changing an approved spec → `ESCALATE`.

## Output Format

The Architect role envelope wraps the Findings block produced here. Do not add a top-level `Result:` or `Summary:` outside this block; those belong to the Architect envelope.

```text
Result: PASS | FAIL | BLOCKED | ESCALATE

Artifact reviewed: <path of the changed ADR / spec / change-request>
Binding set checked: <count> accepted ADRs, <count> approved specs

Findings:
- <artifact>: <the contradiction and which statement is authoritative>

Corrections routed:
- <artifact>: <Planner amendment | Architect ADR amendment/supersede | escalation>

Next owner:
- Planner | Architect | Human | none
```

`BLOCKED` is returned when the changed artifact was not provided. When `Result` is `ESCALATE`, append an Escalation Request block and then a Phase 2 Human Escalation Report using the template defined in the `escalation-review` skill.

## Quality Criteria

- Every accepted ADR and approved spec was read before the verdict.
- Each contradiction names the exact conflicting statements, not a vague "may conflict."
- Corrections are routed to the owning role (Planner for specs, Architect for ADRs); the Architect never edits specs directly.
- Escalation is used only when reconciling the drift requires changing an approved specification.

## Common Pitfalls

- **Reviewing the whole artifact instead of the change.** For an amendment, check the delta against the binding set, not every line.
- **Editing a spec to fix drift.** Specs are the Planner's; route the amendment, do not write it.
- **Treating a `proposed` ADR or `draft` spec as binding.** Only `accepted` ADRs and `approved` specs constrain the change.
- **Silently passing a near-miss.** If two artifacts describe the same decision with different content, that is drift even when neither says the other is wrong.
