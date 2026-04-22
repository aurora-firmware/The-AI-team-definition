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
│  PLANNER: Brainstorm      │  ← interactive exploration
│  Explore ideas            │
│  Produce design doc       │
└─────────┬────────────────┘
          ↓
   ★ GATE 1: Spec Approval (human) ★
          ↓
┌──────────────────────────┐
│  PLANNER: Task Breakdown  │  ← structured decomposition
│  Atomic tasks             │
│  Dependencies mapped      │
│  Verification defined     │
└─────────┬────────────────┘
          ↓
┌──────────────────────────┐
│  GATE 2: Task Plan        │  ← Architect evaluates
│  Preflight                │
│  Validate decomposition   │
│  Catch conflicts early    │
└─────────┬────────────────┘
          ↓
┌─────────────────────────────────────────────────────┐
│  DEVELOPMENT LOOP (human-invoked, runs autonomously) │
│                                                      │
│  ┌───────────────────────────────────────────────┐  │
│  │  SEQUENTIAL EXECUTION (per task)              │  │
│  │                                               │  │
│  │  ┌─────────────┐                              │  │
│  │  │  DEVELOPER  │  ← test-driven development   │  │
│  │  │ (one task)  │                              │  │
│  │  └──────┬──────┘                              │  │
│  │         ↓  (max 2 retries)                    │  │
│  │  ┌─────────────┐  FAIL ──────────────┐        │  │
│  │  │  REVIEWER   │  ← two-stage review │        │  │
│  │  └──────┬──────┘                     │        │  │
│  │         │ PASS                       │        │  │
│  │         ↓                            ↑        │  │
│  │  Integration → merge + test + done   │        │  │
│  │  Repeat for next task ───────────────┘        │  │
│  └───────────────────────────────────────────────┘  │
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

### 2. Task Breakdown + Gate 2

**Role:** Planner (structured mode), then Architect (Gate 2 evaluator).
**Procedure:** Structured task decomposition.
**Input:** Approved specification.
**Output:** Set of task files in `project/tasks/pending/`, validated by the Architect.

After the Planner writes the task files, the Architect automatically reviews the task plan:
- Checks dependency correctness and completeness.
- Identifies any two tasks that modify the same file without a declared dependency (merge conflict risk).
- Verifies architectural consistency with existing decision records.
- Creates corrective tasks or flags issues back to the Planner if problems are found.

Gate 2 is automated and does not require human approval.
When the Architect passes the task plan at Gate 2, the human starts the development loop.

### 3 & 4. Implementation + Code Review

After Gate 2 passes, a human starts the development loop. From that point the loop runs autonomously — no human intervention until the queue is empty, a task is blocked, or escalation is required.

#### What the development loop does

1. Picks the next task from `pending/` (priority → dependency readiness → creation date).
2. Moves it to `in-progress/`, creates the task branch, commits the state change on `dev-agent`.
3. Assigns the task to the **Developer** for test-driven implementation and debugging — waits for completion.
4. Assigns the completed task to the **Reviewer** for two-stage code review — waits for verdict.
5. Reads the verdict (`PASS` / `FAIL` / `ESCALATE`) from the task file.
6. On **PASS**: runs the integration procedure to merge the task branch into `dev-agent`, run tests, and move the task to `completed/`. Picks the next task.
7. On **FAIL** (cycles 1–2): sends task back to the Developer with the reviewer's feedback.
8. On **FAIL** (cycle 3) or **ESCALATE**: moves task to `blocked/`, commits on `dev-agent`, stops.

#### Developer details

**Role:** Developer.
**Procedure:** Test-driven implementation and debugging.
**Input:** Task file in `project/tasks/in-progress/`.
**Output:** Working code with passing tests, Work Log entry appended to the task file.

#### Reviewer details

**Role:** Reviewer.
**Procedure:** Two-stage code review.
**Input:** Completed task with code changes and Developer Work Log entry.
**Output:** Verdict appended to the task file under `### Review Verdict — [date]`.
**Two stages:**
1. Spec compliance — does the code do what the task requires?
2. Code quality — is it clean, secure, and maintainable?

**On review failure:**
1. The task stays in `project/tasks/in-progress/`.
2. Reviewer appends verdict and specific, actionable feedback under `### Review Verdict — [date]`.
3. The development loop routes the task back to the Developer for fixes on the same branch.
4. Up to two retries (three total review attempts). On a third failure, the development loop escalates to Architect.

#### When the development loop stops

| Condition | Task state | Action required |
|---|---|---|
| Queue empty | All in `completed/` | Human approves final merge to `main` (Gate 5) |
| Task blocked | Moved to `blocked/` | Human resolves blocker, restarts the development loop |
| Escalation | Moved to `blocked/` | Human adjusts spec or task, restarts the development loop |
| `in-progress/` not empty at startup | Unchanged | Human decides whether to resume or abandon |

### 5. Final Merge

Integration happens per-task inside the development loop: after each Reviewer PASS, the integration procedure merges the task branch into `dev-agent`, runs the full test suite, and moves the task to `completed/` (Gate 4).
If integration fails, the development loop stops and files a bug report — the task branch is not deleted and `dev-agent` is left clean.

Once the queue is empty and all tasks are in `completed/`, the human reviews the status summary and approves the merge to `main` (Gate 5).
This is a sign-off — the human confirms the outcome matches the spec intent, not individual code diffs.

**Ends when:** Human approves the merge from `dev-agent` to `main` (Gate 5).

### Bug-Fix Flow

When the development loop stops because the integration procedure found regressions, bugs are filed automatically as bug reports and the feature branch is preserved.
To fix these regressions, the human starts the bug-fix loop.

From that point the loop runs autonomously — same structure as the development loop but operating on `project/bugs/open/` instead of `project/tasks/pending/`.

#### What the bug-fix loop does

1. Picks the highest-severity open bug (critical → high → medium → low, oldest first on ties).
2. Moves it to `project/bugs/in-progress/`, creates a bug branch from `dev-agent` (`bug/B-NNN-short-description`).
3. Assigns the bug to the **Developer** — waits for completion.
4. Assigns the completed fix to the **Reviewer** — waits for verdict.
5. On **PASS**: runs the integration procedure to merge the bug branch into `dev-agent`, then moves the bug to `project/bugs/resolved/`.
6. On **FAIL** (cycles 1–2): sends the bug back to the Developer with the reviewer's feedback.
7. On **FAIL** (cycle 3) or **ESCALATE**: consults the Architect first. If the Architect cannot resolve it, stops and escalates to the human.

#### When to start the bug-fix loop

- After the development loop stops due to integration regressions — fix the filed bugs before restarting the development loop.
- Independently, whenever open bugs exist in `project/bugs/open/` that need autonomous resolution.

The development loop and bug-fix loop do not run concurrently.
The typical cycle after regressions: development loop stops → bugs filed → human starts bug-fix loop → bugs resolved → human restarts development loop.

## Git Branching Strategy

Full rules and commit format: `ai-process/guidelines/git-conventions.md`.

**Branches:**
- `main` — human-only, production releases.
- `dev-agent` — integration target. The integration procedure merges task branches here during the development loop; the Integrator handles manual merges and conflict resolution. Planners, Reviewers, and Architects commit docs/specs directly here.
- `task/T-NNN-short-description` — created by the Developer at task pickup, deleted after successful integration.

**Key constraints:**
- No automated role ever commits to `main`.
- The Developer never commits to `dev-agent`.
- The integration procedure is the standard path for merging task branches into `dev-agent`. The Integrator handles manual merges and conflict resolution.
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
