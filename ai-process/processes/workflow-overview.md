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
   ★ GATE 2: Task Plan Review (human) ★
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
│  │         ↓  (max 2 cycles)                │  │
│  │  ┌─────────────┐  FAIL ──────────────┐   │  │
│  │  │  REVIEWER   │  ← code-review      │   │  │
│  │  └──────┬──────┘                     │   │  │
│  │         │ PASS                       │   │  │
│  │         ↓                            ↑   │  │
│  │  git commit + move to completed/     │   │  │
│  │  Repeat for next task ───────────────┘   │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  Stops on: empty queue │ blocked task │ escalate│
└─────────┬──────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│  INTEGRATOR                          │
│  Merge in dependency order           │
│  ★ GATE 4: Integration Tests ★      │
│  Bisect on failure                   │
└─────────┬───────────────────────────┘
          ↓
   ★ GATE 5: Final Merge Approval (human) ★
          ↓
       ✓ DONE
```

## Phase Details

### 1. Brainstorm

**Agent:** Planner (creative mode).
**Skill:** brainstorm.
**Input:** Feature request or problem description from a human.
**Output:** Design document with explored alternatives and a recommended approach.
**Ends when:** Human approves the specification.

### 2. Task Breakdown

**Agent:** Planner (structured mode).
**Skill:** write-plan.
**Input:** Approved specification.
**Output:** Set of task files in `project/tasks/pending/`, each following `.claude/skills/new-task/assets/TEMPLATE-task.md`.
**Ends when:** Human approves the task plan.

### 3 & 4. Implementation + Code Review (automated via `/dev-loop`)

These two phases run as a tightly coupled loop driven by the `/dev-loop` skill.
After Gate 2 is approved, a human invokes:

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
6. On **PASS**: moves task to `completed/`, commits on `dev`, picks the next task.
7. On **FAIL** (cycles 1–2): sends task back to the Implementer with the reviewer's feedback.
8. On **FAIL** (cycle 3) or **ESCALATE**: moves task to `blocked/`, commits on `dev`, stops.

See `.claude/skills/dev-loop/SKILL.md` for the full procedure.

#### Implementer details

**Agent:** Implementer.
**Skills:** tdd, debug.
**Input:** Task file in `project/tasks/in-progress/`.
**Output:** Working code with passing tests, handoff note appended to the task file.

#### Reviewer details

**Agent:** Reviewer.
**Skill:** code-review.
**Input:** Completed task with code changes and implementer handoff note.
**Output:** Verdict appended to the task file under `### Review Verdict — [date]`.
**Two stages:**
1. Spec compliance — does the code do what the task requires?
2. Code quality — is it clean, secure, and maintainable?

**On review failure:**
1. The task stays in `project/tasks/in-progress/`.
2. Reviewer appends specific, actionable feedback under `### Review Feedback — [date]`.
3. `/dev-loop` routes the task back to the Implementer for fixes on the same branch.
4. Maximum two review cycles. On a third failure, `/dev-loop` escalates to architect.

#### When `/dev-loop` stops

| Condition | Task state | Action required |
|---|---|---|
| Queue empty | All in `completed/` | Run the integrator (Gate 4) |
| Task blocked | Moved to `blocked/` | Human resolves blocker, re-runs `/dev-loop` |
| Escalation | Moved to `blocked/` | Human adjusts spec or task, re-runs `/dev-loop` |
| `in-progress/` not empty at startup | Unchanged | Human decides whether to resume or abandon |

### 5. Integration

**Agent:** Integrator.
**Skill:** conflict-resolution (if needed).
**Input:** All reviewed and approved task branches.
**Output:** Merged codebase with passing integration tests.
**Process:**
1. Merge branches in dependency order.
2. Run full test suite.
3. If tests fail, bisect to identify the breaking change.
4. Create a fix task or escalate.
5. Confirm all integrated task branches are now merged and their task files are in `completed/`.

**Ends when:** Human approves the final merge (Gate 5).

Note: tasks are moved to `completed/` by `/dev-loop` immediately after the reviewer passes (Gate 3).
The integrator confirms that state, merges the code branches, and runs integration tests (Gate 4).

## Git Branching Strategy

Full rules and commit format: `ai-process/guidelines/git-conventions.md`.

**Branches:**
- `main` — human-only, production releases.
- `dev` — integration target. The integrator merges task branches here; planners, reviewers, and architects commit docs/specs directly here.
- `task/T-NNN-short-description` — created by the implementer at task pickup, deleted after successful integration.

**Key constraints:**
- No agent ever commits to `main`.
- The implementer never commits to `dev`.
- The integrator is the only agent that merges task branches into `dev`.
- Branches blocked at review stay open on their task branch until the blocker is resolved.

## Escalation

At any point, if an agent cannot complete its work:
1. **Architect consultation** — the architect agent reviews the situation and advises (one automatic attempt).
2. **Human escalation** — if the architect cannot resolve it, the issue is surfaced to a human.

See `ai-process/processes/escalation-procedure.md` for details.

## Quality Gates

Five checkpoints control the workflow (see `ai-process/processes/quality-gates.md` for full criteria):

| Gate | Checkpoint | Evaluator | Phase boundary |
|------|-----------|-----------|----------------|
| 1 | Spec Approval | Human | Brainstorm → Task Breakdown |
| 2 | Task Plan Review | Human | Task Breakdown → Parallel Execution |
| 3 | Code Review | Reviewer agent | Execution → Integration |
| 4 | Integration Tests | Automated suite | Integration → Final Review |
| 5 | Final Merge Approval | Human | Integration → Done |

Gates 1, 2, and 5 are human approval points — they keep humans in the loop on high-impact decisions.
Gates 3 and 4 are agent-evaluated — they catch defects before human review.
