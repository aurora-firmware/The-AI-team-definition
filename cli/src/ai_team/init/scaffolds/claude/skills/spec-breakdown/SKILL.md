---
name: spec-breakdown
description: Decompose an approved specification into atomic, independent tasks. Use when a spec needs to be broken into executable work units.
allowed-tools: Read, Grep, Glob, Write, Agent, Skill(new-task)
effort: high
---

# Write Plan

## Input Requirements

- **Approved specification** — the spec that passed Gate 1 (Spec Approval).
- **Project structure** — the existing codebase layout to determine file paths.
- **Existing tasks** — current tasks in `project/tasks/` to avoid conflicts or duplication.

## Procedure

### Step 1: Identify Components
Read the specification and list every distinct unit of work.
A unit of work is something that produces a single testable outcome.

### Step 2: Define Dependencies
For each unit, determine what must exist before it can start.
Draw a dependency graph.
Maximize independence — units that touch different files should not depend on each other.

### Step 3: Write Task Files
For each unit, invoke the `new-task` skill to create the task file. Provide the full required input set in the invocation text:
- `title`: the task title
- `description`: the task description
- `priority`: the task priority
- `assigned-role`: the intended owner, or `unassigned`

The `new-task` skill handles template loading, ID assignment, filename, and frontmatter scaffolding. Because all required fields are provided here, it should not ask follow-up questions.

Then fill in the task body so it satisfies:
- **Title**: Clear, descriptive, starts with a verb (Implement, Add, Create, Fix).
- **Description**: Enough context to start without asking questions.
- **Acceptance criteria**: Author every criterion using one of the five EARS patterns documented in the `new-task` skill (Ubiquitous, Event-driven, Unwanted-behaviour, State-driven, Optional).
- **Dependencies**: List of task IDs that must complete first.
- **Files to touch**: Exact file paths that will be created or modified.
- **Verification command**: Shell command that proves the task is done.

### Step 4: Validate the Plan
Verify completeness: does the full set of tasks cover the entire specification?
Verify isolation: do any two tasks modify the same file? If yes, add a dependency between them.
Verify atomicity: can each task be completed in a single agent pass? If a task feels too large, split it.

### Step 5: Place Tasks
Save all task files to `project/tasks/pending/`.

### Step 6: Architect Preflight
**Spawn the Architect subagent** with this prompt:

> "Review the task plan just placed in `project/tasks/pending/` for the spec at `project/specs/<spec-file>`.
> Use the spec-breakdown-review skill.
> Validate dependency correctness, file conflict risk, architectural consistency with `project/decisions/`, atomicity, and implementation readiness.
> If all is sound, return `Result: PASS` and state that the plan is ready for /dev-loop.
> If issues are found, return `Result: FAIL` with exact Planner corrections, or `Result: ESCALATE` only when a problem requires changing the approved specification.
> Populate every field of the Output Format block, including `Obstacles Encountered`."

Wait for the Architect to complete.
If the Architect requests Planner revisions, address them and re-trigger the preflight.
If the Architect escalates because the approved specification must change, stop and return the escalation to the human using the Phase 2 human report template defined in the `escalation-review` skill.

## Output Format

- A set of validated task files in `project/tasks/pending/`, approved by the Architect preflight.
- The plan is ready for the human to invoke `/dev-loop` — no further human review of the task plan is required.

## Quality Criteria

- Every task is **atomic** — one clear outcome.
- Every task is **one-shottable** — completable in a single agent session without running out of context. Rules of thumb: touches at most 3–4 files, has at most 5 acceptance criteria, and the description fits in ~20 lines. If a task exceeds any of these, split it.
- Every task is **verifiable** — has a test or command that proves it works.
- Every task is **self-contained** — the description provides enough context to start.
- Every AC uses one of the five EARS patterns.
- No two tasks modify the same file without an explicit dependency between them.
- The full set of tasks covers 100% of the specification.

## Common Pitfalls

- **Tasks too large** — if a task description is longer than ~20 lines, it probably needs splitting.
- **Missing dependencies** — trace the data flow: if Task B reads a file that Task A creates, Task B depends on Task A.
- **Criteria that do not match an EARS pattern** — if a criterion resists EARS, the task is probably not atomic.
- **Forgetting verification commands** — every task must have a way to prove it is done. If you cannot write a verification command, the acceptance criteria are not specific enough.
- **File conflicts** — two tasks creating the same file will cause merge conflicts. Restructure so one task creates the file and the other modifies it (with a dependency).
