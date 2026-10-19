# Architecture Consistency Review

**Ownership boundary:** this skill owns the consistency check for a *created or changed architecture artifact* — an ADR, spec, or change-request — confirming it stays consistent with every approved spec and accepted ADR. It does **not** review task plans: Gate 2's `spec-breakdown-review` independently checks task-plan consistency and readiness. The two reviews are separate skills with separate inputs — a changed artifact here, a task plan there.

Approved specs and accepted ADRs are both binding sources of truth. A new or changed decision can silently contradict something an existing spec or ADR already records, leaving two authoritative artifacts that disagree until someone notices by hand. This review catches that drift at the moment of change.

The result is a Findings block; the Architect role envelope wraps it in its standard output format — do not duplicate `Result:` or `Summary:` fields here.

## When This Runs

Whenever an architecture artifact changes:

- **New or accepted ADR** — after `new-adr` records the decision (run by the Architect).
- **New or amended spec** — after a spec is created (`new-spec`, before Gate 1 sign-off settles) or amended (an Amendment Log entry added during spec revision or change-request intake).
- **Completed work (spec-truth reconciliation, ADR-002)** — after the task queue drains and before the human gives Gate 5 sign-off. Here the trigger is completion, not a changed artifact; see **Completion Mode** below.
- **Change-request** — after the human approves a TODO-free change-request and before the proposed spec amendments are applied. The approved change-request is the authoritative intent for any Planner-owned consistency fixes.

## Completion Mode

In completion mode the review confirms that each approved spec is still true of what was built. It uses the same binding set, findings block, routing rules, and verdicts as every other trigger, with these differences:

- **Changed artifact** — each approved spec touched by the completed work, named by the caller. Do not review specs the work did not touch.
- **Evidence read in place of a delta** — the Work Logs of the completed tasks and resolved bugs that implemented the spec, every ADR created or amended while the work was in flight, and the deferred-Minor findings roll-up (`status-report`).
- **Step 1** isolates what the spec asserts (requirements, interfaces, guarantees) instead of what changed.
- **Step 3** checks each assertion against the evidence: a requirement the work did not deliver, behavior the work added that the spec does not describe, or an interface that now differs. Record each drift with the spec statement and the evidence that contradicts it.
- **Routing** is unchanged: the Planner amends the approved spec on a planning branch and records the change in its Amendment Log; the Architect amends or supersedes ADRs; a drift that needs a decision beyond an amendment escalates.

A `PASS` means every touched spec is still true. Gate 5 accepts a `PASS`, or a `FAIL` whose routed amendments have all been applied.

## Input Requirements

- **Changed artifact** — the ADR, spec, or change-request just created or amended, and which kind it is; in completion mode, the approved specs the completed work touched. If it was not provided, return `BLOCKED`.
- **Decision records** — all ADRs in `{{project_dir}}/decisions/`; treat `accepted` ones as binding.
- **Specifications** — all specs in `{{project_dir}}/specs/`; treat `approved` ones as binding.
- **Change scope** — for an amendment or change-request, the specific decision, section, or requirement that changed.

## Procedure

### Step 1: Isolate What Changed

Identify exactly what decision, requirement, or contract the changed artifact now asserts. For an amendment or change-request, isolate the delta — not the whole document.

For an approved change-request, treat the approved change-request itself as the authoritative intent. The review checks the binding set against that approved intent; it does not reinterpret the requested change through downstream draft wording.

### Step 2: Read the Binding Set

Read every accepted ADR in `{{project_dir}}/decisions/` and every approved spec in `{{project_dir}}/specs/`. These are the artifacts the change must not contradict.

### Step 3: Check for Contradiction

For each binding artifact, decide whether the changed artifact contradicts it — asserts a different decision for the same concern, removes a guarantee another artifact relies on, or restates a rule with different content. Record each contradiction with the specific artifact, the conflicting statements, and which one is now intended to be authoritative.

