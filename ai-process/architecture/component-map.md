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
| Planner | Creates specifications with the human, then decomposes approved specifications into executable tasks | Interactive Brainstorming; Structured Task Decomposition | Human | Human (approval), Task directory (`pending/`), Architect (Gate 2) | `.claude/agents/planner.md` |
| Architect | Owns structural review: Gate 2 preflight, architectural consistency, escalation analysis, and ADR decisions | Gate 2 Preflight; Escalation Consultation; New ADR | Planner (Gate 2), Any blocked role | Planner (revision requests), Requesting role (directives), Human (escalation), Decision Log | `.claude/agents/architect.md` |
| Developer | Implements tasks and fixes bugs; diagnoses bugs before changing production code | Test-Driven Implementation; Diagnostic Debugging | Development Loop or Bug-Fix Loop | Reviewer | `.claude/agents/developer.md` |
| Reviewer | Reviews task acceptance, bug diagnosis, targeted fixes, verification evidence, and code quality | Two-Stage Code Review | Developer (via Development Loop or Bug-Fix Loop) | Development Loop or Bug-Fix Loop (verdict in task or bug file) | `.claude/agents/reviewer.md` |
| Integrator | Resolves merge conflicts; supports task and bug integration into target branches and human-controlled final merge | Integration Procedure; Conflict Resolution | Development Loop or Bug-Fix Loop (integration), Human (manual merges), Integration Procedure (conflicts) | `dev-agent`, preserved task branch, or `main` branch | `.claude/agents/integrator.md` |

## Procedures

| Procedure | Purpose | Used By | Implementation |
|---|---|---|---|
| Interactive Brainstorming | Explore the request, alternatives, constraints, and prior decisions before writing a specification | Planner | `.claude/skills/brainstorm/SKILL.md` |
| Structured Task Decomposition | Decompose an approved specification into atomic tasks with dependencies, acceptance criteria, and verification | Planner | `.claude/skills/write-plan/SKILL.md` |
| Gate 2 Preflight | Validate task dependencies, file conflict risk, decision-record consistency, atomicity, and implementation readiness | Architect | `.claude/skills/gate-2-preflight/SKILL.md` |
| Test-Driven Implementation | Write a failing test, verify failure, implement the minimal change, verify pass, and refactor | Developer | `.claude/skills/tdd/SKILL.md` |
| Diagnostic Debugging | Reproduce or confirm a defect, gather evidence, isolate the fault, record a root-cause hypothesis, then permit fixing | Developer | `.claude/skills/debug/SKILL.md` |
| Two-Stage Code Review | Review tasks for acceptance compliance and bugs for diagnosis, root-cause fit, verification, and code quality | Reviewer | `.claude/skills/code-review/SKILL.md` |
| Integration Procedure | Merge task or bug branches, run pre- and post-merge tests, promote completed work, and file regression bugs on failure | Development Loop, Bug-Fix Loop, Integrator | `.claude/skills/integrate/SKILL.md` |
| Conflict Resolution | Resolve git merge conflicts while preserving both sides' intent | Integrator | `.claude/skills/conflict-resolution/SKILL.md` |
| Escalation Consultation | Analyse blocked work after role self-recovery and issue guidance or escalate to human | Architect | `.claude/skills/escalation-consultation/SKILL.md` |
| New Specification | Create a specification document from the standard template | Planner | `.claude/skills/new-spec/SKILL.md` |
| New Task | Create a task file in `project/tasks/pending/` from the standard template | Planner | `.claude/skills/new-task/SKILL.md` |
| New Bug | Create an evidence-rich bug report in `project/bugs/open/` from the standard template | Human, Developer, Reviewer, Integration Procedure | `.claude/skills/new-bug/SKILL.md` |
| New ADR | Create an architecture decision record in `project/decisions/` from the standard template | Architect | `.claude/skills/new-adr/SKILL.md` |
| Status Report | Summarize specifications, tasks, bugs, decisions, and integration state for Gate 5 | Development Loop, Bug-Fix Loop, Human | `.claude/skills/status-report/SKILL.md` |

## Processes

| Process | Purpose | Started By | Implementation |
|---|---|---|---|
| Development Loop | Autonomous task loop across `project/tasks/pending/`: Developer → Reviewer → Integration until the queue is empty, blocked, or escalated | Human after Gate 2 passes | `.claude/skills/dev-loop/SKILL.md` |
| Bug-Fix Loop | Diagnosis-first bug loop across `project/bugs/open/`: Diagnostic Debugging → implementation → Reviewer → Integration until the queue is empty or escalated | Human when open bugs need resolution | `.claude/skills/bug-loop/SKILL.md` |

## Gates

| Gate | Purpose | Evaluator |
|---|---|---|
| Gate 1: Specification Approval | Confirm the specification is complete and aligned with the feature request | Human |
| Gate 2: Task Plan Preflight | Confirm the task plan is complete, conflict-aware, and implementation-ready | Architect |
| Gate 3: Code Review | Confirm task implementations satisfy acceptance criteria and bug fixes include sound diagnosis, targeted fix, verification, and quality | Reviewer |
| Gate 4: Integration Tests | Confirm merged task or bug work does not regress the target branch | Integration Procedure |
| Gate 5: Final Merge Sign-off | Confirm completed work matches spec intent before `dev-agent` → `main` | Human |

## Documents and Directories

| Component | Type | Purpose | Location |
|---|---|---|---|
| Specifications | Directory | Feature and system specs | `project/specs/` |
| Task Board | Directory tree | Task lifecycle tracking | `project/tasks/{pending,in-progress,completed,blocked}/` |
| Bug Tracker | Directory tree | Bug lifecycle tracking | `project/bugs/{open,in-progress,resolved}/` |
| Decision Log | Directory | Architecture decision records | `project/decisions/` |
| Templates | Procedure assets | Reusable document formats | `.claude/skills/*/assets/` |
| Process Docs | Directory | Workflow and procedure definitions | `ai-process/processes/` |
| Guidelines | Directory | Standards and checklists | `ai-process/guidelines/` |
| Architecture Docs | Directory | System design documentation | `ai-process/architecture/` |
| Action Procedures | Directory | Automation for document creation and status reporting | `.claude/skills/` (with `disable-model-invocation: true` where no model reasoning is needed) |

## Interaction Diagram

```
Human ←──→ Planner ──→ Task Directory ──→ Development Loop ──→ Developer ──→ Reviewer ──→ Integration ──→ Human
   │          │                                  │                  ↑             │              ↑
   │          ↓                                  │                  │             │              │
   │     Architect ←──────── escalation ─────────┴──────────────────┴─────────────┘              │
   │          │                                                                                 │
   │          ↓                                                                                 │
   │     Decision Log                                                                           │
   │                                                                                            │
   └────────→ Bug Tracker ──→ Bug-Fix Loop ──→ Diagnostic Debugging ──→ Developer ──→ Reviewer ─┘
```
