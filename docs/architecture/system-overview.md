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
│  │ creative │  │ advisory     │  │ merge + test       │    │
│  │ + struct │  │ + escalation │  │ + conflict resolve │    │
│  └────┬─────┘  └──────┬───────┘  └─────────┬──────────┘    │
│       │               │                     │               │
│       ↓               ↓ (on demand)         ↑               │
│  ┌──────────────────────────────────────────┤               │
│  │         EXECUTION POOL                   │               │
│  │                                          │               │
│  │  ┌─────────────┐  ┌─────────────┐       │               │
│  │  │ IMPLEMENTER │  │ IMPLEMENTER │  ...  │               │
│  │  │ + TESTER    │  │ + TESTER    │       │               │
│  │  └──────┬──────┘  └──────┬──────┘       │               │
│  │         ↓                ↓              │               │
│  │  ┌─────────────┐  ┌─────────────┐       │               │
│  │  │  REVIEWER   │  │  REVIEWER   │       │               │
│  │  └──────┬──────┘  └──────┬──────┘       │               │
│  │         └────────────────┴───────────────┘               │
│  └──────────────────────────────────────────────────────────┘
│                                                              │
│  ★ HUMAN GATES: Spec approval, Task plan review, Final merge │
└─────────────────────────────────────────────────────────────┘
```

## Layers

### Planning Layer

**Agents:** Planner, Architect.
**Purpose:** Transform a feature request into an approved specification and a set of executable tasks.
**Key principle:** Separate creative exploration (brainstorming) from structured decomposition (task breakdown).

### Execution Layer

**Agents:** Implementer, Tester, Reviewer.
**Purpose:** Produce working, tested, reviewed code for each task.
**Key principle:** Tasks are atomic and parallelizable. No two agents modify the same file simultaneously.

### Integration Layer

**Agents:** Integrator.
**Purpose:** Merge completed work, run integration tests, and resolve conflicts.
**Key principle:** Merge in dependency order. Test once (optimistic). Bisect on failure.

### Oversight Layer

**Actors:** Humans.
**Purpose:** Approve high-impact decisions at three gates.
**Key principle:** Humans stay in the loop without becoming bottlenecks. Only three mandatory gates.

## Information Flow

| From | To | What |
|---|---|---|
| Human | Planner | Feature request or problem description |
| Planner | Human | Specification for approval |
| Planner | Task directory | Task files in `tasks/pending/` |
| Task directory | Implementer | Individual task assignment |
| Implementer | Reviewer | Completed code for review |
| Reviewer | Implementer | Feedback (if review fails) |
| Reviewer | Integrator | Approved code (if review passes) |
| Any agent | Architect | Escalation request |
| Architect | Requesting agent | Advisory guidance |
| Architect | Human | Escalation (if architect cannot resolve) |
| Integrator | Human | Merged code for final approval |

## Design Decisions

1. **File-based task tracking** — agents read and write Markdown files natively. No external databases or issue trackers required.
2. **Filesystem state machine** — task status is represented by which directory the file lives in, making it visible and auditable.
3. **Separation of agents and skills** — agents are roles (who), skills are procedures (how). Skills can be composed and reused across agent roles.
4. **Three human gates** — enough oversight to catch major issues, few enough to avoid bottlenecking the team.
