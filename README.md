# The AI Team Definition

A reusable operating framework for projects developed by AI agent teams.

## What This Is

This is a **meta-project** — it defines **how AI agent teams build software**.

At its core is the **ai-process**: a set of documents that describe the rules the AI team must follow — workflows, quality gates, coding standards, and role responsibilities.
Those rules are then **implemented** by three things that live alongside every project using this framework:

- the **agents** (`.claude/agents/`) — the roles that carry out the process;
- the **skills** (`.claude/skills/`) — the procedures the agents follow;
- the **`ai-team` CLI** (`cli/`) — the tooling that supports the skills by managing project artifacts and bootstrapping the framework into new repositories.

Think of it as a constitution for an AI development team.
The ai-process is the law; the agents, skills, and CLI are the institutions that carry it out.

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
| **/new-spec** | Creates a specification by invoking `ai-team spec new`, then fills spec content |
| **/new-task** | Creates a pending task by invoking `ai-team task new` |
| **/new-bug** | Creates an evidence-backed bug report by invoking `ai-team bug new`, then fills bug content |
| **/new-adr** | Creates an Architecture Decision Record by invoking `ai-team adr new`, then fills ADR content |
| **/status-report** | Summarizes project state by invoking `ai-team status` and writes a report with `ai-team report` |

## Agent Platform Compatibility

Agent and skill definitions live in `.claude/` for Claude Code.
The `.codex/` directory provides OpenAI Codex compatibility with project-scoped agent TOML files and a symlinked `.codex/skills` view of `.claude/skills/`.
Skills stay shared from the same source files.

## Using This Framework in Your Project

Adopting the framework means installing the `ai-team` CLI, using it to scaffold the process files into your project, then adding project-local guidance for your stack and commands.
The full walkthrough is in `guides/setup-guide.md`.
For a narrated usage guide see [`cli/docs/usage.md`](cli/docs/usage.md); for an exhaustive command and flag reference see [`cli/docs/commands.md`](cli/docs/commands.md).

### Install the CLI

Install from PyPI once published:

```bash
pipx install ai-team-cli
```

For a local build from this repository:

```bash
cd cli
python scripts/sync_init_scaffolds.py  # use python3 if your shell has no python shim
uv build
pipx install --force dist/*.whl
```

### Initialize a Project

From the target repository root:

```bash
ai-team init . --tools claude --no-interactive
```

This creates the empty `project/` state folders, copies the bundled `.claude/agents/` and `.claude/skills/`, and writes `.ai-team.toml`.
To also copy the process specification documents, add `--include-ai-process`:

```bash
ai-team init . --tools claude --include-ai-process --no-interactive
```

Use `--dry-run` to preview files before writing, and `--force` only when you intentionally want existing files overwritten.

### Daily CLI Commands

The CLI manages project artifacts directly:

```bash
ai-team status
ai-team list tasks
ai-team show T-001
ai-team task new "Add onboarding flow" --priority high --assigned-role developer
ai-team task start T-001
ai-team task complete T-001
ai-team bug new "Login crashes on empty token" --severity high
ai-team bug start B-001
ai-team bug resolve B-001
ai-team spec new "Billing reconciliation" --author "Team"
ai-team adr new "Use PostgreSQL for ledger storage"
ai-team validate
ai-team report
ai-team archive --older-than 90d --dry-run
```

The action skills use those commands internally. For example, `/new-task` delegates file creation to `ai-team task new`, `/new-bug` delegates to `ai-team bug new`, and `/status-report` delegates to `ai-team status` plus `ai-team report`.

The most common loop is:

1. Create or approve a spec.
2. Create tasks in `project/tasks/pending/`.
3. Run `/dev-loop` to implement, review, integrate, and complete tasks.
4. Run `/bug-loop` for open bugs.
5. Run `ai-team status` and `ai-team report` for Gate 5 sign-off context.

After initialization, still add your project's `CLAUDE.md`, stack-specific commands, and coding guidance in `project/docs/`.
Keep the framework files generic unless you intentionally fork the process.

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
├── cli/                 `ai-team` CLI package and bundled init scaffolds
├── .claude/
│   ├── agents/          Agent role definitions (5 roles)
│   └── skills/          Skill procedures and action commands
└── .codex/              Codex agent TOML files and symlinked skills compatibility
```

## Contributing to This Project

Changes to the framework follow the same workflow the framework defines.

- **Changing a rule** (workflow, standard, convention): update `ai-process/` first, then update any agents or skills that implement the changed rule.
- **Changing an agent or skill**: verify that the change is consistent with — or explicitly revises — the relevant ai-process documents.
- **Changing bundled init content**: update the source files, then run `python cli/scripts/sync_init_scaffolds.py` so `ai-team init` ships the same content.
- **Architecture-affecting decisions**: record an ADR in `project/decisions/` before implementing.

The ai-process is the specification.
Agents and skills are the implementation.
Never let them contradict each other.
