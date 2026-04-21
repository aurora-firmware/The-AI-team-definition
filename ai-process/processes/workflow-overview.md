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
┌─────────────────────┐
│  PLANNER: Brainstorm │  ← brainstorm skill, creative mode
│  Explore ideas       │
│  Produce design doc  │
└─────────┬───────────┘
          ↓
   ★ GATE 1: Spec Approval (human) ★
          ↓
┌─────────────────────────┐
│  PLANNER: Task Breakdown │  ← write-plan skill, structured mode
│  Atomic tasks            │
│  Dependencies mapped     │
│  Verification defined    │
└─────────┬───────────────┘
          ↓
┌─────────────────────────┐
│  ARCHITECT: Preflight    │  ← automated, no human gate
│  Validate decomposition  │
│  Catch conflicts early   │
└─────────┬───────────────┘
          ↓
┌────────────────────────────────────────────────┐
│  /dev-loop  (human-invoked, runs autonomously)  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  SEQUENTIAL EXECUTION (per task)         │  │
│  │                                          │  │
│  │  ┌─────────────┐                         │  │
│  │  │ IMPLEMENTER │  ← tdd, debug           │  │
│  │  │ (one task)  │                         │  │
│  │  └──────┬──────┘                         │  │
│  │         ↓  (max 2 retries)               │  │
│  │  ┌─────────────┐  FAIL ──────────────┐   │  │
│  │  │  REVIEWER   │  ← code-review      │   │  │
│  │  └──────┬──────┘                     │   │  │
│  │         │ PASS                       │   │  │
│  │         ↓                            ↑   │  │
│  │  /integrate → merge + test + done    │   │  │
│  │  Repeat for next task ───────────────┘   │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  Stops on: empty queue │ blocked task │ escalate│
└─────────┬──────────────────────────────────────┘
          ↓
   ★ GATE 4: Final Merge Sign-off (human) ★
          ↓
       ✓ DONE
```

## Phase Details

### 1. Brainstorm

**Agent:** Planner (creative mode).
**Skill:** brainstorm.
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

### 2. Task Breakdown + Architect Preflight

**Agent:** Planner (structured mode), then Architect (preflight).
**Skills:** write-plan.
**Input:** Approved specification.
**Output:** Set of task files in `project/tasks/pending/`, validated by the Architect.

After the Planner writes the task files, the Architect automatically reviews the task plan:
- Checks dependency correctness and completeness.
- Identifies any two tasks that modify the same file without a declared dependency (merge conflict risk).
- Verifies architectural consistency with existing decision records.
- Creates corrective tasks or flags issues back to the Planner if problems are found.

No human approval is required — the Architect's preflight replaces Gate 2.
When the Architect signals the plan is sound, the human invokes `/dev-loop`.

### 3 & 4. Implementation + Code Review (automated via `/dev-loop`)

After the Architect preflight completes, a human invokes:

```
/dev-loop
```

From that point the loop runs autonomously — no human intervention until the queue is empty, a task is blocked, or escalation is required.

#### What `/dev-loop` does

1. Picks the next task from `pending/` (priority → dependency readiness → creation date).
2. Moves it to `in-progress/`, creates the task branch, commits the state change on `dev`.
3. Spawns the **Implementer** agent (skills: tdd, debug) — waits for completion.
4. Spawns the **Reviewer** agent (skill: code-review) — waits for verdict.
5. Reads the verdict (`PASS` / `FAIL` / `ESCALATE`) from the task file.
6. On **PASS**: invokes the `integrate` skill to merge the task branch into `dev`, run tests, and move the task to `completed/`. Picks the next task.
7. On **FAIL** (cycles 1–2): sends task back to the Implementer with the reviewer's feedback.
8. On **FAIL** (cycle 3) or **ESCALATE**: moves task to `blocked/`, commits on `dev`, stops.

See `.claude/skills/dev-loop/SKILL.md` for the full procedure.

#### Implementer details

**Agent:** Implementer.
**Skills:** tdd, debug.
**Input:** Task file in `project/tasks/in-progress/`.
**Output:** Working code with passing tests, Work Log entry appended to the task file.

#### Reviewer details

**Agent:** Reviewer.
**Skill:** code-review.
**Input:** Completed task with code changes and implementer Work Log entry.
**Output:** Verdict appended to the task file under `### Review Verdict — [date]`.
**Two stages:**
1. Spec compliance — does the code do what the task requires?
2. Code quality — is it clean, secure, and maintainable?

**On review failure:**
1. The task stays in `project/tasks/in-progress/`.
2. Reviewer appends verdict and specific, actionable feedback under `### Review Verdict — [date]`.
3. `/dev-loop` routes the task back to the Implementer for fixes on the same branch.
4. Up to two retries (three total review attempts). On a third failure, `/dev-loop` escalates to Architect.

