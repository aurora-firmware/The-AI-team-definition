---
title: "AI Team Workflow Overview"
status: approved
created: 2026-03-10
---

# AI Team Workflow Overview

## End-to-End Flow

```
Feature Request (human)
    ↓
┌──────────────────────────┐
│  PLANNER: Brainstorm     │  ← interactive exploration
│  Explore ideas           │
│  Produce design doc      │
└─────────┬────────────────┘
          ↓
   ★ GATE 1: Spec Approval (human) ★
          ↓
┌──────────────────────────┐
│  PLANNER: Task Breakdown │  ← structured decomposition
│  Atomic tasks            │
│  Dependencies mapped     │
│  Verification defined    │
└─────────┬────────────────┘
          ↓
┌──────────────────────────┐
│  GATE 2: Task Plan       │  ← Architect evaluates
│  Preflight               │
│  Validate decomposition  │
│  Catch conflicts early   │
└─────────┬────────────────┘
          ↓
┌──────────────────────────────────────────────────────┐
│  DEVELOPMENT LOOP (human-invoked, runs autonomously) │
│                                                      │
│  ┌───────────────────────────────────────────────┐   │
│  │  SEQUENTIAL EXECUTION (per task)              │   │
│  │                                               │   │
│  │  ┌─────────────┐                              │   │
│  │  │  DEVELOPER  │  ← test-driven development   │   │
│  │  │ (one task)  │                              │   │
│  │  └──────┬──────┘                              │   │
│  │         ↓  (max 2 retries)                    │   │
│  │  ┌─────────────┐  FAIL ──────────────┐        │   │
│  │  │  REVIEWER   │  ← two-stage review │        │   │
│  │  └──────┬──────┘                     │        │   │
│  │         │ PASS                       │        │   │
│  │         ↓                            ↑        │   │
│  │  Integration → merge + test + done   │        │   │
│  │  Repeat for next task ───────────────┘        │   │
│  └───────────────────────────────────────────────┘   │
│                                                      │
│  Stops on: empty queue │ blocked task │ escalation   │
└─────────┬────────────────────────────────────────────┘
          ↓
   ★ GATE 5: Final Merge Sign-off (human) ★
          ↓
       ✓ DONE
```

## Phase Details

### 1. Brainstorm

**Role:** Planner (creative mode).
**Procedure:** Interactive brainstorming.
**Input:** Feature request or problem description from a human.
**Output:** Specification document in `project/specs/`, written after the human has confirmed the direction.

This phase is **interactive**. The Planner does not produce a finished document for cold review — it works with the human through a dialogue:

1. Reads the request and checks for ambiguities.
2. Asks focused clarifying questions (batched, about five per round as a recommendation) if material unknowns exist, covering the six internal brainstorm categories. Runs a second round if coverage requires it. Stops and waits for answers.
3. Generates at least two solution alternatives and presents them briefly.
4. Asks the human to pick a direction (or provide the deciding constraint). Stops and waits.
5. Asks follow-up questions on scope or behaviour if the chosen direction still has gaps. One round maximum.
6. Confirms the approach in 2–3 sentences and gets explicit human sign-off before writing.
7. Writes the specification.

**Ends when:** Human approves the specification at Gate 1.
Because the human shaped the spec throughout the dialogue, Gate 1 approval should be quick.

**Lighter path — change-request:** For smaller changes that do not warrant a full new spec, the Planner uses a change-request document (`project/change-requests/CR-NNN-<slug>.md`) instead of the full brainstorm flow. A change-request records desired changes and possible spec amendments, then produces tasks and amendments as needed. Larger features still use the full brainstorm, Gate 1 approval, and task breakdown path. The CLI command `ai-team change-request new` creates a change-request document from the bundled template.

### 2. Task Breakdown + Gate 2

**Role:** Planner (structured mode), then Architect (Gate 2 evaluator).
**Procedure:** Structured task decomposition.
**Input:** Approved specification (or accepted change-request).
**Output:** Set of task files in `project/tasks/pending/`, validated by the Architect.

During breakdown the Planner explicitly considers whether the spec changes require documentation updates or test coverage updates. When they do, those updates are planned as implementation tasks or acceptance criteria — not as prerequisites before task creation. If documentation and test updates are not needed, the Planner omits them without creating placeholder tasks.

After the Planner writes the task files, the Architect automatically reviews the task plan at Gate 2. Gate 2 focuses on technical task-plan readiness — dependencies, file conflict risks, architectural consistency with existing decision records, atomicity, and verifiability. It does not reopen product or spec approval questions already settled at Gate 1.
- Checks dependency correctness and completeness.
- Identifies any two tasks that modify the same file without a declared dependency (merge conflict risk).
- Verifies architectural consistency with existing decision records.
- Returns a correction request to the Planner if problems are found; product-scope concerns that do not block technical readiness are noted as follow-up items, not Gate 2 failures.

