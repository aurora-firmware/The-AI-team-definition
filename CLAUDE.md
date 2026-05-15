# The AI Team Definition

> **This is a META-PROJECT.** Its output is the ai-process (the rules), the agents and skills that implement those rules, and the `ai-team` CLI that supports the skills by managing project artifacts.

The **ai-process** is the authoritative description of the rules the AI team must follow.
The **`guides/`** folder holds human-readable specifications for cross-cutting authoring contracts (agent shape, skill shape, spec content). They specify *what good output looks like* in domains the ai-process does not own at that level of detail.
The **CLI package sources** (`cli/src/ai_team/init/sources/`) are the *product source-of-truth* for the agents, skills, and templates exported by `ai-team init`. Editing those files (and regenerating scaffolds) is how you change framework behavior.
The **`ai-team` CLI** itself (`cli/`) is the *tooling* the action skills invoke to scaffold, move, and report on project artifacts.
When they conflict: the ai-process wins for *rules*; `guides/` wins for *authoring contracts*; the CLI sources are the *implementation* that must satisfy both.

> The `.claude/` and `.codex/` folders at the repository root are **local agent configuration for this repo only** — they are this project's own consumed copy of the exported scaffolds, used when running agents *in* this repo. They are **not** part of the AI team definition and are not the source-of-truth for any rule, skill, or agent. Treat them as drifted artefacts: do not edit them to change framework behavior, and do not cite them as authoritative. If you need this repo's local copy refreshed, re-export from the CLI sources.

---

## Repository Map

| Folder | Purpose |
|---|---|
| `project/` | Placeholder for reference, expected in a project using the ai-process |
| `ai-process/architecture/` | System architecture documentation (skills and agents scope) |
| `ai-process/guidelines/` | Coding standards, review checklists, markdown conventions |
| `ai-process/processes/` | Workflow definitions, quality gates, escalation procedures |
| `guides/` | Human-facing specifications and reference docs: setup, customization, agent/skill/spec authoring contracts. The CLI sources implement these contracts |
| `cli/src/ai_team/init/sources/` | **Product source-of-truth.** Authoritative agents, skills, and assets that `ai-team init` exports to adopting projects. Edit here to change framework behavior |
| `cli/src/ai_team/templates/` | **Product source-of-truth.** Authoritative templates the CLI uses when creating new artifacts (spec, task, bug, adr, progress report) |
| `cli/` (rest) | The `ai-team` CLI package itself — manages project artifacts and bootstraps the framework into new repositories; the action skills invoke it instead of carrying their own scripts and templates |
| `.claude/`, `.codex/` | **Local agent configuration for this repo only.** Not part of the framework definition. Not authoritative. Do not edit to change framework behavior — change the CLI sources and re-export instead |

---

## The Spec–Implementation Relationship

```
ai-process/                          ← rules layer (workflow + gates + standards)
  processes/                         workflows, gates, transitions
  guidelines/                        coding, git, markdown standards
  architecture/                      AI team's structure

guides/                              ← authoring-contract layer (human-readable specs)
  agent_template.md                  shape every agent file must follow
  skill_template.md                  shape every skill file must follow
  spec-authoring-guide.md            what belongs in a specification document
  setup-guide.md / customization-guide.md   adoption guidance

cli/src/ai_team/init/sources/        ← product source-of-truth (implements the contracts)
  agents/claude/                     authoritative agent role files
  agents/codex/                      authoritative codex agent files
  skills/                            authoritative skill procedure files

cli/src/ai_team/templates/           ← product source-of-truth (artifact templates)
  spec.md, task.md, bug.md, adr.md, progress-report.md

cli/                                 ← tooling layer
  ai-team                            CLI that the action skills invoke

.claude/, .codex/                    ← local agent config for THIS repo only — not authoritative
```

**Reviewing this project** means checking that the CLI sources (agents, skills, templates) faithfully implement what `ai-process/` rules and `guides/` contracts specify, and that the CLI tooling stays consistent with the artifact lifecycle the ai-process defines.
**Changing framework behavior** means updating either the rules (`ai-process/`), the authoring contracts (`guides/`), or the implementation (`cli/src/ai_team/init/sources/` and `cli/src/ai_team/templates/`), then bringing the others into alignment atomically. Never update a CLI source in a way that contradicts an ai-process rule or a guides contract without updating the spec first.

### CLI sources must be self-contained

A skill or agent file under `cli/src/ai_team/init/sources/` must not reference paths under `ai-process/` or `guides/`. The rules and contracts document the *intent*; the implementation must *embed* the rules so that an agent or skill can execute without reading outside the exported scaffold tree.

When an ai-process rule or guides contract applies:

- **If a single agent uses it** → embed it in that agent's `## Quality Bar` (example: coding standards in `developer.md`, review checklist in `reviewer.md`).
- **If multiple agents or skills use it** → extract it as its own skill and have callers reference the skill by name (example: `git-conventions/SKILL.md` is invoked from `integrate`, `code-review`, `dev-loop`, and `bug-loop`).
- **Do not duplicate content across source files.** Duplication causes drift. Either pick a single owning file and cross-reference, or extract to a skill.

---

## Framework vs Project-Specific Details

This repository defines a reusable process framework.
Its agents and skills must not hardcode details that belong to a consuming software project.

Do **not** put project-specific values in the CLI sources (`cli/src/ai_team/init/sources/agents/`, `cli/src/ai_team/init/sources/skills/`, `cli/src/ai_team/templates/`) or in `ai-process/`, including:
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

### Agent files (`cli/src/ai_team/init/sources/agents/claude/`)

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

### Skill files (`cli/src/ai_team/init/sources/skills/`)

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

These are the conventions applied across the CLI sources after the 2026-04 review. New files should follow them; existing files were brought into compliance. The conventions describe the *exported* agents and skills under `cli/src/ai_team/init/sources/` — not the local `.claude/`/`.codex/` config in this repo.

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

1. Read `CLAUDE.md` (this file), `guides/agent_template.md`, `guides/skill_template.md`, and `guides/spec-authoring-guide.md`.
2. Spot-check that every agent under `cli/src/ai_team/init/sources/agents/claude/` has the nine canonical sections in order and no forbidden sections.
3. Spot-check that skills under `cli/src/ai_team/init/sources/skills/` never embed role identity; never reference `ai-process/` or `guides/`; carry the 4-field escalation block whenever they can return `ESCALATE`.
4. Grep for verdict drift: `grep -rn "Gate 2 Verdict:\|Verdict:" cli/src/ai_team/init/sources/` should surface only aligned uses of `Result:`.
5. Grep for spawn drift: `grep -rn "Spawn the" cli/src/ai_team/init/sources/skills/` should only show `**Spawn the <Role> subagent**`.
6. Spot-check `cli/src/ai_team/templates/spec.md` against `guides/spec-authoring-guide.md` — the template must steer authors toward prose + measurable criteria, not implementation code.

### Adding a new agent

1. Copy the template from `guides/agent_template.md`.
2. Place the new agent under `cli/src/ai_team/init/sources/agents/claude/` (and the Codex `.toml` under `cli/src/ai_team/init/sources/agents/codex/` if applicable).
3. Decide whether the role needs a new skill or invokes existing ones. New skills: create them first.
4. Keep the `## Escalation` section to one paragraph pointing at the skill(s). If a threshold or trigger does not yet exist in a skill, add it to the skill rather than inlining it in the agent.
5. Add the agent to the "Canonical Agents In This Repo" table in `guides/agent_template.md`.
6. Regenerate scaffold outputs with `cli/scripts/sync_init_scaffolds.py`.

### Adding a new skill

1. Copy the template from `guides/skill_template.md` matching the category (procedure, orchestrator, action).
2. Place the new skill under `cli/src/ai_team/init/sources/skills/<skill-name>/` as `body.md` + `metadata.toml`.
3. If the skill can return `ESCALATE`, include a `## Escalation` section with the 4-field block.
4. If the skill invokes another skill in-process, declare `Skill(other-skill)` in `allowed-tools`.
5. If the skill spawns subagents, declare `Agent` in `allowed-tools` and use `**Spawn the <Role> subagent**` wording.
6. If the skill is human-triggered only, set `disable-model-invocation: true`.
7. Regenerate scaffold outputs with `cli/scripts/sync_init_scaffolds.py`.

### Changing an existing rule

1. Find its single owning file in the CLI sources (an agent's `Quality Bar`, or a dedicated skill).
2. Change it there.
3. Grep for stale references — consumers reference owners by name (e.g., `` `git-conventions` skill ``), so the change propagates without content duplication.
4. If the rule was duplicated (shouldn't happen, but may), fix the duplication: pick an owner, delete the copies, and insert cross-references.
5. Regenerate scaffold outputs with `cli/scripts/sync_init_scaffolds.py`.

### Don't

- Don't edit `.claude/` or `.codex/` to change framework behavior — those are local config. Edit the CLI sources.
- Don't add a rule to `ai-process/` without also updating the CLI sources so the implementation stays consistent (or vice versa — update both atomically).
- Don't embed `ai-process/` or `guides/` paths in agent/skill files under `cli/src/ai_team/init/sources/`.
- Don't duplicate spec content across multiple CLI source files.
- Don't add procedural steps to an agent.
- Don't add role identity or authority to a skill.
- Don't invent a new verdict vocabulary for a new skill.