#### When `/dev-loop` stops

| Condition | Task state | Action required |
|---|---|---|
| Queue empty | All in `completed/` | Human approves final merge to `main` (Gate 4) |
| Task blocked | Moved to `blocked/` | Human resolves blocker, re-runs `/dev-loop` |
| Escalation | Moved to `blocked/` | Human adjusts spec or task, re-runs `/dev-loop` |
| `in-progress/` not empty at startup | Unchanged | Human decides whether to resume or abandon |

### 5. Final Merge

Integration happens per-task inside the `/dev-loop` cycle: after each reviewer PASS, the `integrate` skill merges the task branch into `dev`, runs the full test suite, and moves the task to `completed/` (Gate 3).
If integration fails, `/dev-loop` stops and files a bug — the task branch is not deleted and `dev` is left clean.

Once the queue is empty and all tasks are in `completed/`, the human reviews the `/status-report` summary and approves the merge to `main` (Gate 4).
This is a sign-off — the human confirms the outcome matches the spec intent, not individual code diffs.

**Ends when:** Human approves the merge from `dev` to `main` (Gate 4).

### Bug-Fix Flow (automated via `/bug-loop`)

When `/dev-loop` stops because the `integrate` skill found regressions, bugs are filed automatically via `/new-bug` and the feature branch is preserved.
To fix these regressions, the human invokes:

```
/bug-loop
```

From that point the loop runs autonomously — same structure as `/dev-loop` but operating on `project/bugs/open/` instead of `project/tasks/pending/`.

#### What `/bug-loop` does

1. Picks the highest-severity open bug (critical → high → medium → low, oldest first on ties).
2. Moves it to `project/bugs/in-progress/`, creates a bug branch from `dev` (`bug/B-NNN-short-description`).
3. Spawns the **Implementer** agent — waits for completion.
4. Spawns the **Reviewer** agent — waits for verdict.
5. On **PASS**: invokes the `integrate` skill to merge the bug branch into `dev`, then moves the bug to `project/bugs/resolved/`.
6. On **FAIL** (cycles 1–2): sends the bug back to the Implementer with the reviewer's feedback.
7. On **FAIL** (cycle 3) or **ESCALATE**: consults the Architect first. If the Architect cannot resolve it, stops and escalates to the human.

See `.claude/skills/bug-loop/SKILL.md` for the full procedure.

#### When to invoke `/bug-loop`

- After `/dev-loop` stops due to integration regressions — fix the filed bugs before re-running `/dev-loop`.
- Independently, whenever open bugs exist in `project/bugs/open/` that need autonomous resolution.

`/dev-loop` and `/bug-loop` do not run concurrently.
The typical cycle after regressions: `/dev-loop` stops → bugs filed → human invokes `/bug-loop` → bugs resolved → human re-invokes `/dev-loop`.

## Git Branching Strategy

Full rules and commit format: `ai-process/guidelines/git-conventions.md`.

**Branches:**
- `main` — human-only, production releases.
- `dev` — integration target. The `integrate` skill merges task branches here (invoked by `/dev-loop`); the Integrator agent handles manual merges and conflict resolution. Planners, reviewers, and architects commit docs/specs directly here.
- `task/T-NNN-short-description` — created by the implementer at task pickup, deleted after successful integration.

**Key constraints:**
- No agent ever commits to `main`.
- The implementer never commits to `dev`.
- The `integrate` skill (invoked by `/dev-loop`) is the standard path for merging task branches into `dev`. The Integrator agent handles manual merges and conflict resolution.
- Branches blocked at review stay open on their task branch until the blocker is resolved.

## Escalation

At any point, if an agent cannot complete its work:
1. **Architect consultation** — the architect agent reviews the situation and advises (one automatic attempt).
2. **Human escalation** — if the architect cannot resolve it, the issue is surfaced to a human.

See `ai-process/processes/escalation-procedure.md` for details.

## Quality Gates

Four checkpoints control the workflow (see `ai-process/processes/quality-gates.md` for full criteria):

| Gate | Checkpoint | Evaluator | Phase boundary |
|------|-----------|-----------|----------------|
| 1 | Spec Approval | Human | Brainstorm → Task Breakdown |
| — | Architect Preflight | Architect agent | Task Breakdown → `/dev-loop` |
| 2 | Code Review | Reviewer agent | Implementation → Integration (per-task, inside `/dev-loop`) |
| 3 | Integration Tests | `integrate` skill | Review → Completed (per-task, inside `/dev-loop`) |
| 4 | Final Merge Sign-off | Human | `dev` → `main` |

Gates 1 and 4 are human touchpoints — design approval and final production sign-off.
The Architect Preflight is automated — it catches structural problems in the task plan before agents start coding.
Gates 2 and 3 are agent-evaluated — they catch defects during execution.