Gate 2 is automated and does not require human approval.
When the Architect passes the task plan at Gate 2, the human starts the development loop.

### 3 & 4. Implementation + Code Review

After Gate 2 passes, a human starts the development loop. From that point the loop runs autonomously — no human intervention until the queue is empty, a task is blocked, or escalation is required.

#### Work-item state model

Task and bug files are canonical lifecycle state on `dev-agent`.
Implementation branches are for source, test, and project artifact changes.
They may contain a copy of the task or bug file for context, but the canonical status, Diagnosis Log, Work Log, and Review Verdict entries are the versions committed on `dev-agent`.

The active loop owns synchronization between role output and canonical lifecycle files:

1. Developers return Diagnosis Log and Work Log entries to the active loop as part of their handoff.
2. The active loop appends those entries to the canonical task or bug file on `dev-agent` and commits the lifecycle update before review starts.
3. Reviewers append Review Verdict entries to the canonical task or bug file on `dev-agent` and commit the verdict.
4. The active loop reads verdicts only from the committed canonical file on `dev-agent`.

This model is required for task-regression bugs, whose bug-fix branch is based on a preserved task branch that may not contain the bug report file.
The bug report remains available through the canonical bug file on `dev-agent`; the bug-fix loop passes its content to the Developer and Reviewer and records their log and verdict entries back to that canonical file.

#### What the development loop does

Before claiming the first task, the loop reads the project's documented baseline test command from the `## Test` section of the root `CLAUDE.md` and runs it. If the test command is missing or ambiguous, the loop escalates to the human rather than guessing. If it fails, the loop stops and reports the failure. Project test commands belong in root guidance files (`CLAUDE.md` or `AGENTS.md`) or in referenced project-local docs such as `project/docs/coding_guidelines.md`; `ai-team init` can scaffold these files from stable templates.

1. Picks the next task from `pending/` (priority → dependency readiness → creation date), using `ai-team list tasks --state pending`.
2. Moves it to `in-progress/`, creates the task branch, commits the state change on `dev-agent`.
3. Assigns the task to the **Developer** for test-driven implementation and debugging — waits for completion and a Work Log handoff.
4. Appends the Developer's Work Log entry to the canonical task file on `dev-agent` and commits it.
5. Assigns the completed task to the **Reviewer** for two-stage code review — waits for a committed verdict.
6. Reads the verdict (`PASS` / `FAIL` / `ESCALATE`) from the canonical task file on `dev-agent`.
7. On **PASS**: runs the integration procedure to merge the task branch into `dev-agent`, run tests, and move the task to `completed/`. Picks the next task.
8. On **FAIL** (cycles 1–2): sends task back to the Developer with the reviewer's feedback.
9. On **FAIL** (cycle 3) or **ESCALATE**: consults the Architect first. If the Architect cannot resolve it, moves the task to `blocked/`, commits on `dev-agent`, and stops for human action.

#### Developer details

**Role:** Developer.
**Procedure:** Test-driven implementation and debugging.
**Input:** Task file in `project/tasks/in-progress/`.
**Output:** Working code with passing tests on the task branch, plus a Work Log entry returned to the development loop for the canonical task file.

#### Reviewer details

**Role:** Reviewer.
**Procedure:** Two-stage code review.
**Input:** Completed task with code changes and Developer Work Log entry.
**Output:** Verdict appended and committed to the canonical task file on `dev-agent` under `### Review Verdict — [date]`.
**Two stages:**
1. Spec compliance — does the code do what the task requires?
2. Code quality — is it clean, secure, and maintainable?

**On review failure:**
1. The task stays in `project/tasks/in-progress/`.
2. Reviewer appends and commits verdict and specific, actionable feedback under `### Review Verdict — [date]`.
3. The development loop routes the task back to the Developer for fixes on the same branch.
4. Up to two retries (three total review attempts). On a third failure, the development loop escalates to Architect.

#### When the development loop stops

| Condition | Task state | Action required |
|---|---|---|
| Queue empty | All in `completed/` | Human approves final merge to `main` (Gate 5) |
| Task blocked | Moved to `blocked/` | Human resolves blocker, restarts the development loop |
| Human escalation | Moved to `blocked/` after Architect consultation fails | Human adjusts spec or task, restarts the development loop |
| `in-progress/` not empty at startup | Unchanged | Human decides whether to resume or abandon |

### 5. Final Merge

Integration happens per-task inside the development loop: after each Reviewer PASS, the integration procedure merges the task branch into `dev-agent`, runs the full test suite, and moves the task to `completed/` (Gate 4).
If integration fails because the task branch introduces a regression, the integration procedure reverts the merge, files a bug report that records the preserved task branch as `source_branch`, and leaves `dev-agent` clean.
The development loop stops until the regression bug is fixed on a branch based from that preserved task branch.

