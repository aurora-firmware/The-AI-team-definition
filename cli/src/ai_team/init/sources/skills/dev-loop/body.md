# Dev Loop

Autonomous orchestrator that processes the pending task queue without human intervention.
Stops only at hard gates: empty queue, blocked task, or escalation.

## Input Requirements

Optional: a single task ID or branch name as `$ARGUMENTS` (e.g., `T-012` or `task/T-012-my-feature`).
- If provided, the loop processes only that task — it does not continue to the next task after completion or failure.
- If omitted, the loop processes the full pending queue until empty, blocked, or escalated.

The orchestrator reads queue state using the {{ai-team-cli|`ai-team` CLI|`ai_team` tool}}:
- `{{ai-team list tasks --state pending}}` — pending work queue
- `project/tasks/in-progress/` — active task slot (filesystem)
- `project/tasks/blocked/` — escalation output (filesystem)

Task files are canonical lifecycle state on `dev-agent`.
Developer branches are for implementation artifacts only; the active loop records Developer Work Log handoffs in the canonical task file.

## Procedure

### Step 1: Check the Queue

If `$ARGUMENTS` is non-empty:
- Parse it as a task ID (e.g., `T-012`) or branch name (e.g., `task/T-012-my-feature`). Extract the task ID either way.
- Locate the matching file: `project/tasks/pending/<task-id>-*.md`.
- If not found in `pending/`, stop with: "Task <task-id> not found in project/tasks/pending/. Check the task ID and its current status."
- Use this single task as the queue. After it completes (success, blocked, or escalated), stop — do not continue to other tasks.

If `$ARGUMENTS` is empty, discover pending tasks using: `{{ai-team list tasks --state pending}}`.
If the queue is empty, proceed directly to **Step 8: Loop Complete** so the canonical
Gate 5 status report is produced before the loop stops.

### Step 2: Baseline Test Guard

The baseline guard runs once at loop startup. It is NOT re-checked between tasks. Rationale: post-merge regressions are caught by the integrate skill's destination-branch test step; re-checking between tasks adds latency without adding coverage.

Discover and run the project's baseline test command from project-specific guidance before claiming any task. Start with root guidance (`CLAUDE.md`, `AGENTS.md`, or equivalent instructions provided in the session), then follow clear references to project-local docs such as `project/docs/coding_guidelines.md`, README files, build configuration, or other documented test instructions. Prefer an explicitly documented test command over inferring one from dependencies or filenames.

Skip this step when looping back after a completed task (control returns to Step 1, which skips Step 2 on subsequent iterations).

#### Discovery Order

1. Read root project guidance files that exist, especially `CLAUDE.md` and `AGENTS.md`.
2. Read any project-local docs referenced by those files for test, build, or verification commands.
3. Read common project documentation or configuration files when guidance points there or no root guidance exists, such as README files, package/build manifests, or project-specific coding guidelines.
4. Identify the smallest documented automated command that verifies the project starts green enough for task work.

#### Missing or Unavailable

If no automated baseline test command is documented, or the documentation explicitly says no automated tests exist, ask the human for one of these before claiming a task:

- The intended baseline test command to run.
- Explicit confirmation that no automated baseline test is available for this project.

Stop until the human responds. Report:
`BLOCKED: no automated baseline test command is documented. Provide the command to run, or confirm that this project has no automated baseline test.`

If the human confirms that no automated baseline test is available, record that confirmation in the loop summary and continue to Step 3 without running a baseline command.

#### Ambiguous

If multiple plausible automated baseline commands are documented and no source clearly identifies which one is the baseline, ask the human which command to use before claiming a task.

Stop until the human responds. Report:
`BLOCKED: multiple plausible baseline test commands are documented. Confirm which command the loop should run before claiming tasks.`

#### Runnable

If a clear baseline test command is documented, run it.

