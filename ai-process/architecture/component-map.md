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
| Planner | Creates specifications with the human, then decomposes approved specifications into executable tasks | Brainstorm; Spec Breakdown | Human | Human (approval), Task directory (`pending/`), Architect (Gate 2; Architecture Consistency Review for created/changed specs and change-requests) | `.claude/agents/planner.md` |
| Architect | Owns structural review: Gate 2 preflight, architectural consistency, escalation analysis, and ADR decisions | Spec Breakdown Review; Architecture Consistency Review; Escalation Review; New ADR | Planner (Gate 2; Architecture Consistency Review for created/changed specs and change-requests), Any blocked role | Planner (revision requests, consistency findings), Requesting role (directives), Human (escalation), Decision Log | `.claude/agents/architect.md` |
| Developer | Implements tasks and fixes bugs; diagnoses bugs before changing production code | TDD; Debug | Development Loop or Bug-Fix Loop | Reviewer | `.claude/agents/developer.md` |
| Reviewer | Reviews task acceptance, bug diagnosis, targeted fixes, verification evidence, and code quality | Code Review | Developer (via Development Loop or Bug-Fix Loop) | Development Loop or Bug-Fix Loop (verdict in task or bug file) | `.claude/agents/reviewer.md` |
| Integrator | Resolves merge conflicts; supports task and bug integration into target branches and human-controlled final merge | Integrate; Merge Conflicts | Development Loop or Bug-Fix Loop (integration), Human (manual merges), Integrate (conflicts) | `dev-agent`, preserved task branch, or `main` branch | `.claude/agents/integrator.md` |

## Procedures

| Procedure | Purpose | Used By | Implementation |
|---|---|---|---|
| Brainstorm | Explore the request, alternatives, constraints, and prior decisions before writing a specification | Planner | `.claude/skills/brainstorm/SKILL.md` |
| Change Request (intake) | Capture smaller desired changes and possible spec amendments without the full brainstorm-to-spec flow; produces tasks and amendments as needed | Planner, Human | `ai-team change-request new`; template at `cli/src/ai_team/templates/change-request.md`; artifacts stored in `project/change-requests/` |
| Spec Breakdown | Decompose an approved specification into atomic tasks with dependencies, acceptance criteria, and verification | Planner | `.claude/skills/spec-breakdown/SKILL.md` |
| Spec Breakdown Review | Validate task dependencies, file conflict risk, decision-record consistency, atomicity, and implementation readiness (evaluates Gate 2) | Architect | `.claude/skills/spec-breakdown-review/SKILL.md` |
| Architecture Consistency Review | Check a created or changed spec, ADR, or change-request against every approved spec and accepted ADR, and route amendments for any drift | Architect | `.claude/skills/architecture-consistency-review/SKILL.md` |
| TDD | Write a failing test, verify failure, implement the minimal change, verify pass, and refactor | Developer | `.claude/skills/tdd/SKILL.md` |
| Debug | Reproduce or confirm a defect, gather evidence, isolate the fault, record a root-cause hypothesis, then permit fixing | Developer | `.claude/skills/debug/SKILL.md` |
| Code Review | Review tasks for acceptance compliance and bugs for diagnosis, root-cause fit, verification, and code quality | Reviewer | `.claude/skills/code-review/SKILL.md` |
| Integrate | Merge task or bug branches, run pre- and post-merge tests, promote completed work, and file regression bugs on failure | Development Loop, Bug-Fix Loop, Integrator | `.claude/skills/integrate/SKILL.md` |
| Merge Conflicts | Resolve git merge conflicts while preserving both sides' intent | Integrator | `.claude/skills/merge-conflicts/SKILL.md` |
| Escalation Review | Analyse blocked work after role self-recovery and issue guidance or escalate to human | Architect | `.claude/skills/escalation-review/SKILL.md` |
| New Specification | Create a specification document from the standard template | Planner | `.claude/skills/new-spec/SKILL.md` |
| New Task | Create a task file in `project/tasks/pending/` from the standard template | Planner | `.claude/skills/new-task/SKILL.md` |
| New Bug | Create an evidence-rich bug report in `project/bugs/open/` from the standard template | Human, Developer, Reviewer, Integrate | `.claude/skills/new-bug/SKILL.md` |
| New ADR | Create an architecture decision record in `project/decisions/` from the standard template | Architect | `.claude/skills/new-adr/SKILL.md` |
| Status Report | Summarize specifications, tasks, bugs, decisions, and integration state for Gate 5 | Development Loop, Bug-Fix Loop, Human | `.claude/skills/status-report/SKILL.md` |

## Processes

