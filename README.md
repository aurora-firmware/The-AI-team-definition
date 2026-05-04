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

## Process Overview

```text
                         +----------------------+
                         |        Human         |
                         +----------+-----------+
                                    |
                                    v
        +------------------- Spec + Planning Process -------------------+
        |                                                               |
        |  Feature request -> Planner brainstorm -> Specification       |
        |                         |                                     |
        |                         v                                     |
        |                  Gate 1: human approval                       |
        |                         |                                     |
        |                         v                                     |
        |             Planner task plan -> Gate 2: Architect            |
        |                         |                                     |
        +-------------------------+-------------------------------------+
                                  |
                                  v
        +---------------- Development Loop (/dev-loop) -----------------+
        |                                                               |
        |  pending task -> Developer -> Reviewer -> Integration         |
        |                     ^           |              |              |
        |                     |           | FAIL         | regression   |
        |                     +-----------+              v              |
        |                                      bug report in open/      |
        +-------------------------+---------------------+---------------+
                                  |                     |
                                  | queue empty         | bugs exist
                                  v                     v
        +---------------- Final Sign-off --------+   +-- Bug Loop (/bug-loop) --+
        |                                        |   |                          |
        |  status report -> Gate 5: Human        |   | diagnose -> fix ->       |
        |  approves dev-agent -> main            |   | review -> integrate      |
        |                                        |   |            ^             |
        +----------------------------------------+   |            | FAIL        |
                                                     +------------+-------------+

        Escalation path for blocked work:
        Developer / Reviewer / Integrator / Loop -> Architect -> Human
```

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
| **spec-breakdown** | Decomposition of a spec into atomic tasks |
| **spec-breakdown-review** | Architect validation of task plans before development starts |
| **tdd** | Test-driven development cycle |
| **debug** | Diagnosis-first debugging: reproduce or confirm, gather evidence, isolate, then fix |
| **code-review** | Two-stage review: task or bug criteria, then code quality |
| **merge-conflicts** | Git conflict resolution preserving both sides' intent |
| **integrate** | Branch merge with project-discovered verification and task completion |
| **escalation-review** | Architect analysis for blocked work before human escalation |
| **/dev-loop** | Autonomous Developer → Reviewer → Integration loop across the pending task queue |
| **/bug-loop** | Autonomous diagnosis-first Developer → Reviewer → Integration loop across the open bug queue |
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

Adopting the framework means copying its process, agent, skill, and template files into your project repository, then adding project-local guidance for your stack and commands.
The full walkthrough is in `guides/setup-guide.md`.
The short version:

1. **Create the directory structure** — `project/specs/`, `project/tasks/`, `project/bugs/`, `project/decisions/`, `ai-process/`, `.claude/agents/`, `.claude/skills/`, and project-local docs such as `project/docs/`.
2. **Copy the framework files** — all agent definitions from `.claude/agents/`, all skill definitions from `.claude/skills/`, and the process, guideline, and architecture docs from `ai-process/`.
3. **Write your project's `CLAUDE.md`** — document project purpose, repository layout, stack, build/run/test/lint commands, and where project-specific rules live.
4. **Add project-local guidance** — put stack-specific coding rules in `project/docs/coding_guidelines.md` or another project-local document referenced by `CLAUDE.md`; keep the copied framework files generic unless you intentionally fork the process.
5. **Configure permissions** — create `.claude/settings.json` for the commands and tools agents may use in this project.
6. **Verify** — run `/status-report` (should produce an empty report) and `/new-task` (should create a file in `project/tasks/pending/`).

The normal workflow is:

1. Human and Planner shape a specification; human approves it at Gate 1.
2. Planner decomposes the approved spec into tasks.
3. Architect validates the task plan at Gate 2.
4. Human starts `/dev-loop`; Gate 3 code review and Gate 4 integration run inside the loop.
5. Bugs are filed in `project/bugs/open/` and handled through `/bug-loop`.
6. Human approves the final `dev-agent` → `main` merge at Gate 5.

See `guides/setup-guide.md` for the complete file list, CLAUDE.md starter template, and verification steps.

## Guides

| Guide | Purpose |
|---|---|
| [`guides/setup-guide.md`](guides/setup-guide.md) | Step-by-step walkthrough for bootstrapping a new project with the framework |
| [`guides/customization-guide.md`](guides/customization-guide.md) | What to adapt when tailoring the framework to your project's stack and conventions |
| [`guides/agent_template.md`](guides/agent_template.md) | Canonical template and rules for writing new agent definitions |
| [`guides/skill_template.md`](guides/skill_template.md) | Canonical template and rules for writing new skill definitions |

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
│   ├── decisions/       Architecture Decision Records
│   └── docs/            Project-specific commands, coding conventions, and operations
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