- If the baseline test command passes, continue to Step 3.
- If the baseline test command fails, stop immediately and report: `BLOCKED: baseline test command failed before any task was claimed. Failing command: <command>. Output summary: <last 20 lines of combined stdout/stderr>.`

### Step 3: Pick the Next Task

Select the highest-priority task whose dependencies are all satisfied:
1. **Priority order:** critical → high → medium → low (read from task frontmatter `priority` field)
2. **Dependency check:** all tasks listed in `dependencies` must exist in `project/tasks/completed/`
3. **Tiebreak:** oldest `created` date first

If no task has all dependencies satisfied, stop and report which tasks are waiting and what they are waiting for.

### Step 4: Claim the Task

1. Switch to `dev-agent`.
2. Move the selected task file from `project/tasks/pending/` to `project/tasks/in-progress/`.
3. Commit the task move: `chore(tasks): move T-NNN to in-progress`.
4. Create and check out the task branch from `dev-agent`: `git checkout -b task/T-NNN-short-description` (derive from task filename).

### Step 5: Implementation Cycle

Before spawning the Developer, read the latest canonical task file from `dev-agent`.
Check out the task branch `task/T-NNN-...`.

**Spawn the Developer subagent** with this prompt:

> "Pick up the task from the canonical task file `project/tasks/in-progress/<task-file>` on `dev-agent` and implement it using the tdd skill.
> You are on branch `task/T-NNN-...`. Commit after each red→green→refactor cycle.
> Do not edit the task lifecycle file on the task branch.
> Return a Work Log handoff entry at session end. The entry's heading is `### Session N — YYYY-MM-DD`; the body is free prose covering what was done, what was tried and rejected, and what remains. The loop will append and commit it on `dev-agent`.
> Populate every field of the Output Format block, including `Obstacles Encountered`."

Wait for the Developer to complete before continuing.
If the Developer returns `ESCALATE`, go directly to **On ESCALATE**.
If the Developer does not return a Work Log handoff entry, stop with `BLOCKED` and report the missing handoff.

Record the Work Log handoff:
1. Switch to `dev-agent`.
2. Append the Developer's Work Log handoff under `## Work Log` in `project/tasks/in-progress/<task-file>`.
3. Commit the lifecycle update: `chore(tasks): record T-NNN work log`.

### Step 6: Review Cycle

**Spawn the Reviewer subagent** with this prompt:

> "Review the task using the canonical task file `project/tasks/in-progress/<task-file>` on `dev-agent` and the code-review skill.
> The Developer has completed their work on branch `task/T-NNN-...`.
> Append your verdict to the canonical task file's Review section under `### Review Verdict — YYYY-MM-DD` and commit it on `dev-agent`.
> Verdict must be one of: PASS, FAIL, or ESCALATE. On ESCALATE, include the four-field escalation request block defined in the code-review skill.
> Populate every field of the Output Format block, including `Obstacles Encountered`."

Wait for the reviewer to complete before continuing.

### Step 7: Read the Verdict

Switch to `dev-agent`, then read the canonical task file and find the most recent `### Review Verdict` entry.
Extract the verdict: **PASS**, **FAIL**, or **ESCALATE**.

#### On PASS

Before invoking integration, confirm that both the committed Developer Work Log and the
committed Review Verdict exist on `dev-agent` (they were recorded in Steps 5 and 6).
The `integrate` skill verifies that the latest committed verdict is PASS — ensure this
state is in place before calling integrate.

1. Invoke the `integrate` skill to merge the reviewed branch into `dev-agent`:
   > `/integrate task/T-NNN-... dev-agent`

   The integrate skill handles test verification, the merge, regression checks, task file promotion to `completed/`, and branch deletion.

2. **If integrate succeeds** — the branch is merged and deleted, the task is in `completed/`. Go back to **Step 1** to pick the next task.

