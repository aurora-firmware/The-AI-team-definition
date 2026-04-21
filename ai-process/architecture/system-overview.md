---
title: "AI Team System Overview"
status: approved
created: 2026-03-10
---

# AI Team System Overview

## What This Defines

This document describes the architecture of an AI agent team — how agents are organized, how work flows between them, and how quality is maintained. It is not about a specific software product; it is the operating model that any AI-developed project can adopt.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        AI AGENT TEAM                         │
│                                                              │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ PLANNER  │  │  ARCHITECT   │  │    INTEGRATOR      │    │
│  │          │  │              │  │                    │    │
│  │ creative │  │ structural   │  │ merge + test       │    │
│  │ + struct │  │ + preflight  │  │ + conflict resolve │    │
│  └────┬─────┘  └──────┬───────┘  └─────────┬──────────┘    │
│       │               │                     │               │
│       ↓               ↓ (on demand)         ↑               │
│  ┌──────────────────────────────────────────┤               │
│  │         EXECUTION POOL                   │               │
│  │                                          │               │
│  │  ┌─────────────┐  ┌─────────────┐       │               │
│  │  │ IMPLEMENTER │  │ IMPLEMENTER │  ...  │               │
│  │  │   (TDD)    │  │   (TDD)    │       │               │
│  │  └──────┬──────┘  └──────┬──────┘       │               │
│  │         ↓                ↓              │               │
│  │  ┌─────────────┐  ┌─────────────┐       │               │
│  │  │  REVIEWER   │  │  REVIEWER   │       │               │
│  │  └──────┬──────┘  └──────┬──────┘       │               │
│  │         └────────────────┴───────────────┘               │
│  └──────────────────────────────────────────────────────────┘
│                                                              │
│  ★ HUMAN GATES: Spec approval, Final merge sign-off          │
└─────────────────────────────────────────────────────────────┘
```

## Layers

### Planning Layer

**Agents:** Planner, Architect.
**Purpose:** Transform a feature request into an approved specification and a set of executable tasks.
**Key principle:** Separate creative exploration (brainstorming) from structured decomposition (task breakdown).

### Orchestration Layer

**Skill:** `/dev-loop`.
**Purpose:** Drive the full Implementer → Reviewer loop autonomously across all pending tasks.
**Key principle:** The human invokes the loop once after the Architect preflight; the loop runs until the queue is empty or a hard stop is hit (blocked task, escalation). No human input is required between tasks.

### Execution Layer

**Agents:** Implementer, Reviewer.
**Purpose:** Produce working, tested, reviewed code for each task.
**Key principle:** Tasks are atomic and independent. The implementer writes both tests and production code using the TDD skill. The reviewer evaluates spec compliance and code quality. Both are spawned and sequenced by `/dev-loop`.

### Integration Layer

**Skill:** `integrate` (invoked per-task by `/dev-loop`).
**Agent:** Integrator (conflict resolution and manual merges into `dev`/`main`).
**Purpose:** Merge completed work, run integration tests, and resolve conflicts.
**Key principle:** Merge in dependency order. Test once (optimistic). Revert and file bugs on failure.

### Oversight Layer

**Actors:** Humans.
**Purpose:** Approve high-impact decisions at two gates.
**Key principle:** Humans stay in the loop without becoming bottlenecks. Only two mandatory gates.

## Information Flow

> Note: `/dev-loop` is an orchestration skill (workflow subprocess), not an agent role. The table tracks control/data flow between humans, agents, and the orchestrator.

| From | To | What |
|---|---|---|
| Human | Planner | Feature request or problem description |
| Planner | Human | Specification for approval |
| Planner | Task directory | Task files in `project/tasks/pending/` |
| Planner | Architect | Task plan preflight request |
| Architect | `/dev-loop` | Validated task plan — ready to run |
| Human | `/dev-loop` | Invocation after Architect preflight |
| `/dev-loop` | Implementer | Task assignment (spawned per task) |
| Implementer | `/dev-loop` | Completion signal; Work Log entry in task file |
| `/dev-loop` | Reviewer | Review request (spawned per task) |
| Reviewer | `/dev-loop` | Verdict in task file (`PASS`/`FAIL`/`ESCALATE`) |
| `/dev-loop` | Implementer | Feedback routing (on `FAIL`) |
| `/dev-loop` | `integrate` skill | Merge request (on `PASS`) |
| `integrate` skill | Task directory | State transitions (`in-progress` → `completed`) |
| `/dev-loop` | Task directory | State transitions (`in-progress` → `blocked`) |
| `/dev-loop` | Human | Stop notification (queue empty, blocked, or escalation) |
| Any agent | Architect | Escalation request |
| Architect | Requesting agent | Advisory guidance |
| Architect | Human | Escalation (if architect cannot resolve) |
| Human | `main` | Final merge from `dev` after Gate 4 sign-off |

## Design Decisions

1. **File-based task tracking** — agents read and write Markdown files natively. No external databases or issue trackers required.
2. **Filesystem state machine** — task status is represented by which directory the file lives in, making it visible and auditable.
3. **Separation of agents and skills** — agents are roles (who), skills are procedures (how). Skills can be composed and reused across agent roles.
4. **Two human gates** — Gate 1 (spec approval, where design decisions are made) and Gate 4 (final merge sign-off, where outcomes are confirmed). Everything between is agent-driven. The Architect preflight replaces the former Gate 2 (task plan review) with an automated structural check, removing a human bottleneck without losing the quality check.
5. **Orchestration via skill, not agent** — the Implementer → Reviewer loop is driven by the `/dev-loop` skill rather than a dedicated orchestrator agent. A skill is the right primitive when the control flow is deterministic and human-invoked. An orchestrator agent would add value only if it needed to be spawned programmatically by other agents or required its own decision authority beyond following the loop procedure.
