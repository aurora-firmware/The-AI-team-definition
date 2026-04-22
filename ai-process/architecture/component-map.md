---
title: "Component Map"
status: approved
created: 2026-03-10
---

# Component Map

This document maps the ai-process roles, procedures, processes, and gates to their implementation files where applicable.

## Roles

| Role | Purpose | Procedures Used | Receives From | Hands Off To | Implementation |
|---|---|---|---|---|---|
| Planner | Breaks features into specs and tasks | Interactive Brainstorming; Structured Task Decomposition | Human | Human (approval), Task directory (`pending/`) | `.claude/agents/planner.md` |
| Architect | Evaluates Gate 2, foresees cross-cutting impact, and redirects development when structural problems arise | — (structural authority within spec bounds) | Planner (Gate 2), Any blocked role | Planner (revision requests), Requesting role (directives), Human (escalation) | `.claude/agents/architect.md` |
| Implementer | Writes tests and production code using test-driven implementation | Test-Driven Implementation and Debugging | Task directory | Reviewer | `.claude/agents/implementer.md` |
| Reviewer | Reviews code for spec compliance and quality | Two-Stage Code Review | Implementer (via Development Loop) | Development Loop (verdict in task file) | `.claude/agents/reviewer.md` |
| Integrator | Resolves merge conflicts; manual merges into `dev`/`main` | Conflict Resolution | Integration Procedure (conflicts), Human (manual merges) | `dev` or `main` branch | `.claude/agents/integrator.md` |

## Procedures

| Procedure | Purpose | Used By | Implementation |
|---|---|---|---|
| Interactive Brainstorming | Explore solution space, evaluate trade-offs | Planner | `.claude/skills/brainstorm/SKILL.md` |
| Structured Task Decomposition | Decompose feature into atomic tasks | Planner | `.claude/skills/write-plan/SKILL.md` |
| Two-Stage Code Review | Two-stage review: spec compliance and code quality | Reviewer | `.claude/skills/code-review/SKILL.md` |
| Test-Driven Implementation | Write test first, verify failure, implement, verify pass | Implementer | `.claude/skills/tdd/SKILL.md` |
| Debugging | Reproduce, isolate, fix, verify | Implementer | `.claude/skills/debug/SKILL.md` |
| Integration Procedure | Merge task branch, run tests, promote task to completed | Development Loop (per-task) | `.claude/skills/integrate/SKILL.md` |
| Conflict Resolution | Resolve git merge conflicts | Integrator | `.claude/skills/conflict-resolution/SKILL.md` |

## Processes

| Process | Purpose | Started By | Implementation |
|---|---|---|---|
| Development Loop | Autonomous Implementer → Reviewer loop across all pending tasks | Human after Gate 2 passes | `.claude/skills/dev-loop/SKILL.md` |
| Bug-Fix Loop | Autonomous bug-fix loop across open bugs | Human when open bugs need resolution | `.claude/skills/bug-loop/SKILL.md` |

## Gates

| Gate | Purpose | Evaluator |
|---|---|---|
| Gate 1: Specification Approval | Confirm the specification is complete and aligned with the feature request | Human |
| Gate 2: Task Plan Preflight | Confirm the task plan is complete, conflict-aware, and implementation-ready | Architect |
| Gate 3: Code Review | Confirm task implementation satisfies the spec and quality bar | Reviewer |
| Gate 4: Integration Tests | Confirm merged work does not regress `dev` | Integration Procedure |
| Gate 5: Final Merge Sign-off | Confirm completed work matches spec intent before `dev` → `main` | Human |

## Documents and Directories

| Component | Type | Purpose | Location |
|---|---|---|---|
| Specifications | Directory | Feature and system specs | `project/specs/` |
| Task Board | Directory tree | Task lifecycle tracking | `project/tasks/{pending,in-progress,completed,blocked}/` |
| Bug Tracker | Directory tree | Bug lifecycle tracking | `project/bugs/{open,in-progress,resolved}/` |
| Decision Log | Directory | Architecture decision records | `project/decisions/` |
| Templates | Procedure assets | Reusable document formats | `.claude/skills/*/assets/` and `ai-process/templates/` |
| Process Docs | Directory | Workflow and procedure definitions | `ai-process/processes/` |
| Guidelines | Directory | Standards and checklists | `ai-process/guidelines/` |
| Architecture Docs | Directory | System design documentation | `ai-process/architecture/` |
| Action Procedures | Directory | Automation for document creation | `.claude/skills/` (with `disable-model-invocation: true`) |

## Interaction Diagram

```
Human ←──→ Planner ──→ Task Directory ──→ Implementer ──→ Reviewer ──→ Integrator ──→ Human
              ↑                              ↑    ↑           ↑             ↑
              │                              │    │           │             │
              └──────── Architect ───────────┴────┴───────────┴─────────────┘
                      (consulted on demand by any role)
```
