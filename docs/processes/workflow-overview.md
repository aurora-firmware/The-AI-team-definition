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
   ★ HUMAN GATE: Spec Approval ★
          ↓
┌─────────────────────────┐
│  PLANNER: Task Breakdown │  ← write-plan skill, structured mode
│  Atomic tasks            │
│  Dependencies mapped     │
│  Verification defined    │
└─────────┬───────────────┘
          ↓
   ★ HUMAN GATE: Task Plan Review ★
          ↓
┌────────────────────────────────────────────┐
│  PARALLEL EXECUTION                         │
│                                             │
│  ┌─────────────┐  ┌─────────────┐          │
│  │ IMPLEMENTER │  │ IMPLEMENTER │  ...     │
│  │ + TESTER    │  │ + TESTER    │          │
│  │ (Task A)    │  │ (Task B)    │          │
│  └──────┬──────┘  └──────┬──────┘          │
│         ↓                ↓                  │
│  ┌─────────────┐  ┌─────────────┐          │
│  │  REVIEWER   │  │  REVIEWER   │          │
│  │  (Task A)   │  │  (Task B)   │          │
│  └──────┬──────┘  └──────┬──────┘          │
└─────────┼────────────────┼─────────────────┘
          ↓                ↓
┌─────────────────────────────────────┐
│  INTEGRATOR                          │
│  Merge in dependency order           │
│  Run integration tests               │
│  Bisect on failure                   │
└─────────┬───────────────────────────┘
          ↓
   ★ HUMAN GATE: Final Merge Approval ★
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
**Output:** Set of task files in `tasks/pending/`, each following `TEMPLATE-task.md`.
**Ends when:** Human approves the task plan.

### 3. Parallel Execution

**Agents:** Implementer + Tester (per task).
**Skills:** tdd, debug.
**Input:** A single task file moved to `tasks/in-progress/`.
**Output:** Working code with passing tests.
**Constraint:** No two agents modify the same file simultaneously.
**Ends when:** All acceptance criteria in the task are met.

### 4. Code Review

**Agent:** Reviewer.
**Skill:** code-review.
**Input:** Completed task with code changes.
**Output:** Pass/fail verdict with notes.
**Two stages:**
1. Spec compliance — does the code do what the task requires?
2. Code quality — is it clean, secure, and maintainable?

**Ends when:** Reviewer passes both stages, or task returns to implementer for fixes.

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

**Ends when:** Human approves the final merge.

## Escalation

At any point, if an agent cannot complete its work:
1. **Architect consultation** — the architect agent reviews the situation and advises (one automatic attempt).
2. **Human escalation** — if the architect cannot resolve it, the issue is surfaced to a human.

See `docs/processes/escalation-procedure.md` for details.

## Human Gates

Three mandatory approval points:
1. **Spec approval** — after brainstorm, before task breakdown.
2. **Task plan review** — after task breakdown, before execution.
3. **Final merge approval** — after integration tests pass, before merging to main.

These gates exist to keep humans in the loop on high-impact decisions. See `docs/processes/quality-gates.md`.