| Process | Purpose | Started By | Implementation |
|---|---|---|---|
| Development Loop | Autonomous task loop across `project/tasks/pending/`: Developer → Reviewer → Integration until the queue is empty, blocked, or escalated | Human after Gate 2 passes | `.claude/skills/dev-loop/SKILL.md` |
| Bug-Fix Loop | Diagnosis-first bug loop across `project/bugs/open/`: Debug → implementation → Reviewer → Integrate until the queue is empty or escalated | Human when open bugs need resolution | `.claude/skills/bug-loop/SKILL.md` |

## Gates

| Gate | Purpose | Evaluator |
|---|---|---|
| Gate 1: Specification Approval | Confirm the specification is complete and aligned with the feature request | Human |
| Gate 2: Task Plan Preflight | Confirm the task plan is complete, conflict-aware, and implementation-ready | Architect |
| Gate 3: Code Review | Confirm task implementations satisfy acceptance criteria and bug fixes include sound diagnosis, targeted fix, verification, and quality | Reviewer |
| Gate 4: Integration Tests | Confirm merged task or bug work does not regress the target branch | Integrate |
| Gate 5: Final Merge Sign-off | Confirm completed work matches spec intent before `dev-agent` → `main` | Human |

## Documents and Directories

| Component | Type | Purpose | Location |
|---|---|---|---|
| Specifications | Directory | Feature and system specs | `project/specs/` |
| Change Requests | Directory | Lightweight intake artifacts for smaller changes; produced by `ai-team change-request new` | `project/change-requests/` |
| Task Board | Directory tree | Task lifecycle tracking | `project/tasks/{pending,in-progress,completed,blocked}/` |
| Bug Tracker | Directory tree | Bug lifecycle tracking | `project/bugs/{open,in-progress,resolved}/` |
| Decision Log | Directory | Architecture decision records | `project/decisions/` |
| Root Guidance Files | Files | Project-level command documentation for autonomous agents; `## Test` section is the canonical home for the baseline test command consumed by `dev-loop` | `CLAUDE.md` and `AGENTS.md` at the project root; scaffolded by `ai-team init` from templates in `cli/src/ai_team/init/sources/root/` |
| Project Guidance Files | Files | Artifact directory orientation for agents; always generated by `ai-team init` | `project/CLAUDE.md` and `project/AGENTS.md`; scaffolded from `cli/src/ai_team/init/sources/project/` |
| Templates | Procedure assets | Reusable document formats | `.claude/skills/*/assets/` |
| Process Docs | Directory | Workflow and procedure definitions (spec layer only — not exported by `ai-team init`) | `ai-process/processes/` |
| Guidelines | Directory | Standards and checklists (spec layer only — not exported by `ai-team init`) | `ai-process/guidelines/` |
| Architecture Docs | Directory | System design documentation (spec layer only — not exported by `ai-team init`) | `ai-process/architecture/` |
| Action Procedures | Directory | Automation for document creation and status reporting | `.claude/skills/` (`disable-model-invocation: true` only for human-only actions that no other skill invokes) |
| CLI Scaffold Sources | Package assets | Authoritative source for agents, skills, and templates exported by `ai-team init`; also the input to the `pi` sync target | `cli/src/ai_team/init/sources/` |

## CLI Command Mapping

Action skills that create or report on project artifacts invoke `ai-team` CLI commands. The table below maps each action skill to the command(s) it calls.

| Skill | CLI Command(s) | Purpose |
|---|---|---|
| `new-spec` | `ai-team spec new` | Create a new specification document |
| `new-task` | `ai-team task new` | Create a new task file in `project/tasks/pending/` |
| `new-bug` | `ai-team bug new` | Create a new bug report in `project/bugs/open/` |
| `new-adr` | `ai-team adr new` | Create a new architecture decision record in `project/decisions/` |
| `status-report` | `ai-team status`, `ai-team report` | Generate inline Gate 5 summary and full progress report |
| *(change-request intake)* | `ai-team change-request new` | Create a change-request document in `project/change-requests/` |

## Pi Extension Components

The pi extension delivers the same artifact actions to pi sessions as a single `ai_team` tool. It is a second implementation of the CLI's artifact behaviour, co-equal with the Python CLI (ADR-004), not a wrapper around it. All paths are repo-relative.

