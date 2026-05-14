# The AI Team Definition

> **This is a META-PROJECT.** Its output is the ai-process (the rules), the agents and skills that implement those rules, and the `ai-team` CLI that supports the skills by managing project artifacts.

The **ai-process** is the authoritative description of the rules the AI team must follow.
The **skills** (`.claude/skills/`) and **agents** (`.claude/agents/`) are the *implementation* of those rules.
The **`ai-team` CLI** (`cli/`) is the *tooling* the action skills invoke to scaffold, move, and report on project artifacts.
When they conflict, the ai-process wins.

---

## Repository Map

| Folder | Purpose |
|---|---|
| `project/` | Placeholder for reference, expected in a project using the ai-process |
| `ai-process/architecture/` | System architecture documentation (skills and agents scope) |
| `ai-process/guidelines/` | Coding standards, review checklists, markdown conventions |
| `ai-process/processes/` | Workflow definitions, quality gates, escalation procedures |
| `guides/` | Human-facing guides for setup and customization (not part of the ai-process itself) |
| `cli/` | The `ai-team` CLI package — manages project artifacts and bootstraps the framework into new repositories; the action skills invoke it instead of carrying their own scripts and templates |
| `.claude/agents/` | Agent role definitions (planner, architect, developer, reviewer, integrator) |
| `.claude/skills/` | Skills: procedures (brainstorm, spec-breakdown, tdd, code-review, debug, merge-conflicts, integrate, escalation-review, spec-breakdown-review), orchestrators (/dev-loop, /bug-loop), and actions (/new-spec, /new-task, /new-bug, /new-adr, /status-report, /git-conventions) |
| `.codex/` | OpenAI Codex compatibility layer: project-scoped custom agents in `.codex/agents/*.toml` plus a symlinked `.codex/skills/` view of `.claude/skills/` |

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

cli/                 ← tooling layer (supports the skills)
  ai-team            manages project artifacts; the action skills invoke it
```

**Reviewing this project** means checking that every agent and skill faithfully implements what the ai-process specifies, and that the CLI stays consistent with the artifact lifecycle the ai-process defines.
**Changing this project** means either updating the ai-process first (the spec), then updating the agents/skills that implement the changed rules — or updating both atomically.
Never update an agent or skill in a way that contradicts the ai-process without also updating the ai-process.

### `.claude/` must be self-contained

The `.claude/` folder must not reference paths under `ai-process/`. The spec layer documents the *intent* of the rules; the implementation layer must *embed* the rules so that an agent or skill can execute without reading outside `.claude/`.

When an ai-process rule applies:

- **If a single agent uses it** → embed it in that agent's `## Quality Bar` (example: coding standards in `developer.md`, review checklist in `reviewer.md`).
- **If multiple agents or skills use it** → extract it as its own skill and have callers reference the skill by name (example: `git-conventions/SKILL.md` is invoked from `integrate`, `code-review`, `dev-loop`, and `bug-loop`).
- **Do not duplicate content across `.claude/` files.** Duplication causes drift. Either pick a single owning file and cross-reference, or extract to a skill.

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

**An agent file MUST contain** these nine sections, in this order:

1. `## Purpose` — one short paragraph naming the role and its outcome.
2. `## Inputs` — one-line pointer to the frontmatter description plus the `BLOCKED` fallback.
3. `## Skills` — list of skills this agent invokes and when.
4. `## Decision Authority` — a `### Can Decide Alone` sub-list. The Planner may also have an `### Ask the Human` sub-list.
5. `## Escalation` — one paragraph pointing at the skill(s) that own thresholds and trigger conditions. **No retry counts, no boundary-violation lists here** — those live in the skill.
6. `## Interaction Pattern` — `### Spawned By` and `### Hands Off To` sub-lists.
7. `## Folder Scope` — a three-row table: Read / Write / Never-touch.
8. `## Quality Bar` — observable "done" criteria. Embedded checklists that are owned by a single role (coding standards, review checklist) live here.
9. `## Output Format` — the canonical `Result: PASS | FAIL | BLOCKED | ESCALATE` block followed by a conditional Escalation Request block when `Result` is `ESCALATE`.