Once the queue is empty and all tasks are in `completed/`, the development loop produces a status summary for Gate 5.
The status summary lists the approved specification, completed tasks, unresolved bugs by severity, and latest integration-test result.
The human reviews that status summary and approves the merge to `main` (Gate 5).
This is a sign-off — the human confirms the outcome matches the spec intent, not individual code diffs.

**Ends when:** Human approves the merge from `dev-agent` to `main` (Gate 5).

### Bug-Fix Flow

When the development loop stops because the integration procedure found regressions, bugs are filed automatically as bug reports and the feature branch is preserved.
To fix these regressions, the human starts the bug-fix loop.

From that point the loop runs autonomously — same structure as the development loop but operating on `project/bugs/open/` instead of `project/tasks/pending/`.
Unlike feature tasks, bug fixes are diagnosis-first.
The Developer must reproduce or otherwise confirm the defect, gather evidence, isolate the fault, and record a root-cause hypothesis before changing production code.

#### Bug intake

Bugs may be filed by humans, Reviewers, Developers, or the integration procedure.
Before a bug report enters `project/bugs/open/`, the creator must capture enough diagnostic context for the bug-fix loop to start without guessing:

1. State the observable symptom and impact.
2. Record reproduction status: confirmed, intermittent, or not yet reproduced.
3. Include reproduction steps or the exact command/test that failed.
4. Capture relevant logs, stack traces, error output, screenshots, or failing assertions.
5. Record environment details and branch context, including `source_branch` for task-regression bugs.
6. Identify the suspected area if known, or explicitly say "unknown".
7. Define the fix-verification command or manual check.

If the issue cannot be reproduced yet, the bug may still be filed, but the report must say what evidence exists and what diagnostic step should be tried first.

#### What the bug-fix loop does

1. Picks the highest-severity open bug (critical → high → medium → low, oldest first on ties).
2. Moves it to `project/bugs/in-progress/`, creates a bug branch, and chooses the branch base from the bug type:
   - Existing defect on `dev-agent`: create the bug branch from `dev-agent`.
   - Regression introduced by a task branch: create the bug branch from the bug report's non-empty `source_branch`.
3. Assigns the bug to the **Developer** for diagnosis — passes the canonical bug report content and waits for a Diagnosis Log handoff before implementation continues.
4. The Developer reproduces or confirms the defect, gathers logs, isolates the likely fault, and records the root cause or the reason reproduction is impossible.
5. The bug-fix loop appends the Diagnosis Log entry to the canonical bug file on `dev-agent` and commits it.
6. The Developer fixes the isolated cause with the smallest change that resolves the defect, preferably by first adding or updating a failing regression test.
7. The bug-fix loop appends the Developer's Work Log entry to the canonical bug file on `dev-agent` and commits it.
8. Assigns the completed fix to the **Reviewer** — waits for a committed verdict in the canonical bug file.
9. On **PASS**: runs the integration procedure to merge the bug branch into its target branch, then moves the bug to `project/bugs/resolved/`.
   - Existing-defect bugs target `dev-agent`.
   - Task-regression bugs target the preserved task branch, after which the human restarts the development loop to retry task integration.
10. On **FAIL** (cycles 1–2): sends the bug back to the Developer with the reviewer's feedback.
11. On **FAIL** (cycle 3) or **ESCALATE**: consults the Architect first. If the Architect cannot resolve it, stops and escalates to the human.

#### When to start the bug-fix loop

- After the development loop stops due to integration regressions — fix the filed bugs before restarting the development loop.
- Independently, whenever open bugs exist in `project/bugs/open/` that need autonomous resolution.

The development loop and bug-fix loop do not run concurrently.
The typical cycle after regressions: development loop stops → bugs filed → human starts bug-fix loop → bugs resolved → human restarts development loop.

## Lifecycle State Machines

### Task Lifecycle

| State | Owner | Entry condition | Exit condition |
|---|---|---|---|
| `pending/` | Planner | Task is created from an approved specification | Development loop selects it |
| `in-progress/` | Development loop | Task is claimed and a task branch is created | Reviewer passes, task is blocked, or task is abandoned |
| task branch | Developer | Developer receives assignment | Developer submits for review |
| review pending | Reviewer | Developer reports completion | PASS, FAIL, or ESCALATE verdict |
| integration pending | Integration procedure | Reviewer returns PASS | Integration succeeds or fails |
| `completed/` | Integration procedure | Merge and tests pass | Task is included in the Gate 5 status summary |
| `blocked/` | Development loop or Escalation procedure | Max retries, escalation, or unresolved blocker | Human or Planner resolves blocker and returns task to `pending/` or `in-progress/` |