3. **If integrate fails** — stop the loop entirely and report:
   - The failure reason (pre-merge test failure, unmet acceptance criteria, or post-merge regression).
   - Which bug IDs were filed (if regressions were found).
   - That the feature branch was NOT deleted and `dev-agent` was left clean (integrate reverts on regression).
   - Next step for the human: run `/bug-loop` to autonomously fix the filed regressions, then re-run `/dev-loop`.

#### On FAIL

Increment the review cycle counter.

- If **cycle < 3**: go back to **Step 5** (Developer fixes the issues noted in the Review Verdict)
- If **cycle = 3**: treat as ESCALATE (max review cycles exceeded)

#### On ESCALATE

Follow the two-phase escalation procedure below. Phase 1 is a single Architect consultation; Phase 2 is human escalation. The chain is linear — no second Architect round.

**Phase 1 — Architect Consultation:**
**Spawn the Architect subagent** with this prompt:

> "Use the escalation-review skill for task `project/tasks/in-progress/<task-file>`.
> Problem: <what the reviewer or loop found>
> Attempted: <what the Developer tried and how many review cycles occurred>
> Failed because: <why the task still cannot pass>
> Question: <specific guidance needed to continue within the approved specification>
> Populate every field of the Output Format block, including `Obstacles Encountered`."

If the Architect resolves the issue, go back to **Step 5** with the Architect's guidance.

**Phase 2 — Human Escalation:**
If the Architect cannot resolve the issue:
1. Move the task file from `project/tasks/in-progress/` to `project/tasks/blocked/`.
2. Switch to `dev-agent` and commit: `chore(tasks): escalate T-NNN — move to blocked`.
3. Stop the loop entirely.
4. Produce the report using the Phase 2 Human Escalation Report template defined in the `escalation-review` skill. Fill every section (Work item, Original request, Self-recovery attempts, Architect analysis, Why human input is required, Decision needed).

### Step 8: Loop Complete

When the queue is fully drained (Step 1 finds no pending tasks), invoke `Skill(status-report)` to
produce the canonical Gate 5 summary. The status-report skill runs `{{ai-team status}}`, scans project
state directories, and writes the full progress report — that output is the authoritative end-of-run
status.

After the status-report output, append the following loop-specific run details as supplemental context:
- Tasks completed and merged this run (list with task IDs and merge commits)
- Tasks that were already completed before this run (skip)
- Any blocked tasks
- Any integration failures that stopped the loop mid-run

## Cycle Counter Reset

The review cycle counter resets to 0 each time a new task is picked up in Step 3.
It is local to each task — one task failing twice does not affect the counter for the next task.

## Commit Conventions

All orchestrator commits follow the `git-conventions` skill. Canonical patterns for this orchestrator:

| What | Branch | Message |
|---|---|---|
| Task moved to in-progress | `dev-agent` | `chore(tasks): move T-NNN to in-progress` |
| Developer Work Log recorded | `dev-agent` | `chore(tasks): record T-NNN work log` |
| Task escalated and moved to blocked | `dev-agent` | `chore(tasks): escalate T-NNN — move to blocked` |

The `move T-NNN to completed` commit and merge commit are produced by the `integrate` skill, not by the dev-loop orchestrator.

Implementation commits are made by the Developer on the task branch.
Lifecycle state commits are made by the loop and Reviewer on `dev-agent`.
The orchestrator does not touch implementation or test files.

## Hard Stops (Do Not Continue)

- A task moves to `blocked/` — stop the loop, notify the human
- Integration fails for any reason (pre-merge test failure, unmet criteria, post-merge regression) — stop the loop, report the failure and any filed bug IDs
- A git operation fails (branch already exists, merge conflict on `dev-agent`, etc.) — stop and report the git error before attempting anything else
- `project/tasks/in-progress/` already contains a task on `dev-agent` when the loop starts — stop and ask the human whether to resume that task or treat it as abandoned

## What This Skill Does NOT Do

- Does not touch `main` — human-only branch
- Does not modify specifications or decisions
- Does not fix integration failures — regressions are filed as bugs and the loop stops; fixing is the Developer's job on a subsequent cycle
