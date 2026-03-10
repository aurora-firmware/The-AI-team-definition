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
├── specifications/          Technical specs (with archive/ for superseded versions)
├── tasks/                   Task tracking (pending/ → in-progress/ → completed/ | blocked/)
├── bugs/                    Bug reports (open/ → resolved/)
├── decisions/               Architecture Decision Records (ADRs)
├── templates/               Roadmap, test plan/report, handoff notes, progress reports
├── docs/
│   ├── architecture/        System architecture of the AI team itself
│   ├── guidelines/          Coding standards, review checklists, markdown conventions
│   └── processes/           Workflow definitions, quality gates, escalation procedures
└── .claude/
    ├── agents/              Agent role definitions (6 roles)
    └── skills/              Skills: procedures (6) + action commands (6)
```

## Quick Start — Using This in Your Project

1. **Bootstrap**: In your new project repo, run `/bootstrap-project` to set up the full framework automatically.
2. **Customize**: Edit `CLAUDE.md` with your project name, tech stack, and conventions. See `docs/guides/customization-guide.md`.
3. **Start building**: Use `/new-spec` to write your first specification, then follow the workflow in `docs/processes/workflow-overview.md`.

For detailed manual setup, see `docs/guides/setup-guide.md`.

## Quick Start — Working Within This Repo

1. Read `CLAUDE.md` for the full operating instructions.
2. Use skills to create documents: `/new-spec`, `/new-task`, `/new-bug`, `/new-adr`.
3. Run `/status-report` to get a summary of current project state.

## Agent Roles

| Agent | Responsibility |
|---|---|
| **Planner** | Breaks features into atomic, parallelizable tasks |
| **Architect** | Designs systems, reviews failures, advises on structural issues |
| **Implementer** | Writes production code following assigned skills |
| **Reviewer** | Two-stage code review: spec compliance, then code quality |
| **Tester** | Writes tests, runs suites, reports results and coverage |
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

All contributions must follow the templates and conventions defined in `CLAUDE.md`. Architecture-affecting changes require an ADR in `decisions/`.