The development loop owns task state transitions and records Developer Work Log handoffs in the canonical task file on `dev-agent`.
The Developer owns source, test, and project artifact changes on the task branch, plus the Work Log content handed to the loop.
The Reviewer owns review verdict content and commits verdicts to the canonical task file on `dev-agent`.
The integration procedure owns merge and post-merge validation.

### Bug Lifecycle

| State | Owner | Entry condition | Exit condition |
|---|---|---|---|
| `open/` | Integration procedure or Human | Regression or defect is filed | Bug-fix loop selects it |
| `in-progress/` | Bug-fix loop | Bug branch is created | Reviewer passes, bug is blocked, or escalation occurs |
| diagnosis pending | Developer | Developer receives bug assignment | Defect is reproduced or evidence-backed non-reproduction is documented |
| bug branch | Developer | Root cause or fault hypothesis is recorded | Developer submits fix for review |
| review pending | Reviewer | Developer reports completion | PASS, FAIL, or ESCALATE verdict |
| integration pending | Integration procedure | Reviewer returns PASS | Integration succeeds or fails |
| `resolved/` | Integration procedure or Bug-fix loop | Fix is merged and tests pass | Bug is included in the Gate 5 status summary |

Bug branch base is part of the bug contract.
Existing-defect bugs use `dev-agent` as both source and target branch.
Task-regression bugs use the preserved task branch as both source and target branch, then the development loop retries the original task integration.
The canonical bug report remains on `dev-agent` even when the bug branch is based on another branch.
The bug-fix loop records Developer Diagnosis Log and Work Log handoffs in that canonical bug file, and the Reviewer commits verdicts there before the loop reads them.

### Gate Lifecycle

| Gate | Controls transition | Evaluator | Output |
|---|---|---|---|
| Gate 1: Specification Approval | Feature request → approved spec | Human | Approved specification |
| Gate 2: Task Plan Preflight | Task plan draft → implementation-ready task queue | Architect | Approved task queue or correction request |
| Gate 3: Code Review | Developer-complete task → integration-ready branch | Reviewer | PASS, FAIL, or ESCALATE |
| Gate 4: Integration Tests | Reviewed branch → completed task or bug | Integration procedure | Merged/completed or regression report |
| Gate 5: Final Merge Sign-off | Completed queue → production merge | Human | Approval to merge `dev-agent` to `main` |

Each gate defines its input artifact, evaluator, pass output, fail output, and next owner in `ai-process/processes/quality-gates.md`.

## Git Branching Strategy

Full rules and commit format: `ai-process/guidelines/git-conventions.md`.

**Branches:**
- `main` — human-only, production releases.
- `dev-agent` — integration target and canonical lifecycle state branch. The integration procedure merges task branches here during the development loop; the Integrator handles manual merges and conflict resolution. Planners, Reviewers, Architects, and active loops commit docs/specs/task/bug state here.
- `task/T-NNN-short-description` — implementation branch for a single task, deleted after successful integration.
- `bug/B-NNN-short-description` — implementation branch for a single bug, created by the bug-fix loop from `dev-agent` or the bug report's `source_branch`, deleted after successful integration.

**Key constraints:**
- No automated role ever commits to `main`.
- The Developer never commits to `dev-agent`.
- The integration procedure is the standard path for merging task branches into `dev-agent`. The Integrator handles manual merges and conflict resolution.
- The integration procedure is also the standard path for merging bug branches into their target branch.
- Task and bug lifecycle files are canonical on `dev-agent`; implementation branches are not the source of truth for lifecycle state.
- Branches blocked at review stay open on their task branch until the blocker is resolved.

## Escalation

At any point, if a role cannot complete its work:
1. **Architect consultation** — the Architect reviews the situation and advises (one automatic attempt).
2. **Human escalation** — if the Architect cannot resolve it, the issue is surfaced to a human.

See `ai-process/processes/escalation-procedure.md` for details.

## Quality Gates

Five gates control the workflow (see `ai-process/processes/quality-gates.md` for full criteria):

| Gate | Checkpoint | Evaluator | Phase boundary |
|------|-----------|-----------|----------------|
| 1 | Spec Approval | Human | Brainstorm → Task Breakdown |
| 2 | Task Plan Preflight | Architect | Task Breakdown → Development Loop |
| 3 | Code Review | Reviewer | Implementation → Integration (per-task, inside the development loop) |
| 4 | Integration Tests | Integration procedure | Review → Completed (per-task, inside the development loop) |
| 5 | Final Merge Sign-off | Human | `dev-agent` → `main` |

Gates 1 and 5 are human touchpoints — design approval and final production sign-off.
Gate 2 is automated — it catches structural problems in the task plan before implementation starts.
Gates 3 and 4 are automated role and procedure checks — they catch defects during execution.