**An agent file MUST NOT contain:**
- Step-by-step procedures, numbered workflows, or conditional branching logic.
- Retry thresholds or escalation-trigger lists (those live in the skill that detects them).
- `Must Escalate` or `Escalation Triggers` sections — consolidated into the `## Escalation` pointer above.
- A `Delegation Contract` section — the frontmatter description already names required inputs; use the `## Inputs` one-line pointer.
- A `Capabilities → Tools` sub-section — the `tools` frontmatter is authoritative.

An agent *references* skills ("use the `tdd` skill for implementation") but does not *describe* the procedure the skill follows. Agents do not reference other agents operationally (use role labels under `Spawned By` / `Hands Off To`, not cross-file dependencies).

Full template: [`guides/agent_template.md`](guides/agent_template.md).

### Skill files (`.claude/skills/`)

A skill file defines a **procedure** — a repeatable sequence of steps that any agent (or human) can invoke.
It answers: *What are the steps? In what order? What are the inputs and outputs? What can go wrong?*

**A skill file SHOULD contain:**
- **Steps** — numbered, deterministic sequence with clear inputs and outputs per step.
- **Escalation** — when the skill can return `ESCALATE`, a section listing the retry threshold and boundary-violation triggers, plus the canonical 4-field escalation request block.
- **Output format** — what the skill produces. Verdict vocabulary must align with the agent `Result:` shape; do not invent alternatives like `Gate 2 Verdict:`.
- **Quality criteria** — how to evaluate whether the procedure was followed correctly.
- **Anti-patterns / common pitfalls** — mistakes to avoid during execution.

**A skill file MUST NOT contain:**
- Role identity, decision authority, scope boundaries, or "who I am" framing — those belong in the agent.

Skills fall into three categories:
- **Procedures** — analytical, multi-step work (brainstorm, spec-breakdown, tdd, code-review, debug, merge-conflicts, integrate, escalation-review, spec-breakdown-review).
- **Orchestrators** — autonomous loops that spawn subagents and drive workflows (dev-loop, bug-loop). Use `Agent` in `allowed-tools` and typically `disable-model-invocation: true`.
- **Actions** — single-purpose operations (new-spec, new-task, new-bug, new-adr, status-report, git-conventions).

Full template: [`guides/skill_template.md`](guides/skill_template.md).

### The test

> If the content describes *what to do step by step*, it is a **skill**.
> If the content describes *who you are and what you're allowed to decide*, it is an **agent**.

---

## Settled Conventions

These are the conventions applied across `.claude/` after the 2026-04 review. New files should follow them; existing files were brought into compliance.

### Escalation chain

1. A role's skill detects a threshold breach or boundary violation and returns `ESCALATE` with the 4-field block:
   ```text
   Problem: [what went wrong]
   Attempted: [what was tried, including retry count or review cycle]
   Failed because: [why it did not work]
   Question: [specific decision or guidance needed]
   ```
2. The caller (an orchestrator skill or the human) forwards the request to the Architect by spawning the Architect subagent with the `escalation-review` skill.
3. `escalation-review` returns either `RESOLVED` (with a directive) or `HUMAN_ESCALATION` (with a Phase 2 Human Escalation Report generated from the canonical template in that skill).
4. On `HUMAN_ESCALATION`, the orchestrator commits a lifecycle marker (`chore(tasks): escalate T-NNN — move to blocked` or `chore(bugs): escalate B-NNN — needs human review`), stops the loop, and surfaces the Phase 2 report to the human.

### Subagent invocation

Orchestrators and `spec-breakdown` spawn subagents with uniform wording:

