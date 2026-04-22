---
name: integrate
description: Integrate a feature branch into a destination branch. Verifies changes match the task spec, runs tests on the feature branch, merges, re-runs tests for regressions, files bugs on failure, and deletes the branch on success.
argument-hint: "<branch-or-task-id> [destination-branch]"
---

# Integrate

Merge a reviewed feature branch into a destination branch after verifying spec compliance and test health.

## Inputs

Provided as `$ARGUMENTS`:
- **Required** — feature branch name (e.g., `task/T-012-settings-api`) **or** task ID (e.g., `T-012`). If a task ID is given, derive the branch by scanning `git branch` for a branch containing that ID.
- **Optional** — destination branch (default: `dev-agent`). If provided as a second argument, use it; otherwise use `dev-agent`.

## Procedure

### Step 1: Resolve Inputs

1. Parse `$ARGUMENTS`:
   - First token → feature branch or task ID.
   - Second token (if present) → destination branch; otherwise `destination = dev-agent`.
2. If the input looks like a task ID (`T-NNN` pattern), run `git branch | grep <task-id>` to find the full branch name. If zero matches are found, stop with: "Branch for <task-id> not found. Check that the branch exists locally."
3. Confirm the feature branch exists: `git branch | grep <feature-branch>`. If not found, stop with the same message.
4. Confirm the destination branch exists: `git branch | grep <destination>`. If not found, stop with: "Destination branch '<destination>' not found."

### Step 2: Find the Task File

1. Extract the task ID from the branch name (e.g., `task/T-012-settings-api` → `T-012`).
2. Search for the task file across all task directories:
   ```
   find project/tasks/ -name "<task-id>-*.md"
   ```
3. If no task file is found, continue without spec verification but note the absence in the final report.
4. If found, read the task file completely — focus on the **Description**, **Acceptance Criteria**, and the **Work Log** section.
5. Preserve the Work Log as-is on merge. Do not strip it, rewrite it, or summarize it.

### Step 3: Verify Branch Contains Expected Changes

1. Check out the feature branch: `git checkout <feature-branch>`.
2. Get the diff against the destination: `git diff <destination>...<feature-branch> --stat`
3. Get the full diff for inspection: `git diff <destination>...<feature-branch>`
4. Compare the changed files and logic against the task's acceptance criteria:
   - Each acceptance criterion must be traceable to at least one changed file.
   - No acceptance criterion should be entirely absent from the diff.
5. If the diff is empty (branch is already merged or contains no changes vs destination), stop with: "Feature branch '<feature-branch>' has no changes relative to '<destination>'. Nothing to integrate."
6. If acceptance criteria are present but the diff does not satisfy them, stop with a gap report listing which criteria appear unaddressed. Do not proceed — return the branch to the Developer.

### Step 4: Run Tests on the Feature Branch

While still on the feature branch, run the full test suite:

```bash
npm test
```

Capture stdout and stderr. Evaluate the result:

- **All tests pass** → proceed to Step 5.
- **Tests fail** → stop integration. Report:
  - Which tests failed and what the error output says.
  - This is a pre-merge failure — the branch should not be merged in this state.
  - The task file stays in `project/tasks/in-progress/` and the feature branch stays open.
  - Instruct the Developer to fix the failing tests on the same branch and re-submit for integration.

### Step 5: Merge the Feature Branch into Destination

1. Switch to the destination branch: `git checkout <destination>`.
2. Merge with a descriptive commit message (no fast-forward):
   ```bash
   git merge --no-ff <feature-branch> -m "chore(tasks): merge <task-id> <short-description>"
   ```
   - Derive `<short-description>` from the task file title or the branch name slug.
3. If the merge produces conflicts:
   - Do NOT force-resolve automatically.
   - Invoke the `conflict-resolution` skill with the conflict context.
   - If the conflict-resolution skill cannot resolve a semantic conflict, stop and escalate to the architect before proceeding.

### Step 6: Run Tests on the Destination Branch (Regression Check)

After the merge, on the destination branch, run the full test suite again:

```bash
npm test
```

Evaluate the result:

#### All Tests Pass → Step 7 (Success Path)

#### Tests Fail → Regression Path

1. Compare the failing tests against the pre-merge results from Step 4.
2. For each regression (a test that passed in Step 4 but fails now):
   - Determine which file(s) and logic are responsible.
   - Invoke the `new-bug` skill to file a bug report for each regression:
     > `/new-bug <short description of the regression>`
     - Set severity based on impact: failing API tests → `high`; failing UI unit tests → `medium`; other → `low`.
     - In the bug's Summary section, include: the failing test name, the error message, and the merge commit that introduced the regression.
3. After filing all regression bugs, **revert the merge commit**:
   ```bash
   git revert -m 1 HEAD --no-edit
   ```
   Commit message: `chore(tasks): revert merge of <feature-branch> — regression in <test-names>`
4. Switch back to the feature branch: `git checkout <feature-branch>`.
5. Stop and report:
   - Which regressions were found.
   - Which bug IDs were created.
   - That the merge was reverted and the feature branch was not deleted.
   - Next step: the bugs must be resolved before re-attempting integration.

### Step 7: Finalize (Success Path Only)

Reached only when both Step 4 and Step 6 tests pass.

1. **Update the task file** (if found in Step 2):
   - Move the task file from `project/tasks/in-progress/` to `project/tasks/completed/`.
   - Update `status` in the frontmatter to `completed`.
   - Stage and commit this change as a separate commit on the destination branch:
     `chore(tasks): move <task-id> to completed`
   - This is always a distinct commit after the merge commit — the merge commit covers source changes only.

2. **Delete the feature branch** (safe delete only):
   ```bash
   git branch -d <feature-branch>
   ```
   If `-d` refuses (branch not considered merged by ancestry due to non-FF merge strategy or rebase history), confirm from Step 5 that the merge commit exists in the destination's log, then use:
   ```bash
   git branch -D <feature-branch>
   ```
   Document the forced deletion in the report.

3. **Report success**:
   - Feature branch merged and deleted.
   - Task ID and title.
   - Test counts: N passed before merge, N passed after merge.
   - Destination branch is clean.

## Hard Stops (Do Not Continue)

| Condition | Action |
|---|---|
| Feature branch not found | Stop, report, ask the human to verify the branch name |
| Destination branch not found | Stop, report |
| Diff is empty | Stop — nothing to do |
| Acceptance criteria not met by diff | Stop — return to Developer |
| Pre-merge tests fail (Step 4) | Stop — task stays `in-progress/`, branch stays open, return to Developer |
| Merge conflict that conflict-resolution cannot solve | Stop — escalate to architect |
| Regressions found post-merge (Step 6) | File bugs, revert merge, stop |

## Commit Conventions

All integrator commits follow `ai-process/guidelines/git-conventions.md`:

| What | Branch | Message pattern |
|---|---|---|
| Merge feature branch | `<destination>` | `chore(tasks): merge T-NNN short-description` |
| Move task to completed | `<destination>` | `chore(tasks): move T-NNN to completed` |
| Revert on regression | `<destination>` | `chore(tasks): revert merge of <branch> — regression in <tests>` |

## What This Skill Does NOT Do

- Does not implement fixes — regressions are filed as bugs, not fixed in place.
- Does not touch `main` — human-only branch.
- Does not modify specifications or ADRs.
- Does not skip tests or bypass hooks (`--no-verify` is forbidden).
- Does not merge multiple branches in one invocation — call the skill once per branch.