### Step 4: Report Findings and Route Corrections

This review **reports** contradictions as findings to the owning role — it does not edit specs or apply amendments itself. This is the same model as `spec-breakdown-review`, which returns findings to the Planner for revision. Route each contradiction by which artifact is the wrong side:

- **The changed artifact is a pre-Gate-1 draft spec** → return the findings to the Planner, who revises the draft directly. Do **not** add an Amendment Log entry — a draft's Amendment Log stays empty until Gate 1 approval. The Architect and Planner iterate until the draft is consistent; the human then approves at Gate 1 as usual.
- **An approved spec is the affected side** → return the findings to the Planner, who amends the approved spec in place — on the planning branch of the spec or change-request under review, never directly on `{{integration_branch}}` — and records the change in its Amendment Log, naming the driving ADR ID when an ADR caused the change. For findings raised from an approved change-request, the Planner uses the approved change-request as the authoritative intent while applying those consistency fixes.
- **An ADR is the affected side** → the Architect amends or supersedes the ADR; use `new-adr` to record a superseding decision.
- **A finding can be resolved procedurally without changing the approved change-request intent** → route the correction to the owning role and continue; Planner-owned amendments stay anchored to the approved change-request.
- **A finding would change the approved change-request intent** → stop and ask the Human to revise, reject, or reaffirm the CR before any downstream artifact is amended.
- **Reconciling the drift requires changing an approved spec beyond an in-flight amendment** → escalate to the human through the Planner per the escalation procedure.

The Architect reports findings and routing; the Architect never edits specs directly. Draft revision and approved-spec amendment are both the Planner's.

### Step 5: Produce the Verdict

- No contradiction → `PASS`: the change is consistent with the binding set.
- Contradictions with a clear owner and routing → `FAIL` with the named corrections.
- A contradiction that requires changing an approved spec → `ESCALATE`.
- A contradiction that would change approved change-request intent → `ESCALATE` to the Human so the CR can be revised, rejected, or reaffirmed.

## Output Format

The Architect role envelope wraps the Findings block produced here. Do not add a top-level `Result:` or `Summary:` outside this block; those belong to the Architect envelope.

```text
Result: PASS | FAIL | BLOCKED | ESCALATE

Artifact reviewed: <path of the changed ADR / spec / change-request>
Binding set checked: <count> accepted ADRs, <count> approved specs

Findings:
- <artifact>: <the contradiction and which statement is authoritative>

Corrections routed:
- <artifact>: <Planner draft revision | Planner approved-spec amendment | Architect ADR amendment/supersede | escalation>

Next owner:
- Planner | Architect | Human | none
```

`BLOCKED` is returned when the changed artifact was not provided. When `Result` is `ESCALATE`, append an Escalation Request block and then a Phase 2 Human Escalation Report using the template defined in the `escalation-review` skill.

## Quality Criteria

- Every accepted ADR and approved spec was read before the verdict.
- Each contradiction names the exact conflicting statements, not a vague "may conflict."
- Corrections are routed to the owning role (Planner for specs, Architect for ADRs); the Architect never edits specs directly.
- An approved change-request remains the authoritative intent for Planner-owned consistency fixes until the Human changes that intent.
- Escalation is used only when reconciling the drift requires changing an approved specification or would change approved change-request intent.

## Common Pitfalls

- **Skipping the evidence in completion mode.** A spec cannot be confirmed from the spec alone; read the Work Logs and mid-flight ADRs.
- **Reviewing the whole artifact instead of the change.** For an amendment, check the delta against the binding set, not every line.
- **Editing a spec to fix drift.** Specs are the Planner's; route the amendment, do not write it.
- **Treating a `proposed` ADR or `draft` spec as binding.** Only `accepted` ADRs and `approved` specs constrain the change.
- **Silently passing a near-miss.** If two artifacts describe the same decision with different content, that is drift even when neither says the other is wrong.
