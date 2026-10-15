# Gate 2 Preflight

**Ownership boundary:** spec-breakdown-review owns Gate 2 technical readiness — it validates whether a task plan is safe to hand to `/dev-loop`.
Plan content (coverage decisions, splitting, EARS-pattern authoring in the task template at `cli/src/ai_team/templates/task.md`) is owned by `spec-breakdown` and `new-task`.
The result of this skill is a Findings block; the architect role envelope wraps it in its standard output format — do not duplicate `Result:` or `Summary:` fields here.

## Input Requirements

- **Approved specification** — the spec that passed Gate 1.
- **Planned task files** — the task plan listed by `ai-team list tasks --state planned --spec <spec-or-cr-id>`; `ai-team show <task-id> --json` reports each file's path.
- **Decision records** — existing ADRs in `project/decisions/`.
- **Project structure** — current files needed to verify paths and conflict risk.

## Procedure

Gate 2 is a technical preflight. During review, focus findings only on technical task-plan readiness: dependency correctness, file conflict ordering, ADR/spec consistency, atomicity, and verifiable execution.

### Step 1: Read Planning Context

Read the approved specification and all task files for the plan under review.
Read existing decision records in `project/decisions/`.
Identify each task's dependencies, files to touch, acceptance criteria, and verification command.

### Step 2: Check Spec Coverage

Verify spec coverage: confirm that the full set of planned tasks covers the entire approved specification with no features, sections, or behaviors left unaddressed.
If any part of the spec is not covered by at least one task, flag the gap.
Do not pass Gate 2 if the plan leaves spec sections unimplemented without explicit justification.

### Step 3: Check Dependency Correctness

Verify that every declared dependency refers to a real task.
Check for missing dependencies where one task reads, modifies, or relies on files or behavior created by another task.
Flag circular dependencies.

### Step 4: Check File Conflict Risk

Identify tasks that create or modify the same file.
If overlapping edits are intentional, ensure a dependency orders them.
If no dependency exists, add the dependency directly when the correction is obvious; otherwise request Planner revision.

### Step 5: Check Architectural Consistency

Compare the task plan against existing ADRs and architecture docs.
If a task contradicts an existing decision or requires changing an approved specification, do not pass Gate 2.
When assessing architecture, if the plan contradicts the approved spec or existing ADRs, fail or escalate by following the existing Gate 2 procedure.
Use `new-adr` only when the plan exposes a durable architecture-affecting decision within the approved spec.
When invoking `new-adr`, provide the full required input set:
- `title`: concise decision title derived from the architectural choice
- `description`: the approved spec path, affected task IDs, relevant ADRs, and why the decision is durable rather than an implementation detail
- `status`: `accepted` — the Architect is adopting the decision now as part of approving the task plan
Escalate to human through the Planner when the approved spec must change.

### Step 6: Check Atomicity And Verification

Confirm each task is independently implementable and verifiable.
Flag tasks that exceed the one-shottable threshold:

- More than 3-4 files.
- More than 5 acceptance criteria.
- Description too large or ambiguous for one implementation session.
- No clear verification command.

### Step 7: Produce Verdict

If the plan passes, state that Gate 2 passes and the plan is ready to merge and activate for `/dev-loop`.

If the plan fails:

- For obvious missing dependencies or file-ordering issues, edit the affected task files directly.
- For decomposition or atomicity issues, return a correction request to the Planner with exact task IDs and required changes.
- Do not fail Gate 2 for product-scope concerns that do not block technical readiness; record them as non-blocking follow-up feedback.
- For spec contradictions, escalate because an approved specification change is required.

## Output Format

The architect role envelope wraps the Findings block produced here.
There are no duplicated Result/Summary fields in this output — do not add a top-level `Result:` or `Summary:` outside this block; those fields belong to the architect envelope and must not be repeated here.

Use this structure for the Findings block — matches the Architect agent's standard `Result:` vocabulary:

```text
Result: PASS | FAIL | BLOCKED | ESCALATE

Spec reviewed: project/specs/<file>
Tasks reviewed: <count>

Findings:
- <task-id or area>: <finding and required action>

Corrections made:
- <task-id>: <edit made>

Next owner:
- Planner | Development Loop | Human
```

`BLOCKED` is returned when required inputs are missing (for example, the approved specification path was not provided).

When `Result` is `ESCALATE`, append an Escalation Request block after the fields above:

```text
Problem: [why the plan cannot be validated — spec contradiction, irresolvable circular dependency, unresolved architecture decision]
Attempted: [checks already run and any corrections attempted in-place]
Failed because: [why the problem requires changing the approved specification]
Question: [specific decision or guidance needed from the Human]
```

Then produce a Phase 2 Human Escalation Report using the template defined in the `escalation-review` skill. The Planner (caller of Gate 2) forwards the report to the human alongside the preflight verdict.

## Quality Criteria

- Every planned task in the plan was checked.
- Dependencies are complete and refer to real tasks.
- File conflict risks are resolved by dependency order or Planner correction.
- Existing ADRs were consulted before approval.
- All tasks are atomic, verifiable, and ready for implementation.
- Human escalation is used only when the approved specification or unresolved architecture decision must change.

## Common Pitfalls

- Treating Gate 2 as a second spec approval.
- Passing a plan with hidden file conflicts.
- Fixing decomposition problems by silently rewriting task intent.
- Creating ADRs for routine implementation choices.
- Surfacing task-plan corrections to the human when the approved spec does not need to change.