| Component | Owning path | Interface | Notes |
|---|---|---|---|
| Pi package | `pi/` | npm package manifest declaring the extension entry and the non-orchestrator skills; loaded by pi from a local path | Sits beside `cli/`. Pi host packages are peer dependencies. Carries the TypeScript toolchain (type check, vitest). |
| Scaffold sync `pi` target | `cli/scripts/sync_init_scaffolds.py` | Consumes skill sources, templates, project skeleton, root guidance sources, and the command map; produces `pi/resources/` | Third target beside `claude` and `codex`. Renders `{{ai-team ...}}` markers verbatim for claude/codex and as `ai_team` tool instructions for pi. Derives pi skill headers from `[claude]` (ADR-002). Fails on unknown commands, flags, or unrenderable markers. |
| Pi resources | `pi/resources/` | Generated skills, artifact templates, project skeleton (including its `.gitignore`), root guidance templates, claude/codex scaffold directory list for `check-layout`, the command map | Generated, never hand-edited. Regenerate with the sync. |
| Pi version file | `pi/resources/` (git-ignored) | Carries the `ai-team` distribution version; read by the TS `init` and `check-layout` | Written by the sync. The command map holds no version. The package fails to load if it is missing. |
| Command map | one maintained table, consumed by the sync and the TS schema | Maps each CLI leaf command, its arguments and flags, to an `ai_team` tool `command` value and field names | See "Pi Tool Command Mapping" below. Single place that changes when the CLI gains or changes a command. |
| Pi adapter | `pi/src/` (extension entry) | Registers the `ai_team` tool; validates input, resolves the project root from the session cwd, shapes results and errors, rewrites binary-pointing hints into tool instructions | The only component that imports the pi API. |
| TS artifact core | `pi/src/` (pure core modules) | One handler per command: resolved project root and typed input in, structured result out. Injectable clock and version | One-to-one port of the Python core. Owns models, IDs, locking, filesystem, locator, layout, validation, templates. |
| Parity fixtures | `fixtures/parity/` | Cases declaring command, clock, version, before tree, after tree, exit status, and structured result | Repo-level contract owned by neither implementation (ADR-004). |
| Fixture runners | pytest runner under `cli/tests/`; vitest runner under `pi/` | Each auto-discovers and executes every fixture case against one implementation | Both must pass. A behaviour change updates the fixtures, then both implementations. |
| Python CLI (amended) | `cli/src/ai_team/` | Internal structured result per command (separate message and hint fields); injectable clock and version | stdout, stderr, exit codes, and flags unchanged. |
| ID-allocation locks | Python: `<project_dir>/.ai-team.lock` (`flock`); TS: its own lock path inside the project artifact directory | Each implementation locks only against itself | ADR-003. Mixed concurrent allocation (a Python process and a pi session in the same working tree) is unsupported. The project skeleton `.gitignore` lists both lock paths. |

### Generation Flow

```
skill sources + templates + skeleton + command map
        -> sync_init_scaffolds.py (claude | codex | pi)
        -> pi/resources/ (generated)
        -> pi adapter (ai_team tool)
        -> TS artifact core -> artifact tree

fixtures/parity/ -> pytest runner -> Python CLI
fixtures/parity/ -> vitest runner -> TS artifact core
```

`pi/resources/` is generated output and must never be hand-edited; change the sources and re-run the sync. The `claude` and `codex` exports are unchanged by the `pi` target, apart from the deliberate TS lock entry in the project skeleton `.gitignore`.

## Pi Tool Command Mapping

The `ai_team` tool accepts one command per call. Command names are the CLI's leaf command paths, space-separated; positional arguments become named fields and flags become camelCase fields. The tool never takes a `json` field.

| CLI command | `ai_team` `command` | Fields |
|---|---|---|
| `ai-team spec new` | `spec new` | `title`; optional `author`, `status` |
| `ai-team task new` | `task new` | `title`; optional `priority`, `assignedRole`, `spec` |
| `ai-team task start` / `complete` / `unblock` | `task start` / `task complete` / `task unblock` | `id` |
| `ai-team task block` | `task block` | `id`, `reason` |
| `ai-team bug new` | `bug new` | `title`; optional `severity`, `task` |
| `ai-team bug start` / `resolve` | `bug start` / `bug resolve` | `id` |
| `ai-team adr new` | `adr new` | `title`; optional `status`, `supersedes` |
| `ai-team change-request new` | `change-request new` | `title` |
| `ai-team list <kind>` | `list tasks` / `list bugs` / `list specs` / `list adrs` / `list change-requests` | optional `state` (not for change-requests) |
| `ai-team show` | `show` | `identifier` |
| `ai-team status` | `status` | none |
| `ai-team report` | `report` | optional `out` |
| `ai-team validate` | `validate` | optional `all`, `tasks`, `bugs`, `specs`, `adrs`, `changeRequests` |
| `ai-team archive` | `archive` | optional `olderThan`, `dryRun` |
| `ai-team check-layout` | `check-layout` | none |
| `ai-team init` | `init` | optional `path`, `force`, `dryRun`, `createRootGuidance`; omits `--tools` and `--no-interactive` |

The S-005 spec holds the full tool contract; the command map is the single place that changes when the CLI does.

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
   └────────→ Bug Tracker ──→ Bug-Fix Loop ──→ Debug ──→ Developer ──→ Reviewer ─┘
```
