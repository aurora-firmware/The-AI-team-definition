# The AI Team Definition

A comprehensive operating framework for projects developed entirely by AI agent teams.

## What This Is

This is a **meta-project**. It does not contain software — it defines **how AI agent teams should build software**. The output is a reusable set of:

- **Processes** — workflows, quality gates, escalation procedures
- **Templates** — specifications, tasks, bugs, decision records, test plans, roadmaps
- **Agent Definitions** — roles with clear responsibilities, authority, and interaction patterns
- **Skills** — reusable procedures agents follow for common activities (TDD, code review, debugging, etc.)

These artifacts are designed to be copied into any project repository and adapted to its specific needs.

## Repository Structure

```
├── project/specs/                   Technical specs (with archive/ for superseded versions)
├── project/tasks/                   Task tracking (pending/ → in-progress/ → completed/ | blocked/)
├── project/bugs/                    Bug reports (open/ → resolved/)
├── project/decisions/               Architecture Decision Records (ADRs)
├── ai-process/
│   ├── templates/           Reusable document formats not tied to a specific skill
│   ├── architecture/        System architecture of the AI team itself
│   ├── guidelines/          Coding standards, review checklists, markdown conventions
│   ├── guides/              Setup and customization guides
│   └── processes/           Workflow definitions, quality gates, escalation procedures
└── .claude/
    ├── agents/              Agent role definitions (6 roles)
    └── skills/              Skills: procedures (6) + action commands (6)
```

## Quick Start — Using This in Your Project

1. **Bootstrap**: In your new project repo, run `/bootstrap-project` to set up the full framework automatically.
2. **Customize**: Edit `CLAUDE.md` with your project name, tech stack, and conventions. See `ai-process/guides/customization-guide.md`.
3. **Start building**: Use `/new-spec` to write your first specification, then follow the workflow in `ai-process/processes/workflow-overview.md`.

For detailed manual setup, see `ai-process/guides/setup-guide.md`.

## Understanding the Layout

This repository has two distinct areas, each with a clear purpose:

### `ai-process/` — Framework (Generic, Read-Only)

These are the **reusable framework artifacts** that define how AI teams work. They are meant to be copied into any project and adapted minimally.

- **`processes/`** — Workflow definitions, quality gates, escalation procedures (applies to all projects)
- **`guidelines/`** — Coding standards, review checklists, markdown conventions (framework defaults)
- **`architecture/`** — System architecture diagrams and component maps (describes the AI team structure)
- **`guides/`** — Setup instructions and customization guidance for adopting the framework
- **`templates/`** — Reusable document formats (handoff notes, etc.)

**When adopting this framework in a new project**: Copy everything in `ai-process/` as-is. Only modify if you need language-specific conventions (edit `ai-process/guidelines/coding-standards.md`) or project-specific processes (document in `project/decisions/`).

### `project/` — Project Work (Project-Specific)

These directories hold the actual work artifacts for the project. This is where specifications, tasks, bugs, and decisions about your specific project live.

- **`tasks/`** — Feature work organized by status (pending → in-progress → completed)
- **`bugs/`** — Bug reports organized by status (open → in-progress → resolved)
- **`specs/`** — Feature specifications, with `archive/` for superseded versions
- **`decisions/`** — Architecture Decision Records (ADRs) specific to your project

**When working on a project**: All your work happens here. Create tasks, track bugs, write specs, and record decisions.

### `.claude/` — Agent Configuration (Framework)

Agent role definitions and skills live here (Claude Code requirement). Do not modify unless you're extending the framework with new agent types or skills.

## Quick Start — Working Within This Repo

1. Read `CLAUDE.md` for the full operating instructions.
2. Use skills to create documents: `/new-spec`, `/new-task`, `/new-bug`, `/new-adr`.
3. Run `/status-report` to get a summary of current project state.

## Agent Roles

| Agent | Responsibility |
|---|---|
| **Planner** | Breaks features into atomic, independent tasks |
| **Architect** | Designs systems, reviews failures, advises on structural issues |
| **Implementer** | Writes tests and production code using TDD |
| **Reviewer** | Two-stage code review: spec compliance, then code quality |
| **Integrator** | Merges branches, resolves conflicts, runs integration tests |

## Skills

| Skill | Purpose |
|---|---|
| **Brainstorm** | Explore solution space, evaluate trade-offs |
| **Write Plan** | Decompose features into atomic tasks with dependencies |
| **Code Review** | Two-stage review process (spec + quality) |
| **TDD** | Test-driven development flow |
| **Debug** | Reproduce, isolate, fix, verify |
| **Conflict Resolution** | Git conflict resolution preserving intent |

## Contributing

All contributions must follow the templates and conventions defined in `CLAUDE.md`. Architecture-affecting changes require an ADR in `project/decisions/`.
