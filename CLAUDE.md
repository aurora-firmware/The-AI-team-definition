# The AI Team Definition

> **This is a META-PROJECT.** Its output is processes, templates, agent definitions, and workflow structures — not software.

The **ai-process** is the authoritative description of the rules the AI team must follow.
The **skills** (`.claude/skills/`) and **agents** (`.claude/agents/`) are the *implementation* of those rules.
When they conflict, the ai-process wins.

---

## Repository Map

| Folder | Purpose |
|---|---|
| `project/` |  Placeholder for reference, expected in a project using the ai-process |
| `ai-process/architecture/` | System architecture documentation (skills and agents scope) |
| `ai-process/guidelines/` | Coding standards, review checklists, markdown conventions |
| `ai-process/processes/` | Workflow definitions, quality gates, escalation procedures |
| `guides/` | Human-facing guides for setup and customization (not part of the ai-process itself) |
| `.claude/agents/` | Agent role definitions (planner, architect, developer, reviewer, integrator) |
| `.claude/skills/` | Skills: procedures (brainstorm, write-plan, tdd, code-review, debug, conflict-resolution, integrate), orchestrators (/dev-loop, /bug-loop), and actions (/new-spec, /new-task, /new-bug, /new-adr, /status-report) |
| `.codex/` | Symlinks to `.claude/agents/` and `.claude/skills/` — compatibility layer for the OpenAI Codex agent platform |

---

## The Spec–Implementation Relationship

```
ai-process/          ← specification layer (the rules)
  processes/         defines workflows, gates, transitions
  guidelines/        defines coding, git, and markdown standards
  architecture/      describes the AI team's structure

.claude/             ← implementation layer (the executors)
  agents/            each agent implements a role defined in ai-process
  skills/            each skill implements a procedure defined in ai-process
```

**Reviewing this project** means checking that every agent and skill faithfully implements what the ai-process specifies.
**Changing this project** means either updating the ai-process first (the spec), then updating the agents/skills that implement the changed rules — or updating both atomically.
Never update an agent or skill in a way that contradicts the ai-process without also updating the ai-process.

---

## Framework vs Project-Specific Details

This repository defines a reusable process framework.
Its agents and skills must not hardcode details that belong to a consuming software project.

Do **not** put project-specific values in `.claude/agents/`, `.claude/skills/`, or `ai-process/`, including:
- Specific test commands such as `npm test`, `pytest`, `cargo test`, or project-specific CI commands.
- Specific build, run, dev-server, deploy, or package-manager commands.
- Stack-specific coding rules beyond the framework's general standards.
- Project-specific dependency policies, file layouts, naming conventions, or framework conventions.

Those details must be discovered from the target project when the framework is used there.
Agents and skills should instruct the model to read project-local sources such as the target project's `CLAUDE.md`, `project/docs/coding_guidelines.md`, README, package/build configuration, task verification commands, or human-provided instructions.

If a required project-specific command or rule cannot be found, the agent or skill should stop and ask for it rather than guessing or hardcoding a default in this repository.

---

## Agents vs Skills: What Goes Where

Agents are **roles** (who).
Skills are **procedures** (how).

### Agent files (`.claude/agents/`)

An agent file defines the **identity and authority** of a role — the context an AI model needs to act as that role.
It answers: *Who am I? What can I decide? When must I stop and escalate? What does "done" look like for my work?*

**An agent file SHOULD contain:**
- **Purpose** — one sentence defining the role.
- **Capabilities** — which tools and skills the agent has access to.
- **Decision authority** — what the agent can decide alone vs what it must escalate.
- **Escalation triggers** — conditions that require the agent to stop.
- **Interaction pattern** — who hands work to this agent and who receives work from it.
- **Quality bar** — output standards (what "done" looks like).

**An agent file MUST NOT contain:**
- Step-by-step procedures, numbered workflows, or conditional branching logic.
- Those belong in a skill, even if only one agent uses that skill.

An agent *references* skills ("use the `tdd` skill for implementation") but does not *describe* the procedure the skill follows.

### Skill files (`.claude/skills/`)

A skill file defines a **procedure** — a repeatable sequence of steps that any agent (or human) can invoke.
It answers: *What are the steps? In what order? What are the inputs and outputs? What can go wrong?*

**A skill file SHOULD contain:**
- **Steps** — numbered, deterministic sequence with clear inputs and outputs per step.
- **Quality criteria** — how to evaluate whether the procedure was followed correctly.
- **Anti-patterns / common pitfalls** — mistakes to avoid during execution.
- **Output format** — what the skill produces when complete.

**A skill file MUST NOT contain:**
- Role identity, decision authority, scope boundaries, or escalation thresholds.
- Those belong in the agent file of whichever role invokes the skill.

Skills fall into three categories:
- **Procedures** — analytical, multi-step work (brainstorm, write-plan, tdd, code-review, debug, conflict-resolution, integrate).
- **Orchestrators** — autonomous loops that spawn agents and drive workflows (dev-loop, bug-loop).
- **Actions** — simple document-creation operations (new-spec, new-task, new-bug, new-adr, status-report).

### The test

> If the content describes *what to do step by step*, it is a **skill**.
> If the content describes *who you are and what you're allowed to decide*, it is an **agent**.

---

## How to Work Here



---
