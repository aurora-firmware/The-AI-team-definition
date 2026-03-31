---
title: "Component Map"
status: approved
created: 2026-03-10
---

# Component Map

This document maps every component in the AI team framework: what it is, what it interacts with, and where it is defined.

## Agents

| Agent | Purpose | Skills Used | Receives From | Hands Off To | Definition |
|---|---|---|---|---|---|
| Planner | Breaks features into specs and tasks | brainstorm, write-plan | Human | Human (approval), Task directory (`pending/`) | `.claude/agents/planner.md` |
| Architect | Advises on design and failure recovery | — (advisory role) | Any blocked agent | Requesting agent, or Human (escalation) | `.claude/agents/architect.md` |
| Implementer | Writes tests and production code using TDD | tdd, debug | Task directory | Reviewer | `.claude/agents/implementer.md` |
| Reviewer | Reviews code for spec compliance and quality | code-review | Implementer (via `/dev-loop`) | `/dev-loop` (verdict in task file) | `.claude/agents/reviewer.md` |
| Integrator | Resolves merge conflicts; manual merges into `dev`/`main` | conflict-resolution | `integrate` skill (conflicts), Human (manual merges) | `dev` or `main` branch | `.claude/agents/integrator.md` |

## Skills

| Skill | Purpose | Used By | Definition |
|---|---|---|---|
| brainstorm | Explore solution space, evaluate trade-offs | Planner | `.claude/skills/brainstorm/SKILL.md` |
| write-plan | Decompose feature into atomic tasks | Planner | `.claude/skills/write-plan/SKILL.md` |
| dev-loop | Autonomous Implementer → Reviewer loop across all pending tasks | Orchestrator (human-invoked) | `.claude/skills/dev-loop/SKILL.md` |
| code-review | Two-stage review (spec + quality) | Reviewer | `.claude/skills/code-review/SKILL.md` |
| tdd | Test-driven development cycle | Implementer | `.claude/skills/tdd/SKILL.md` |
| debug | Reproduce, isolate, fix, verify | Implementer | `.claude/skills/debug/SKILL.md` |
| integrate | Merge task branch, run tests, promote task to completed | `/dev-loop` (per-task) | `.claude/skills/integrate/SKILL.md` |
| bug-loop | Autonomous bug-fix loop across open bugs | Orchestrator (human-invoked) | `.claude/skills/bug-loop/SKILL.md` |
| conflict-resolution | Resolve git merge conflicts | Integrator | `.claude/skills/conflict-resolution/SKILL.md` |

## Documents and Directories

| Component | Type | Purpose | Location |
|---|---|---|---|
| Specifications | Directory | Feature and system specs | `project/specifications/` |
| Task Board | Directory tree | Task lifecycle tracking | `project/tasks/{pending,in-progress,completed,blocked}/` |
| Bug Tracker | Directory tree | Bug lifecycle tracking | `project/bugs/{open,in-progress,resolved}/` |
| Decision Log | Directory | Architecture decision records | `project/decisions/` |
| Templates | Skill assets | Reusable document formats | `.claude/skills/*/assets/` and `ai-process/templates/` |
| Process Docs | Directory | Workflow and procedure definitions | `ai-process/processes/` |
| Guidelines | Directory | Standards and checklists | `ai-process/guidelines/` |
| Architecture Docs | Directory | System design documentation | `ai-process/architecture/` |
| Action Skills | Directory | Automation for document creation | `.claude/skills/` (with `disable-model-invocation: true`) |

## Interaction Diagram

```
Human ←──→ Planner ──→ Task Directory ──→ Implementer ──→ Reviewer ──→ Integrator ──→ Human
              ↑                              ↑    ↑           ↑             ↑
              │                              │    │           │             │
              └──────── Architect ───────────┴────┴───────────┴─────────────┘
                      (consulted on demand by any agent)
```
