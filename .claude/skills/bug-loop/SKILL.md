---
name: bug-loop
description: Fully autonomous bug-fix loop. Picks open bugs one at a time, creates a dedicated branch from dev for each, drives each through Implementer → Reviewer cycles until the reviewer passes, then moves to the next bug. Stops only when the queue is empty or a bug cannot be resolved after full escalation. Use this whenever there are open bugs to fix.
argument-hint: "[bug-id ...] — optional space-separated bug IDs (e.g., B-001 B-003). If omitted, processes all open bugs."
allowed-tools: Read, Glob, Grep, Bash, Agent, Skill(integrate)
disable-model-invocation: true
---

# Bug Loop

Autonomous orchestrator that processes the open bug queue without human intervention.
Each bug gets its own branch off `dev` — bugs are never mixed on the same branch.
Stops only when the queue is empty or when a bug requires human resolution after full escalation.

## Inputs

Optional: one or more bug IDs as `$ARGUMENTS` (e.g., `B-001 B-003`).
- If bug IDs are provided, the loop processes only those bugs — skipping all others in the queue.
- If omitted, the loop processes all files in `project/bugs/open/`.

The orchestrator reads state directly from the filesystem:
- `project/bugs/open/` — work queue
- `project/bugs/in-progress/` — active bug slot
- `project/bugs/resolved/` — completed fixes

## Procedure

### Step 1: Check the Queue

If `$ARGUMENTS` is non-empty:
- Parse it as a space-separated list of bug IDs (e.g., `B-001 B-003`).
- For each ID, locate the matching file in `project/bugs/open/<id>-*.md`.
- If any ID has no matching file in `open/`, stop with: "Bug <id> not found in project/bugs/open/. Verify the ID and status."
- Use this filtered list as the queue for the entire run.

If `$ARGUMENTS` is empty, list all files in `project/bugs/open/` (ignore `.gitkeep`) as the queue.

If the queue is empty, stop and report: "Queue is empty. No open bugs to process."

### Step 2: Pick the Next Bug

Select the highest-severity unblocked bug:
1. **Severity order:** critical → high → medium → low (read from bug frontmatter `severity` field)
2. **Tiebreak:** oldest `created` date first

### Step 3: Claim the Bug

1. Move the selected bug file from `project/bugs/open/` to `project/bugs/in-progress/`
2. Update the `status` field in the bug frontmatter to `in-progress`
3. Switch to `dev` and commit the bug move: `chore(bugs): move B-NNN to in-progress`
4. Create and check out the bug branch **from `dev`**: `git checkout -b bug/B-NNN-short-description`
   - Derive the branch name from the bug filename (e.g., `B-001-system-prompt-exposed` → `bug/B-001-system-prompt-exposed`)

### Step 4: Implementation Cycle

**Spawn the Implementer agent** with this prompt:

> "Fix the bug described at `project/bugs/in-progress/<bug-file>`.
> You are on branch `bug/B-NNN-...`. Use the tdd skill where applicable.
> Commit after each red→green→refactor cycle.
> When done, append a handoff note to the bug file's Notes section (or add a `## Notes` section if absent) following the format in `ai-process/templates/handoff-note.md`."

Wait for the implementer to complete before continuing.

### Step 5: Review Cycle

**Spawn the Reviewer agent** with this prompt:

> "Review the bug fix at `project/bugs/in-progress/<bug-file>` using the code-review skill.
> The implementer has completed their work on branch `bug/B-NNN-...`.
> Verify the fix addresses the root cause and passes the Fix Verification steps in the bug file.
> Append your verdict to the bug file under `### Review Verdict — YYYY-MM-DD`.
> Verdict must be one of: PASS, FAIL, or ESCALATE."

Wait for the reviewer to complete before continuing.

### Step 6: Read the Verdict

Read the bug file and find the most recent `### Review Verdict` entry.
Extract the verdict: **PASS**, **FAIL**, or **ESCALATE**.

