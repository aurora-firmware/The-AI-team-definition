# Integrate

Merge a reviewed task or bug branch into a destination branch after verifying expected behavior and test health.

## Input Requirements

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

### Step 2: Find the Canonical Work Item and Verification Command

Task and bug files are canonical lifecycle state on `dev-agent`.
Do not rely on task or bug file copies from the source branch or destination branch.

1. Switch to `dev-agent`.
2. Extract the work item ID from the branch name:
   - `task/T-012-settings-api` → `T-012`
   - `bug/B-003-login-crash` → `B-003`
3. Search for the matching canonical task or bug file:
   ```
   find project/tasks/ -name "<task-id>-*.md"
   find project/bugs/ -name "<bug-id>-*.md"
   ```
4. If no work item file is found, continue without work-item verification but note the absence in the final report.
5. If a task file is found, read it completely — focus on the **Description**, **Acceptance Criteria**, **Verification**, **Work Log**, and **Review** sections.
6. If a bug file is found, read it completely — focus on the **Summary**, **Diagnosis Log**, **Fix Verification**, **Work Log**, and **Review** sections.
7. Determine the source-branch verification command before checking out the source branch. Lookup order:
   - The work item's `## Verification` or `## Fix Verification` section, if it contains concrete automated command(s).
   - Target-project guidance such as the project `CLAUDE.md`, `project/docs/coding_guidelines.md`, README, build configuration, or human-provided instructions.
   - If no automated verification command can be determined, stop with `BLOCKED` and ask the human for the project verification command.
   This is the command Step 4 runs on the source branch. It is scoped to the work item and must not be assumed to also cover the destination branch.
8. Determine the destination-branch verification command — the check Step 6 runs after the merge to catch regressions outside the work item's own declared scope. Do not default this to the source-branch command from item 7; determine it separately:
   a. If the work item or project guidance explicitly defines a separate destination-branch or baseline check, use it.
   b. Otherwise, discover the project's documented baseline command using the discovery order owned by the `dev-loop` skill's Step 2 Baseline Test Guard. Read that skill's **Discovery Order** and apply it directly here — do not restate or re-derive a second copy of it.
   c. If the discovered baseline command differs from the source-branch command from item 7, Step 6 must run both.
   d. If no project baseline command is discoverable at all, Step 6 falls back to running only the source-branch command, but record that fallback here as an explicit coverage-gap flag to carry into Step 6's report. A missing baseline must never be silently treated as sufficient coverage — and must never by itself block integration; only a genuinely failing test blocks Step 6.

### Step 2b: Verify the Latest Committed Review Verdict on dev-agent is PASS

Before leaving `dev-agent`, confirm that the latest committed canonical Review Verdict for
this work item is PASS.

1. While still on `dev-agent`, read the `## Review` section of the work item file.
2. Find the most recent `### Review Verdict` entry.
3. Extract the verdict: PASS, FAIL, or ESCALATE.
4. If the committed verdict is not PASS (or no verdict entry exists), stop and report:
   - Work item ID and the verdict found (or "no verdict committed").
   - Do not merge — the branch must pass review before integration.
   - Instruct the active loop to ensure a committed PASS verdict exists on `dev-agent`
     before re-invoking integrate.

Proceed to Step 3 only when the committed verdict is PASS.

### Step 3: Verify Branch Contains Expected Changes

1. Check out the source branch: `git checkout <source-branch>`.
2. Get the diff against the destination: `git diff <destination>...<source-branch> --stat`
3. Get the full diff for inspection: `git diff <destination>...<source-branch>`
4. Confirm the source diff does not modify the canonical task or bug lifecycle file. If it does, stop and ask the active loop to move lifecycle log or verdict content to `dev-agent` before integration.
5. For task branches, compare the changed files and logic against the task's acceptance criteria:
   - Each acceptance criterion must be traceable to at least one changed file.
   - No acceptance criterion should be entirely absent from the diff.
6. For bug branches, compare the changed files and logic against the bug's Diagnosis Log and Fix Verification:
   - The change should address the isolated fault or documented root-cause hypothesis.
   - A regression test should exist when practical, or the Work Log should explain why manual verification is used.
7. If the diff is empty (branch is already merged or contains no changes vs destination), stop with: "Branch '<source-branch>' has no changes relative to '<destination>'. Nothing to integrate."
8. If expected behavior is present but the diff does not satisfy it, stop with a gap report listing what appears unaddressed. Do not proceed — return the branch to the Developer.

