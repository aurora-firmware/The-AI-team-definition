# Write Plan

**Ownership boundary:** spec-breakdown owns plan coverage (the full set of tasks covers the entire spec), dependency ordering between tasks, and task boundary decisions (splitting or merging units of work).
Per-task shape rules are owned by the `new-task` skill.
Gate 2 technical readiness is owned by the `spec-breakdown-review` skill.

## Input Requirements

- **Approved specification** — the spec that passed Gate 1 (Spec Approval).
- **Project structure** — the existing codebase layout to determine file paths.
- **Existing tasks** — current tasks in `project/tasks/` to avoid conflicts or duplication.

## Procedure

### Step 0: Check Out the Planning Branch
The breakdown runs on the planning branch of the spec or change-request it decomposes (`plan/<id>-…`), never on `dev-agent`.
If that branch exists, run the before-point Workspace Hygiene check from the `git-conventions` skill and check it out.
If it does not exist — the approved spec is already on `dev-agent` — open one as described in **Opening a Planning Branch** in the `git-conventions` skill.

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
- **Acceptance criteria**: Author every criterion using one of the five EARS patterns documented in the task template (`cli/src/ai_team/templates/task.md`) (Ubiquitous, Event-driven, Unwanted-behaviour, State-driven, Optional).
- **Dependencies**: List of task IDs that must complete first.
- **Files to touch**: Exact file paths that will be created or modified.
- **Verification command**: Shell command that proves the task is done. If the task changes a shared or public interface (an API, schema, shared library function, or contract consumed by code outside the task's own module), `## Verification` must include the project's documented baseline/full-suite command in addition to any module-scoped command — a module-scoped command alone is not sufficient for such tasks.

During task writing, consider documentation updates as implementation work derived from the approved spec, not as a prerequisite before creating tasks.
If the spec changes user-facing behavior, commands, templates, guides, or workflow expectations, add the required documentation updates as tasks or acceptance criteria in this breakdown.
Also consider test updates and verification changes as implementation work derived from the approved spec.
If documentation or test updates are not needed, omit them without placeholder tasks.

### Step 4: Validate the Plan
Verify completeness: does the full set of tasks cover the entire specification?
Verify isolation: do any two tasks modify the same file? If yes, add a dependency between them.
Verify atomicity: can each task be completed in a single agent pass? If a task feels too large, split it.

### Step 5: Place Tasks
Save all task files to `project/tasks/pending/` and commit them on the planning branch: `docs(tasks): add task plan for <spec-or-cr-id>`.

### Step 6: Architect Preflight
**Spawn the Architect subagent** with this prompt:

> "Review the task plan just placed in `project/tasks/pending/` for the spec at `project/specs/<spec-file>`.
> Use the spec-breakdown-review skill.
> Validate dependency correctness, file conflict risk, architectural consistency with `project/decisions/`, atomicity, and implementation readiness.
> If all is sound, return `Result: PASS` and state that the plan is ready for /dev-loop.
> If issues are found, return `Result: FAIL` with exact Planner corrections, or `Result: ESCALATE` only when a problem requires changing the approved specification.
> Populate every field of the Output Format block, including `Obstacles Encountered`."

Wait for the Architect to complete.
If the Architect requests Planner revisions, address them, commit them on the planning branch, and re-trigger the preflight.
If the Architect escalates because the approved specification must change, stop and return the escalation to the human using the Phase 2 human report template defined in the `escalation-review` skill.

### Step 7: Merge the Planning Branch
Only after the Architect returns `PASS`:
1. Run the before-point Workspace Hygiene check, then `git checkout dev-agent`.
2. Run `git merge --no-ff plan/<id>-<slug> -m "chore(plan): merge <id> <short-description>"`.
   If the merge conflicts, abort it with `git merge --abort` and stop: report the conflicting planning files to the human. Do not resolve planning conflicts automatically.
3. Run the after-point Workspace Hygiene check.
4. Delete the planning branch with `git branch -d plan/<id>-<slug>`. If `-d` refuses, stop and report — never force deletion.

Until this merge, the tasks are invisible to `/dev-loop`, and `dev-agent` carries none of the spec or change-request changes.

## Output Format

- A set of validated task files in `project/tasks/pending/` on `dev-agent`, approved by the Architect preflight and merged from the planning branch together with the spec or change-request they implement.
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