#### On PASS

1. Invoke the `integrate` skill to merge the reviewed branch into `dev`:
   > `/integrate bug/B-NNN-... dev`

   The integrate skill handles test verification, the merge, regression checks, and branch deletion.
   It will not find a task file (bug branches have no matching `project/tasks/` entry) — that is expected; integrate will note the absence and skip task file promotion.

2. **If integrate succeeds** — on `dev`, move the bug file from `project/bugs/in-progress/` to `project/bugs/resolved/`, update `status` to `resolved`, and commit:
   `chore(bugs): move B-NNN to resolved`
   Then go back to **Step 1** to pick the next bug.

3. **If integrate fails** — stop the loop entirely and report:
   - The failure reason (pre-merge test failure, unmet fix criteria, or post-merge regression).
   - Which bug IDs were filed (if regressions were found).
   - That the bug branch was NOT deleted, `dev` was left clean (integrate reverts on regression), and the bug file remains in `in-progress/`.
   - Next step for the human: resolve the filed regression bugs before re-running the loop.

#### On FAIL

Increment the review cycle counter.

- If **cycle < 3**: go back to **Step 4** (implementer fixes the issues noted in the Review Verdict)
- If **cycle = 3**: treat as ESCALATE (max review cycles exceeded)

#### On ESCALATE

Follow the two-phase escalation procedure from `ai-process/processes/escalation-procedure.md`:

**Phase 1 — Architect Consultation:**
Spawn the Architect agent with a structured request:
- Problem: what the reviewer found
- Attempted: what the implementer tried (and how many cycles)
- Failed because: why it did not work
- Question: specific guidance needed

If the architect resolves the issue, go back to **Step 4** with the architect's guidance.
If the architect cannot resolve it, proceed to Phase 2.

**Phase 2 — Human Escalation:**
1. Leave the bug file in `project/bugs/in-progress/` — there is no `blocked/` state for bugs
2. Stop the loop entirely
3. Report to the human:
   - Which bug is stuck
   - Full chain: reviewer verdict → what the implementer tried → architect's advice and why it was insufficient
   - What the human should do next (revise the bug description, provide guidance, or defer the fix)

### Step 7: Loop Complete

When the queue is fully drained (Step 1 finds no open bugs), report a summary:
- Bugs resolved and merged this run (list with bug IDs and merge commits)
- Any escalated bugs still in `in-progress/`
- Any integration failures that stopped the loop mid-run

## Cycle Counter Reset

The review cycle counter resets to 0 each time a new bug is picked up in Step 2.
It is local to each bug — one bug failing twice does not affect the counter for the next bug.

## Commit Conventions

All orchestrator commits follow the project's git conventions from `ai-process/guidelines/git-conventions.md`:

| What | Branch | Message |
|---|---|---|
| Bug moved to in-progress | `dev` | `chore(bugs): move B-NNN to in-progress` |
| Bug moved to resolved | `dev` | `chore(bugs): move B-NNN to resolved` |
| Bug escalated | `dev` | `chore(bugs): escalate B-NNN — needs human review` |

The merge commit is produced by the `integrate` skill. The `move B-NNN to resolved` commit is made by bug-loop on `dev` only after integrate confirms a successful merge.

Implementation commits are made by the implementer on the bug branch — the orchestrator does not touch `src/` or `tests/`.

## Hard Stops (Do Not Continue)

- A bug reaches human escalation (Phase 2) — stop the loop, notify the human
- A git operation fails (branch already exists, conflict on `dev`, etc.) — stop and report the git error before attempting anything else
- `project/bugs/in-progress/` already contains a bug when the loop starts — stop and ask the human whether to resume that bug or treat it as abandoned

## What This Skill Does NOT Do

- Does not touch `main` — human-only branch
- Does not modify specifications or task files
- Does not fix integration failures — regressions are filed as bugs and the loop stops; fixing is the implementer's job on a subsequent cycle
