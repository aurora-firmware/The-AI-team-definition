---
name: dev-loop
description: Fully autonomous implementation loop. Picks pending tasks one at a time, drives each through Implementer → Reviewer cycles until the reviewer passes, commits, then moves to the next task. Stops only when the queue is empty, a task is blocked, or escalation is required.
argument-hint: "[task-id | task-branch] — optional single task to process (e.g., T-012 or task/T-012-my-feature). If omitted, processes the full pending queue."
allowed-tools: Read, Glob, Grep, Bash, Agent, Skill(integrate)
disable-model-invocation: true
---

# Dev Loop

Autonomous orchestrator that processes the pending task queue without human intervention.
Stops only at hard gates: empty queue, blocked task, or escalation.

## Inputs

Optional: a single task ID or branch name as `$ARGUMENTS` (e.g., `T-012` or `task/T-012-my-feature`).
- If provided, the loop processes only that task — it does not continue to the next task after completion or failure.
- If omitted, the loop processes the full pending queue until empty, blocked, or escalated.

The orchestrator reads state directly from the filesystem:
- `project/tasks/pending/` — work queue
- `project/tasks/in-progress/` — active task slot
- `project/tasks/blocked/` — escalation output

## Procedure

### Step 1: Check the Queue

If `$ARGUMENTS` is non-empty:
- Parse it as a task ID (e.g., `T-012`) or branch name (e.g., `task/T-012-my-feature`). Extract the task ID either way.
- Locate the matching file: `project/tasks/pending/<task-id>-*.md`.
- If not found in `pending/`, stop with: "Task <task-id> not found in project/tasks/pending/. Check the task ID and its current status."
- Use this single task as the queue. After it completes (success, blocked, or escalated), stop — do not continue to other tasks.

If `$ARGUMENTS` is empty, list all files in `project/tasks/pending/`.
If the queue is empty, stop and report: "Queue is empty. All pending tasks have been processed."

### Step 2: Pick the Next Task

Select the highest-priority task whose dependencies are all satisfied:
1. **Priority order:** critical → high → medium → low (read from task frontmatter `priority` field)
2. **Dependency check:** all tasks listed in `dependencies` must exist in `project/tasks/completed/`
3. **Tiebreak:** oldest `created` date first

If no task has all dependencies satisfied, stop and report which tasks are waiting and what they are waiting for.

### Step 3: Claim the Task

1. Move the selected task file from `project/tasks/pending/` to `project/tasks/in-progress/`
2. Create and check out the task branch: `git checkout -b task/T-NNN-short-description` (derive from task filename)
3. Commit the task move on `dev` branch first:
   - Switch to `dev`, commit: `chore(tasks): move T-NNN to in-progress`
   - Switch back to the task branch to continue

### Step 4: Implementation Cycle

**Spawn the Implementer agent** with this prompt:

> "Pick up the task at `project/tasks/in-progress/<task-file>` and implement it using the tdd skill.
> You are on branch `task/T-NNN-...`. Commit after each red→green→refactor cycle.
> Append a Work Log entry at session end. The entry's heading is `### Session N — YYYY-MM-DD`; the body is free prose covering what was done, what was tried and rejected, and what remains. The final entry serves as the handoff to the reviewer."

Wait for the implementer to complete before continuing.

### Step 5: Review Cycle

**Spawn the Reviewer agent** with this prompt:

> "Review the task at `project/tasks/in-progress/<task-file>` using the code-review skill.
> The implementer has completed their work on branch `task/T-NNN-...`.
> Append your verdict to the task file's Review section under `### Review Verdict — YYYY-MM-DD`.
> Verdict must be one of: PASS, FAIL, or ESCALATE."

Wait for the reviewer to complete before continuing.

### Step 6: Read the Verdict

Read the task file and find the most recent `### Review Verdict` entry.
Extract the verdict: **PASS**, **FAIL**, or **ESCALATE**.

#### On PASS

1. Invoke the `integrate` skill to merge the reviewed branch into `dev`:
   > `/integrate task/T-NNN-... dev`

   The integrate skill handles test verification, the merge, regression checks, task file promotion to `completed/`, and branch deletion.

2. **If integrate succeeds** — the branch is merged and deleted, the task is in `completed/`. Go back to **Step 1** to pick the next task.

3. **If integrate fails** — stop the loop entirely and report:
   - The failure reason (pre-merge test failure, unmet acceptance criteria, or post-merge regression).
   - Which bug IDs were filed (if regressions were found).
   - That the feature branch was NOT deleted and `dev` was left clean (integrate reverts on regression).
   - Next step for the human: resolve the filed bugs or unblock the task before re-running the loop.

#### On FAIL

Increment the review cycle counter.

- If **cycle < 3**: go back to **Step 4** (implementer fixes the issues noted in the Review Verdict)
- If **cycle = 3**: treat as ESCALATE (max review cycles exceeded)

#### On ESCALATE

1. Move the task file from `project/tasks/in-progress/` to `project/tasks/blocked/`
2. Switch to `dev` and commit: `chore(tasks): move T-NNN to blocked`
3. Stop the loop entirely.
4. Report the escalation clearly:
   - Which task is blocked
   - The last reviewer verdict and reason
   - What the human should do next (revise spec, modify task, provide guidance)

### Step 7: Loop Complete

When the queue is fully drained (Step 1 finds no pending tasks), report a summary:
- Tasks completed and merged this run (list with task IDs and merge commits)
- Tasks that were already completed before this run (skip)
- Any blocked tasks
- Any integration failures that stopped the loop mid-run

## Cycle Counter Reset

The review cycle counter resets to 0 each time a new task is picked up in Step 2.
It is local to each task — one task failing twice does not affect the counter for the next task.

## Commit Conventions

All orchestrator commits follow the project's git conventions from `ai-process/guidelines/git-conventions.md`:

| What | Branch | Message |
|---|---|---|
| Task moved to in-progress | `dev` | `chore(tasks): move T-NNN to in-progress` |
| Task moved to blocked | `dev` | `chore(tasks): move T-NNN to blocked` |

The `move T-NNN to completed` commit and merge commit are produced by the `integrate` skill, not by the dev-loop orchestrator.

Implementation commits are made by the implementer on the task branch — the orchestrator does not touch `src/` or `tests/`.

## Hard Stops (Do Not Continue)

- A task moves to `blocked/` — stop the loop, notify the human
- Integration fails for any reason (pre-merge test failure, unmet criteria, post-merge regression) — stop the loop, report the failure and any filed bug IDs
- A git operation fails (branch already exists, merge conflict on `dev`, etc.) — stop and report the git error before attempting anything else
- `project/tasks/in-progress/` already contains a task when the loop starts — stop and ask the human whether to resume that task or treat it as abandoned

## What This Skill Does NOT Do

- Does not touch `main` — human-only branch
- Does not modify specifications or decisions
- Does not fix integration failures — regressions are filed as bugs and the loop stops; fixing is the implementer's job on a subsequent cycle
