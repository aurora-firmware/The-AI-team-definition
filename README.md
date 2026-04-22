# The AI Team Definition

A reusable operating framework for projects developed by AI agent teams.

## What This Is

This is a **meta-project** — it does not contain software, it defines **how AI agent teams build software**.

At its core is the **ai-process**: a set of documents that describe the rules the AI team must follow — workflows, quality gates, coding standards, and role responsibilities.
Those rules are then **implemented** by the agents (`.claude/agents/`) and skills (`.claude/skills/`) that live alongside every project using this framework.

Think of it as a constitution for an AI development team.
The ai-process is the law; the agents and skills are the institutions that carry it out.

## The ai-process

The ai-process lives in `ai-process/` and has three layers:

| Layer | Folder | Defines |
|---|---|---|
| Workflows | `ai-process/processes/` | How work flows from idea to shipped feature: the full lifecycle of specs, tasks, bugs, and decisions, plus quality gates and escalation procedures |
| Standards | `ai-process/guidelines/` | How code, git history, and documents must be written: coding standards, review checklists, markdown conventions |
| Structure | `ai-process/architecture/` | How the AI team itself is organized: agent roles, skill boundaries, component responsibilities |

Everything in `ai-process/` is the **specification layer** — the authoritative source of truth.
The agents and skills in `.claude/` are the **implementation layer** — they must faithfully execute what the ai-process defines.

## Agent Roles

Each agent implements a distinct role defined in `ai-process/architecture/`:

| Agent | Responsibility |
|---|---|
| **Planner** | Turns approved specs into atomic, independent tasks |
| **Architect** | Designs systems, validates plans, unblocks structural problems |
| **Developer** | Writes tests and production code following TDD |
| **Reviewer** | Two-stage code review: spec compliance, then code quality |
| **Integrator** | Merges branches, runs integration tests, resolves conflicts |

## Skills

Skills are reusable procedures agents invoke for common activities.
Each skill implements a workflow or action defined in the ai-process:

| Skill | What it implements |
|---|---|
| **brainstorm** | Solution-space exploration before a spec is written |
| **write-plan** | Decomposition of a spec into atomic tasks |
| **tdd** | Test-driven development cycle |
| **code-review** | Two-stage review (spec compliance → code quality) |
| **debug** | Reproduce → gather evidence → isolate → fix → verify loop |
| **conflict-resolution** | Git conflict resolution preserving both sides' intent |
| **integrate** | Branch merge with test verification and task completion |
| **/dev-loop** | Autonomous Developer → Reviewer → Integrator loop across the pending task queue |
| **/bug-loop** | Autonomous diagnosis-first Developer → Reviewer loop across the open bug queue |
| **/new-spec** | Creates a new specification document from the template |
| **/new-task** | Creates a new task document from the template |
| **/new-bug** | Creates an evidence-backed bug report from the template |
| **/new-adr** | Creates a new Architecture Decision Record |
| **/status-report** | Summarizes current project state across all work items |

## Agent Platform Compatibility

Agent and skill definitions live in `.claude/` for Claude Code.
The `.codex/` directory contains symlinks to `.claude/agents/` and `.claude/skills/`, providing the same definitions to the OpenAI Codex agent platform without duplication.
Both platforms read from the same source files.

## Using This Framework in Your Project

Adopting the framework means copying its files into your new project repository and customizing them for your stack.
The full walkthrough is in `guides/setup-guide.md`.
The short version:

1. **Create the directory structure** — `project/specs/`, `project/tasks/`, `project/bugs/`, `project/decisions/`, `ai-process/`, `.claude/agents/`, `.claude/skills/`.
2. **Copy the framework files** — all agent definitions from `.claude/agents/`, all skill definitions from `.claude/skills/` (each as `<name>/SKILL.md`), and the process and guideline docs from `ai-process/`.
3. **Write your project's `CLAUDE.md`** — start from the template in `guides/setup-guide.md`, fill in your project name, purpose, and tech stack.
4. **Customize for your stack** — edit `ai-process/guidelines/coding-standards.md` for language-specific rules.
5. **Verify** — run `/status-report` (should produce an empty report) and `/new-task` (should create a file in `project/tasks/pending/`).

See `guides/setup-guide.md` for the complete file list, CLAUDE.md starter template, and verification steps.

## Repository Structure

```
├── ai-process/
│   ├── processes/       Workflow definitions, quality gates, escalation procedures
│   ├── guidelines/      Coding standards, review checklists, markdown conventions
│   └── architecture/    AI team structure: roles, components, boundaries
├── project/
│   ├── specs/           Feature specifications (with archive/ for superseded versions)
│   ├── tasks/           Task tracking (pending/ → in-progress/ → completed/ | blocked/)
│   ├── bugs/            Bug reports (open/ → in-progress/ → resolved/)
│   └── decisions/       Architecture Decision Records
├── guides/              Human-facing setup and customization guides
├── .claude/
│   ├── agents/          Agent role definitions (5 roles)
│   └── skills/          Skill procedures and action commands
└── .codex/              Symlinks to .claude/agents/ and .claude/skills/ (Codex compatibility)
```

## Contributing to This Project

Changes to the framework follow the same workflow the framework defines.

- **Changing a rule** (workflow, standard, convention): update `ai-process/` first, then update any agents or skills that implement the changed rule.
- **Changing an agent or skill**: verify that the change is consistent with — or explicitly revises — the relevant ai-process documents.
- **Architecture-affecting decisions**: record an ADR in `project/decisions/` before implementing.

The ai-process is the specification.
Agents and skills are the implementation.
Never let them contradict each other.
