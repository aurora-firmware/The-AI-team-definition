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
┌───────────────────────────────────┐
│  SEQUENTIAL EXECUTION (per task)  │
│                                   │
│  ┌─────────────┐                  │
│  │ IMPLEMENTER │  ← tdd, debug   │
│  │ (one task)  │                  │
│  └──────┬──────┘                  │
│         ↓                         │
│  ★ GATE 3: Code Review ★         │
│  ┌─────────────┐                  │
│  │  REVIEWER   │  ← code-review  │
│  └──────┬──────┘                  │
│         ↓                         │
│  Repeat for next task             │
└─────────┬─────────────────────────┘
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

### 3. Implementation

**Agents:** One implementer agent processes tasks sequentially.
**Skills:** tdd, debug.
**Input:** A single task file moved to `project/tasks/in-progress/` by the implementer.
**Output:** Working code with passing tests.
**Ends when:** All acceptance criteria in the task are met and the task is handed off to the reviewer.

**Task pickup order:** The implementer selects the next task from `project/tasks/pending/` using:
1. Highest priority first (`critical > high > medium > low`).
2. Among equal priority, tasks whose dependencies are all in `completed/` first.
3. Among remaining ties, the task with the earliest `created` date.

**Task state transitions during this phase:**
- Implementer moves the task from `project/tasks/pending/` to `project/tasks/in-progress/`.
- If blocked, implementer moves it to `project/tasks/blocked/` and escalates.
- When the blocker is resolved, implementer moves it back to `project/tasks/in-progress/`.

### 4. Code Review

**Agent:** Reviewer.
**Skill:** code-review.
**Input:** Completed task with code changes and a handoff note from the implementer (see `ai-process/templates/handoff-note.md`).
**Output:** Pass/fail verdict with notes.
**Two stages:**
1. Spec compliance — does the code do what the task requires?
2. Code quality — is it clean, secure, and maintainable?

**Ends when:** Reviewer passes both stages, or task returns to implementer for fixes.

**On review failure:**
1. The task stays in `project/tasks/in-progress/` (it does not move).
2. The reviewer appends feedback to the task file's **Notes** section, prefixed with `### Review Feedback — [date]`.
3. The implementer reads the feedback, makes fixes on the same task branch, and re-submits for review.
4. Maximum two review cycles per task. If the task still fails after two rejections, escalate to architect.

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
5. Move each successfully integrated task from `project/tasks/in-progress/` to `project/tasks/completed/`.

**Ends when:** Human approves the final merge (Gate 5).

The integrator is the only agent that moves tasks to `completed/`.
A task reaches `completed/` only after passing both code review (Gate 3) and integration tests (Gate 4).

## Git Branching Strategy

<!-- TODO: Define the full branching strategy. This section needs:
     - Base branch convention (e.g., main)
     - Task branch naming convention (e.g., task/T-003-implement-auth-flow)
     - When branches are created (at task pickup) and by whom (implementer)
     - When branches are deleted (after successful integration)
     - How the integrator merges task branches into the base branch
     - What happens to branches when a task is blocked or rejected at review
     See report.md issue 2.6 for full context. -->

This section is pending definition. The branching model must be defined before the integrator and conflict-resolution skill can operate.

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
