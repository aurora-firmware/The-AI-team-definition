---
name: bug-loop
description: Fully autonomous bug-fix loop. Picks open bugs one at a time, creates a dedicated branch from the correct base, drives each through diagnosis-first Developer → Reviewer cycles until the reviewer passes, then moves to the next bug. Stops only when the queue is empty or a bug cannot be resolved after full escalation. Use this whenever there are open bugs to fix.
argument-hint: "[bug-id ...] — optional space-separated bug IDs (e.g., B-001 B-003). If omitted, processes all open bugs."
allowed-tools: Read, Glob, Grep, Bash, Agent, Skill(integrate)
disable-model-invocation: true
---

# Bug Loop

Autonomous orchestrator that processes the open bug queue without human intervention.
Each bug gets its own branch — bugs are never mixed on the same branch.
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
3. Switch to `dev-agent` and commit the bug move: `chore(bugs): move B-NNN to in-progress`
4. Determine the bug branch base and target:
   - If the bug frontmatter has a non-empty `source_branch`, use that branch as both the base and target.
   - Otherwise use `dev-agent` as both the base and target.
5. Create and check out the bug branch from the selected base: `git checkout -b bug/B-NNN-short-description`
   - Derive the branch name from the bug filename (e.g., `B-001-system-prompt-exposed` → `bug/B-001-system-prompt-exposed`)

### Step 4: Diagnosis + Implementation Cycle

**Spawn the Developer role** with this prompt:

> "Fix the bug described at `project/bugs/in-progress/<bug-file>`.
> You are on branch `bug/B-NNN-...`.
> Use the debug skill first.
> Before changing production code, reproduce or confirm the defect, gather relevant logs or command output, isolate the fault, and append a Diagnosis Log entry to the bug file.
> The Diagnosis Log entry must record reproduction status, evidence captured, isolated fault, root cause or fault hypothesis, and planned verification.
> After diagnosis, use the tdd skill where applicable: add or update a failing regression test when the defect can be tested automatically, verify it fails, implement the minimal fix, and verify it passes.
> Commit after each red→green→refactor cycle.
> Append a Work Log entry at session end. The entry's heading is `### Session N — YYYY-MM-DD`; the body is free prose covering what was done, what was tried and rejected, and what remains. The final entry serves as the handoff to the reviewer."

Wait for the Developer to complete before continuing.

### Step 5: Review Cycle

**Spawn the Reviewer agent** with this prompt:

> "Review the bug fix at `project/bugs/in-progress/<bug-file>` using the code-review skill.
> The Developer has completed their work on branch `bug/B-NNN-...`.
> Verify the Diagnosis Log records reproduction status, evidence captured, isolated fault, and root cause or fault hypothesis.
> Verify the fix addresses the isolated cause and passes the Fix Verification steps in the bug file.
> Verify a regression test exists when practical, or that the Work Log explains why only manual verification was possible.
> Append your verdict to the bug file under `### Review Verdict — YYYY-MM-DD`.
> Verdict must be one of: PASS, FAIL, or ESCALATE."

Wait for the reviewer to complete before continuing.

### Step 6: Read the Verdict

Read the bug file and find the most recent `### Review Verdict` entry.
Extract the verdict: **PASS**, **FAIL**, or **ESCALATE**.

#### On PASS

1. Invoke the `integrate` skill to merge the reviewed branch into the target branch chosen in Step 3:
   > `/integrate bug/B-NNN-... <target-branch>`

   The integrate skill handles test verification, the merge, regression checks, and branch deletion.
   It reads the bug file for diagnosis and fix-verification context, but bug state changes remain owned by bug-loop.

2. **If integrate succeeds** — on `dev-agent`, move the bug file from `project/bugs/in-progress/` to `project/bugs/resolved/`, update `status` to `resolved`, and commit:
   `chore(bugs): move B-NNN to resolved`
   Then go back to **Step 1** to pick the next bug.

3. **If integrate fails** — stop the loop entirely and report:
   - The failure reason (pre-merge test failure, unmet fix criteria, or post-merge regression).
   - Which bug IDs were filed (if regressions were found).
   - That the bug branch was NOT deleted, the target branch was left clean (integrate reverts on regression), and the bug file remains in `in-progress/`.
   - Next step for the human: resolve the filed regression bugs before re-running the loop.

#### On FAIL

Increment the review cycle counter.

- If **cycle < 3**: go back to **Step 4** (Developer fixes the issues noted in the Review Verdict)
- If **cycle = 3**: treat as ESCALATE (max review cycles exceeded)

#### On ESCALATE

Follow the two-phase escalation procedure from `ai-process/processes/escalation-procedure.md`:

**Phase 1 — Architect Consultation:**
Spawn the Architect agent with a structured request:
- Use the `escalation-consultation` skill.
- Problem: what the reviewer found.
- Attempted: what the Developer tried, including diagnosis attempts and review cycles.
- Failed because: why the bug still cannot pass.
- Question: specific guidance needed to continue within the bug report and approved specification.

If the Architect resolves the issue, go back to **Step 4** with the Architect's guidance.
If the Architect cannot resolve it, proceed to Phase 2.

**Phase 2 — Human Escalation:**
1. Leave the bug file in `project/bugs/in-progress/` — there is no `blocked/` state for bugs
2. Stop the loop entirely
3. Report to the human:
   - Which bug is stuck
   - Full chain: reviewer verdict → what the Developer tried → architect's advice and why it was insufficient
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
| Bug moved to in-progress | `dev-agent` | `chore(bugs): move B-NNN to in-progress` |
| Bug moved to resolved | `dev-agent` | `chore(bugs): move B-NNN to resolved` |
| Bug escalated | `dev-agent` | `chore(bugs): escalate B-NNN — needs human review` |

The merge commit is produced by the `integrate` skill. The `move B-NNN to resolved` commit is made by bug-loop on `dev-agent` only after integrate confirms a successful merge.

Implementation commits are made by the Developer on the bug branch — the orchestrator does not touch `src/` or `tests/`.

## Hard Stops (Do Not Continue)

- A bug reaches human escalation (Phase 2) — stop the loop, notify the human
- A git operation fails (branch already exists, conflict on `dev-agent`, etc.) — stop and report the git error before attempting anything else
- `project/bugs/in-progress/` already contains a bug when the loop starts — stop and ask the human whether to resume that bug or treat it as abandoned
- The Developer cannot reproduce the bug and cannot form an evidence-backed fault hypothesis — escalate instead of patching by guesswork

## What This Skill Does NOT Do

- Does not touch `main` — human-only branch
- Does not modify specifications or task files
- Does not fix integration failures — regressions are filed as bugs and the loop stops; fixing is the Developer's job on a subsequent cycle