### Step 4: Run Tests on the Source Branch

While still on the source branch, run the discovered source-branch verification command set:

```text
<source verification command(s)>
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
   - Invoke the `merge-conflicts` skill with the conflict context.
   - If the merge-conflicts skill cannot resolve a semantic conflict, stop and escalate to the architect before proceeding.

### Step 6: Run Tests on the Destination Branch (Regression Check)

After the merge, on the destination branch, run the destination-branch verification command(s) determined in Step 2 item 8 — the project's documented baseline command, plus the source-branch command from item 7 when the two differ:

```text
<destination-branch verification command(s)>
```

If Step 2 recorded a coverage-gap flag (no project baseline command was discoverable), state that explicitly in the report for this step, for example: "post-merge check used the task-scoped command only; no project-wide baseline command was discoverable — coverage outside the task's declared scope was not verified." Do not report post-merge success as equivalent to Step 4's result without that qualification. The coverage gap is a reporting requirement, not a hard stop — do not block integration solely because no baseline is documented.

Evaluate the result:

#### All Tests Pass → Step 7 (Success Path)

#### Tests Fail → Regression Path

1. Determine the post-merge failing test set: the union of failing tests across every destination-branch command Step 6 ran (the source-branch command from item 7 and, when it also ran, the discovered baseline command from item 8). This union — not either command's output alone — is the single result set compared against Step 4.
2. For every test in that set, file a bug through the same loop below. Whether the test ran in Step 4 must never decide whether a bug gets filed — it only changes the classification recorded as evidence:
   - Classify each failing test for evidence purposes only:
     - **True regression** — the test passed in Step 4's source-branch run and fails now.
     - **Previously-uncovered failure** — the test was never executed in Step 4 because it is covered only by the newly-discovered baseline command from item 8, and it fails now.
   - Determine which file(s) and logic are responsible.
   - Switch to `dev-agent`.
   - Invoke the `new-bug` skill to file a canonical bug report for each failing test. Provide the full required input set in the invocation text:
     - `title`: concise regression title
     - `severity`: based on user impact, data risk, security risk, and how much of the system is blocked
     - `summary`: include the merge commit that introduced the regression, the destination branch, the source branch that was being integrated, and the classification (true regression or previously-uncovered failure)
     - `reproduction-status`: `confirmed`
     - `reproduction-steps`: the destination-branch command that now fails
     - `expected-behavior`: the command should pass after integration
     - `actual-behavior`: the failing test name and error message
     - `evidence`: failing command, stderr/stdout summary, merge commit, destination branch, source branch, and whether Step 4 ran and passed the test or never executed it
     - `environment`: current project/runtime details known from the verification run
     - `source-branch`: the source branch being integrated, so the bug-fix loop fixes the regression on that preserved branch before integration is retried
     - `suspected-area`: changed files implicated by the regression, or `unknown`
     - `fix-verification`: the destination-branch command that must pass after the fix
   - Commit the filed regression bug report(s) on `dev-agent`: `chore(bugs): file integration regression for <work-item-id>`.
3. Switch back to the destination branch.
4. After filing all regression bugs, **revert the merge commit**:
   ```bash
   git revert -m 1 HEAD --no-edit
   ```
   Commit message: `chore(<kind>): revert merge of <source-branch> — regression in <test-names>`
5. Switch back to the source branch: `git checkout <source-branch>`.
6. Stop and report:
   - Which regressions were found.
   - Which bug IDs were created.
   - That the merge was reverted and the source branch was not deleted.
   - Next step: the bugs must be resolved before re-attempting integration.

### Step 7: Finalize (Success Path Only)

Reached only when both Step 4 and Step 6 tests pass.

1. **Update the canonical task file** (if a task file was found in Step 2):
   - Move the task file from `project/tasks/in-progress/` to `project/tasks/completed/`
     with a deletion-aware git operation so the old-path deletion and new-path addition
     are staged atomically:
     ```bash
     git mv project/tasks/in-progress/<task-file> project/tasks/completed/<task-file>
     ```
     If the file was already moved in the working tree, repair the index before
     continuing:
     ```bash
     git rm project/tasks/in-progress/<task-file>
     git add project/tasks/completed/<task-file>
     ```
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
   If `-d` refuses (branch not considered merged by ancestry due to non-FF merge strategy or rebase history), stop and report:
   - The exact error output from `git branch -d`.
   - The merge commit SHA from Step 5.
   - Forced deletion is forbidden — do not escalate to the `-D` flag.
   - Instruct the human to inspect the branch and delete it manually once satisfied it is safe.

4. **Report success**:
   - Verify the lifecycle move actually landed — working-tree cleanliness alone is not
     enough, because a still-tracked old path can be clean:
     - Old path no longer tracked: `git ls-files project/tasks/in-progress/<task-file>`
       returns nothing (confirm against HEAD with
       `git ls-tree -r HEAD --name-only project/tasks/in-progress/`).
     - New path tracked: `git ls-files project/tasks/completed/<task-file>` returns the file.
     - No uncommitted move left behind: `git status --porcelain project/tasks/in-progress/`
       is empty.
     If any check fails, stop and report that the task lifecycle move is incomplete — the
     old path is still tracked, the new path is missing, or uncommitted changes remain.
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
| Merge conflict that merge-conflicts cannot solve | Stop — escalate to architect |
| Regressions found post-merge (Step 6) | File bugs, revert merge, stop |

## Commit Conventions

All integrator commits follow the `git-conventions` skill. Canonical patterns for this skill:

| What | Branch | Message pattern |
|---|---|---|
| Merge task branch | `<destination>` | `chore(tasks): merge T-NNN short-description` |
| Merge bug branch | `<destination>` | `chore(bugs): merge B-NNN short-description` |
| Move task to completed | `<destination>` | `chore(tasks): move T-NNN to completed` |
| Revert on regression | `<destination>` | `chore(<kind>): revert merge of <branch> — regression in <tests>` |

## Escalation

The Integrator's self-recovery threshold is **one bisect cycle**.
Return `ESCALATE` when a post-merge regression cannot be localized to a single task branch after one bisect, or the merge conflict in Step 5 cannot be resolved by the `merge-conflicts` skill.
Use this structured request:

```text
Problem: [what went wrong — unresolvable conflict, multi-task regression, etc.]
Attempted: [merge attempt, merge-conflicts invocation, bisect scope]
Failed because: [why the single-bisect or merge-conflicts could not isolate the cause]
Question: [specific guidance needed — which source task owns the behavior, which spec applies, etc.]
```

The active loop routes the request to the Architect via the `escalation-review` skill. Do not force-resolve or pick a side in a semantic conflict.

## Output Format

- **Result:** `PASS`, `FAIL`, `BLOCKED`, or `ESCALATE`.
- **Merge evidence:** source branch, destination branch, merge commit, and revert commit if one was produced.
- **Verification:** pre-merge and post-merge command results, including the coverage-gap flag when no project baseline command was discoverable, or why verification could not run.
- **State changes:** lifecycle file moves, regression bugs filed, and source branch deletion status.
- **Next action:** whether the active loop can continue or which owner must act next.

## Quality Criteria

- The canonical task or bug file on `dev-agent` was used for acceptance or fix-verification context.
- The source branch was verified before merge and the destination branch was verified after merge.
- Regression bugs include enough evidence for the bug-fix loop to reproduce and fix from the preserved source branch.
- Lifecycle-file edits from implementation branches were not merged.
- All commits follow the `git-conventions` skill.

## Common Pitfalls

- Merging a branch whose tests already fail on the source branch.
- Defaulting the destination-branch check to the same narrow command as the source-branch check instead of discovering the project baseline (Step 2 item 8), or silently skipping the coverage-gap flag when no baseline is discoverable.
- Filing regression bugs without setting `source-branch` to the preserved branch.
- Moving bug lifecycle state inside `integrate`; bug state is owned by `bug-loop`.
- Treating conflict resolution as a textual choice instead of preserving both work items' intent.

## What This Skill Does NOT Do

- Does not implement fixes — regressions are filed as bugs, not fixed in place.
- Does not touch `main` — human-only branch.
- Does not modify specifications or ADRs.
- Does not skip tests or bypass hooks (`--no-verify` is forbidden).
- Does not merge multiple branches in one invocation — call the skill once per branch.
- Does not merge task or bug lifecycle-file edits from implementation branches. Lifecycle state is owned by `dev-agent`.
