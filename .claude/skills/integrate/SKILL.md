---
name: integrate
description: Integrate a task or bug branch into a destination branch. Verifies expected changes, runs tests on the source branch, merges, re-runs tests for regressions, files bugs on failure, and deletes the branch on success.
argument-hint: "<branch-or-task-id> [destination-branch]"
---

# Integrate

Merge a reviewed task or bug branch into a destination branch after verifying expected behavior and test health.

## Inputs

Provided as `$ARGUMENTS`:
- **Required** — branch name (e.g., `task/T-012-settings-api`, `bug/B-003-login-crash`) **or** task ID (e.g., `T-012`). If a task ID is given, derive the branch by scanning `git branch` for a branch containing that ID.
- **Optional** — destination branch (default: `dev-agent`). If provided as a second argument, use it; otherwise use `dev-agent`.

## Procedure

### Step 1: Resolve Inputs

1. Parse `$ARGUMENTS`:
   - First token → branch or task ID.
   - Second token (if present) → destination branch; otherwise `destination = dev-agent`.
2. If the input looks like a task ID (`T-NNN` pattern), run `git branch | grep <task-id>` to find the full branch name and set it as `source-branch`. If zero matches are found, stop with: "Branch for <task-id> not found. Check that the branch exists locally."
   If the input is already a branch name, set it as `source-branch`.
3. Confirm the source branch exists: `git branch | grep <source-branch>`. If not found, stop with the same message.
4. Confirm the destination branch exists: `git branch | grep <destination>`. If not found, stop with: "Destination branch '<destination>' not found."

### Step 2: Find the Work Item File

1. Extract the work item ID from the branch name:
   - `task/T-012-settings-api` → `T-012`
   - `bug/B-003-login-crash` → `B-003`
2. Search for the matching task or bug file:
   ```
   find project/tasks/ -name "<task-id>-*.md"
   find project/bugs/ -name "<bug-id>-*.md"
   ```
3. If no work item file is found, continue without work-item verification but note the absence in the final report.
4. If a task file is found, read it completely — focus on the **Description**, **Acceptance Criteria**, and the **Work Log** section.
5. If a bug file is found, read it completely — focus on the **Summary**, **Diagnosis Log**, **Fix Verification**, and **Work Log** sections.
6. Preserve the Work Log and Diagnosis Log as-is on merge. Do not strip them, rewrite them, or summarize them.

### Step 3: Verify Branch Contains Expected Changes

1. Check out the source branch: `git checkout <source-branch>`.
2. Get the diff against the destination: `git diff <destination>...<source-branch> --stat`
3. Get the full diff for inspection: `git diff <destination>...<source-branch>`
4. For task branches, compare the changed files and logic against the task's acceptance criteria:
   - Each acceptance criterion must be traceable to at least one changed file.
   - No acceptance criterion should be entirely absent from the diff.
5. For bug branches, compare the changed files and logic against the bug's Diagnosis Log and Fix Verification:
   - The change should address the isolated fault or documented root-cause hypothesis.
   - A regression test should exist when practical, or the Work Log should explain why manual verification is used.
6. If the diff is empty (branch is already merged or contains no changes vs destination), stop with: "Branch '<source-branch>' has no changes relative to '<destination>'. Nothing to integrate."
7. If expected behavior is present but the diff does not satisfy it, stop with a gap report listing what appears unaddressed. Do not proceed — return the branch to the Developer.

### Step 4: Run Tests on the Source Branch

While still on the source branch, run the full test suite:

```bash
npm test
```

Capture stdout and stderr. Evaluate the result:

- **All tests pass** → proceed to Step 5.
- **Tests fail** → stop integration. Report:
  - Which tests failed and what the error output says.
  - This is a pre-merge failure — the branch should not be merged in this state.
  - The work item file stays in `in-progress/` and the source branch stays open.
  - Instruct the Developer to fix the failing tests on the same branch and re-submit for integration.

### Step 5: Merge the Source Branch into Destination

1. Switch to the destination branch: `git checkout <destination>`.
2. Merge with a descriptive commit message (no fast-forward):
   ```bash
   git merge --no-ff <source-branch> -m "chore(<kind>): merge <work-item-id> <short-description>"
   ```
   - Use `tasks` for task branches and `bugs` for bug branches.
   - Derive `<short-description>` from the work item title or the branch name slug.
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
     - In the bug's Summary and Evidence sections, include: the failing test name, the error message, the merge commit that introduced the regression, the destination branch, and the source branch that was being integrated.
     - Set `source_branch` to the source branch being integrated so the bug-fix loop fixes the regression on that preserved branch before integration is retried.
3. After filing all regression bugs, **revert the merge commit**:
   ```bash
   git revert -m 1 HEAD --no-edit
   ```
   Commit message: `chore(<kind>): revert merge of <source-branch> — regression in <test-names>`
4. Switch back to the source branch: `git checkout <source-branch>`.
5. Stop and report:
   - Which regressions were found.
   - Which bug IDs were created.
   - That the merge was reverted and the source branch was not deleted.
   - Next step: the bugs must be resolved before re-attempting integration.

### Step 7: Finalize (Success Path Only)

Reached only when both Step 4 and Step 6 tests pass.

1. **Update the task file** (if found in Step 2):
   - Move the task file from `project/tasks/in-progress/` to `project/tasks/completed/`.
   - Update `status` in the frontmatter to `completed`.
   - Stage and commit this change as a separate commit on the destination branch:
     `chore(tasks): move <task-id> to completed`
   - This is always a distinct commit after the merge commit — the merge commit covers source changes only.

2. **Do not move bug files here.**
   Bug state changes are owned by the bug-fix loop after integrate reports success.

3. **Delete the source branch** (safe delete only):
   ```bash
   git branch -d <source-branch>
   ```
   If `-d` refuses (branch not considered merged by ancestry due to non-FF merge strategy or rebase history), confirm from Step 5 that the merge commit exists in the destination's log, then use:
   ```bash
   git branch -D <source-branch>
   ```
   Document the forced deletion in the report.

4. **Report success**:
   - Source branch merged and deleted.
   - Work item ID and title when available.
   - Test counts: N passed before merge, N passed after merge.
   - Destination branch is clean.

## Hard Stops (Do Not Continue)

| Condition | Action |
|---|---|
| Source branch not found | Stop, report, ask the human to verify the branch name |
| Destination branch not found | Stop, report |
| Diff is empty | Stop — nothing to do |
| Expected behavior not met by diff | Stop — return to Developer |
| Pre-merge tests fail (Step 4) | Stop — work item stays `in-progress/`, branch stays open, return to Developer |
| Merge conflict that conflict-resolution cannot solve | Stop — escalate to architect |
| Regressions found post-merge (Step 6) | File bugs, revert merge, stop |

## Commit Conventions

All integrator commits follow `ai-process/guidelines/git-conventions.md`:

| What | Branch | Message pattern |
|---|---|---|
| Merge task branch | `<destination>` | `chore(tasks): merge T-NNN short-description` |
| Merge bug branch | `<destination>` | `chore(bugs): merge B-NNN short-description` |
| Move task to completed | `<destination>` | `chore(tasks): move T-NNN to completed` |
| Revert on regression | `<destination>` | `chore(<kind>): revert merge of <branch> — regression in <tests>` |

## What This Skill Does NOT Do

- Does not implement fixes — regressions are filed as bugs, not fixed in place.
- Does not touch `main` — human-only branch.
- Does not modify specifications or ADRs.
- Does not skip tests or bypass hooks (`--no-verify` is forbidden).
- Does not merge multiple branches in one invocation — call the skill once per branch.