```markdown
**Spawn the <Role> subagent** with this prompt:

> "[Role-specific instructions]
> [Skill to use]
> [Target branch or canonical file]
> [Verdict vocabulary — Result: PASS | FAIL | ESCALATE]
> Populate every field of the Output Format block, including `Obstacles Encountered`."
```

The four ingredients per spawn prompt:
1. Name the skill the subagent should use.
2. Name the target (branch, file, or canonical path).
3. Specify the expected verdict vocabulary.
4. Require `Obstacles Encountered` in the output.

### Verdict vocabulary

All agents and all skills the agents invoke use the same verdict words:

```text
Result: PASS | FAIL | BLOCKED | ESCALATE
```

Do not invent per-skill vocabulary (e.g. `Gate 2 Verdict:`). If the domain needs a specialised label, add it as an additional field alongside `Result:`.

### Explicit skill invocation

A skill that invokes another skill in-process must declare it in `allowed-tools`:

```yaml
allowed-tools: Read, Glob, Grep, Bash, Skill(merge-conflicts), Skill(new-bug), Skill(git-conventions)
```

Referential mentions (describing what a downstream caller will do) do not require a `Skill()` declaration. Example: `tdd` mentions `escalation-review` in prose but does not call it — no declaration needed.

### Naming

- Agent names: bare role (`planner`, `developer`, `architect`).
- Skill names: lowercase-hyphenated, action-oriented (`spec-breakdown`, `code-review`, `git-conventions`).
- Branch names: `task/T-NNN-short-description`, `bug/B-NNN-short-description` (see `git-conventions` skill).
- Commit messages: `<type>(<component>): <description>` (see `git-conventions` skill).

---

## How to Work Here

### Reviewing this repo

1. Read `CLAUDE.md` (this file) and `guides/agent_template.md` / `guides/skill_template.md`.
2. Spot-check that every agent has the nine canonical sections in order and no forbidden sections.
3. Spot-check that skills never embed role identity; never reference `ai-process/`; carry the 4-field escalation block whenever they can return `ESCALATE`.
4. Grep for verdict drift: `grep -rn "Gate 2 Verdict:\|Verdict:" .claude/` should surface only aligned uses of `Result:`.
5. Grep for spawn drift: `grep -rn "Spawn the" .claude/skills/` should only show `**Spawn the <Role> subagent**`.

### Adding a new agent

1. Copy the template from `guides/agent_template.md`.
2. Decide whether the role needs a new skill or invokes existing ones. New skills: create them first.
3. Keep the `## Escalation` section to one paragraph pointing at the skill(s). If a threshold or trigger does not yet exist in a skill, add it to the skill rather than inlining it in the agent.
4. Add the agent to the "Canonical Agents In This Repo" table in `guides/agent_template.md`.

### Adding a new skill

1. Copy the template from `guides/skill_template.md` matching the category (procedure, orchestrator, action).
2. If the skill can return `ESCALATE`, include a `## Escalation` section with the 4-field block.
3. If the skill invokes another skill in-process, declare `Skill(other-skill)` in `allowed-tools`.
4. If the skill spawns subagents, declare `Agent` in `allowed-tools` and use `**Spawn the <Role> subagent**` wording.
5. If the skill is human-triggered only, set `disable-model-invocation: true`.

### Changing an existing rule

1. Find its single owning file in `.claude/` (an agent's `Quality Bar`, or a dedicated skill).
2. Change it there.
3. Grep for stale references — consumers reference owners by name (e.g., `` `git-conventions` skill ``), so the change propagates without content duplication.
4. If the rule was duplicated (shouldn't happen, but may), fix the duplication: pick an owner, delete the copies, and insert cross-references.

### Don't

- Don't add a rule to `ai-process/` without also updating `.claude/` so the implementation stays consistent (or vice versa — update both atomically).
- Don't embed `ai-process/` paths in `.claude/` files.
- Don't duplicate spec content across multiple `.claude/` files.
- Don't add procedural steps to an agent.
- Don't add role identity or authority to a skill.
- Don't invent a new verdict vocabulary for a new skill.
