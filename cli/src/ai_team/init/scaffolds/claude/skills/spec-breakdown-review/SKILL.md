---
name: spec-breakdown-review
description: Validate a pending task plan before development starts. Use when the Planner has decomposed an approved specification into tasks and Gate 2 must confirm dependency correctness, file conflict risk, ADR consistency, atomicity, and implementation readiness.
allowed-tools: Read, Grep, Glob, Write, Edit, Skill(new-adr)
effort: high
---

# Gate 2 Preflight

## Input Requirements

- **Approved specification** — the spec that passed Gate 1.
- **Pending task files** — task plan in `project/tasks/pending/`.
- **Decision records** — existing ADRs in `project/decisions/`.
- **Project structure** — current files needed to verify paths and conflict risk.

## Procedure

### Step 1: Read Planning Context

Read the approved specification and all task files for the plan under review.
Read existing decision records in `project/decisions/`.
Identify each task's dependencies, files to touch, acceptance criteria, and verification command.

### Step 2: Check Dependency Correctness

Verify that every declared dependency refers to a real task.
Check for missing dependencies where one task reads, modifies, or relies on files or behavior created by another task.
Flag circular dependencies.

### Step 3: Check File Conflict Risk

Identify tasks that create or modify the same file.
If overlapping edits are intentional, ensure a dependency orders them.
If no dependency exists, add the dependency directly when the correction is obvious; otherwise request Planner revision.

### Step 4: Check Architectural Consistency

Compare the task plan against existing ADRs and architecture docs.
If a task contradicts an existing decision or requires changing an approved specification, do not pass Gate 2.
Use `new-adr` only when the plan exposes a durable architecture-affecting decision within the approved spec.
When invoking `new-adr`, provide the full required input set:
- `title`: concise decision title derived from the architectural choice
- `context`: the approved spec path, affected task IDs, relevant ADRs, and why the decision is durable rather than an implementation detail
Escalate to human through the Planner when the approved spec must change.

### Step 5: Check Atomicity And Verification

Confirm each task is independently implementable and verifiable.
Flag tasks that exceed the one-shottable threshold:

- More than 3-4 files.
- More than 5 acceptance criteria.
- Description too large or ambiguous for one implementation session.
- No clear verification command.

### Step 6: Produce Verdict

If the plan passes, state that Gate 2 passes and the pending queue is ready for `/dev-loop`.

If the plan fails:

- For obvious missing dependencies or file-ordering issues, edit the affected task files directly.
- For decomposition or atomicity issues, return a correction request to the Planner with exact task IDs and required changes.
- For spec contradictions, escalate because an approved specification change is required.

## Output Format

Use this structure — matches the Architect agent's standard `Result:` vocabulary:

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

- Every pending task in the plan was checked.
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
