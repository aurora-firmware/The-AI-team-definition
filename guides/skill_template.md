---
title: "Skill Template"
status: draft
created: 2026-04-22
updated: 2026-04-24
---

# Skill Template

Use this template when creating a new skill for this framework. Skills are **procedures**: they describe what to do, in what order, with which inputs and outputs.

This template reflects the conventions settled during the 2026-04 review of `.claude/`. It follows the [Claude Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): concise `SKILL.md`, specific discovery metadata, progressive disclosure for detail, clear workflows, validation loops for quality-critical work.

## Skill Categories

Skills fall into three categories. The shape of the `SKILL.md` differs slightly per category.

- **Procedures** — analytical, multi-step work. Have a numbered `Procedure`, `Escalation` section, `Quality Criteria`, and `Common Pitfalls`. Examples: `tdd`, `code-review`, `integrate`, `debug`, `conflict-resolution`, `gate-2-preflight`, `escalation-consultation`, `brainstorm`, `write-plan`.
- **Orchestrators** — autonomous loops that spawn subagents and drive workflows. Have a numbered `Procedure` with explicit `**Spawn the <Role> subagent**` blocks, `Cycle Counter Reset`, `Commit Conventions`, `Hard Stops`, and `What This Skill Does NOT Do`. Usually carry `disable-model-invocation: true`. Examples: `dev-loop`, `bug-loop`.
- **Actions** — simple document-creation or single-purpose operations. Short numbered list, usually no escalation section, often carry `disable-model-invocation: true`. Examples: `new-spec`, `new-task`, `new-bug`, `new-adr`, `status-report`, `git-conventions`.

## The Separation Rule

A skill file must **not** contain:
- Role identity, decision authority, or scope ("I am the Reviewer", "the Architect can decide X alone") — those belong in the agent file of whichever role invokes the skill.
- Operational cross-references to other agents ("then the Developer agent takes over") — describe the handoff back to the *caller* (often an orchestrator skill), not to another agent.

A skill file **should** contain:
- Steps.
- Thresholds ("three consecutive failures", "one bisect cycle").
- Output format and verdict vocabulary.
- The 4-field escalation request block when the skill can return `ESCALATE`.

## Directory Structure

```text
skill-name/
├── SKILL.md
├── assets/
│   └── TEMPLATE-example.md
├── references/
│   └── reference-topic.md
└── scripts/
    └── helper.py
```

Only create `assets/`, `references/`, or `scripts/` when the skill needs them. Do not add `README.md`, quick references, or changelogs — the `SKILL.md` is the single entry point.

## Canonical Section Order

For **procedure skills**:

1. `# Skill Title`
2. `## Input Requirements`
3. `## Procedure` (numbered steps)
4. `## Escalation` (if the skill can return `ESCALATE`)
5. `## Output Format`
6. `## Quality Criteria`
7. `## Common Pitfalls`

For **orchestrator skills**, append after `## Procedure`:

- `## Cycle Counter Reset` (if the procedure has review or retry cycles)
- `## Commit Conventions` (canonical patterns — defer authoritative rules to `git-conventions`)
- `## Hard Stops (Do Not Continue)`
- `## What This Skill Does NOT Do`

## SKILL.md Template (procedure skill)

````markdown
---
name: skill-name
description: Does the specific work this skill is responsible for. Use when [trigger], when a workflow reaches [process point], or when [artifact/context] must be handled.
allowed-tools: Read, Glob, Grep, Bash
---

# Skill Title

## Input Requirements

- **Input artifact:** `path/or/artifact-name`
- **Required context:** [spec, task, bug, ADR, branch, logs, user answer]
- **Required tools or dependencies:** [tool/script/package], or `none`

Stop and return `BLOCKED` if a required input is missing and cannot be inferred safely.

## Procedure

### Step 1: Read Input
Read the input artifact and relevant prior context.

### Step 2: Identify the Work
Identify the concrete work required and the acceptance or completion criteria.

### Step 3: Perform the Action
Perform the smallest sufficient action that satisfies the criteria.

### Step 4: Validate
Run or perform the primary verification.
If validation fails, fix the issue and repeat validation before finishing.
If validation cannot be run, record why and provide the best available evidence.

### Step 5: Produce Output
Record the outcome in the required output location.

## Escalation

Return `ESCALATE` under any of these conditions. All cases use the same structured four-field request; the active loop forwards it to the Architect via the `escalation-consultation` skill. Do not resume the procedure until the Architect responds.

**Retry threshold.** [State the concrete count, e.g. "three consecutive Step N failures"].

**Boundary violations (no retry — escalate on first detection):**
- [Condition 1]
- [Condition 2]

```text
Problem: [what went wrong]
Attempted: [what was tried, including retry count]
Failed because: [why it did not work]
Question: [specific decision or guidance needed from the Architect]
```

## Output Format

- **Updated files:** [which files or directories this skill may write]
- **Log entry or verdict:** [required heading or format]
- **Final response:** [what the caller should be told, including the verdict vocabulary]

Skills used inside an agent's Output Format should align with the agent's `Result: PASS | FAIL | BLOCKED | ESCALATE` vocabulary. Do not invent alternative verdict words (e.g. a skill returning `Gate 2 Verdict:` when the surrounding agent output uses `Result:` — use `Result:`).

## Quality Criteria

- The skill triggered only for the intended use case.
- The procedure produced the expected artifact or state transition.
- Validation evidence is recorded.
- The implementation stayed within the skill's scope.
- The instructions remained concise and avoided duplicate reference content.

## Common Pitfalls

- Using a vague description that does not help skill discovery.
- Putting large reference material directly in `SKILL.md` instead of `references/`.
- Offering many equivalent options instead of a recommended default.
- Skipping validation or failing to define what success means.
- Mixing role identity or authority into a procedure skill.
````

## Orchestrator Additions

Orchestrators drive autonomous loops. They spawn subagents using a uniform prompt shape.

### Subagent spawn prompt

Use the exact wording `**Spawn the <Role> subagent** with this prompt:` followed by a quoted prompt block. The prompt must:

- Name the skill the subagent should use (e.g., *"implement it using the `tdd` skill"*).
- Name the target branch or canonical file path.
- Specify the expected verdict vocabulary (`PASS / FAIL / ESCALATE`, or the full Output Format block).
- End with: *"Populate every field of the Output Format block, including `Obstacles Encountered`."*

Example from `dev-loop/SKILL.md`:

```markdown
**Spawn the Developer subagent** with this prompt:

> "Pick up the task from the canonical task file `project/tasks/in-progress/<task-file>` on `dev-agent` and implement it using the tdd skill.
> You are on branch `task/T-NNN-...`. Commit after each red→green→refactor cycle.
> Do not edit the task lifecycle file on the task branch.
> Return a Work Log handoff entry at session end. The entry's heading is `### Session N — YYYY-MM-DD`; the body is free prose covering what was done, what was tried and rejected, and what remains. The loop will append and commit it on `dev-agent`.
> Populate every field of the Output Format block, including `Obstacles Encountered`."
```

### Frontmatter

Orchestrators typically declare `Agent` in `allowed-tools` (to spawn subagents) and `disable-model-invocation: true` (they are human-triggered, not auto-selected).

```yaml
allowed-tools: Read, Glob, Grep, Bash, Agent, Skill(integrate), Skill(git-conventions)
disable-model-invocation: true
```

### Phase-2 human escalation

When an orchestrator exhausts Phase 1 (Architect) without resolution, it produces a Phase 2 Human Escalation Report using the canonical template defined in `escalation-consultation/SKILL.md`. Do not reinvent the report shape — point at that template.

## Frontmatter Guidance

`name`:
- Lowercase letters, numbers, and hyphens only.
- Short and specific. Prefer action-oriented or noun-phrase names.
- Avoid vague names such as `helper`, `utils`, `tools`.

`description`:
- Third person.
- State what the skill does and when to use it.
- Include concrete trigger words, artifacts, and process states.
- Distinguish the skill from neighbouring skills.

**Good example** (from `code-review/SKILL.md`):
```yaml
description: Two-stage code review for completed tasks and bug fixes. Use when a Developer submits work and the Reviewer must check task acceptance or bug diagnosis criteria before reviewing code quality.
```

`allowed-tools`:
- Declare every tool the skill actually invokes.
- Declare every other skill invoked in-process via `Skill(other-skill)`.
- Referential mentions ("the active loop routes this to `escalation-consultation`") do **not** require a `Skill()` declaration when the current skill does not call it itself.

`argument-hint`:
- Use for skills invoked as slash commands with positional arguments. Document the argument shape tersely in frontmatter and fully in `## Input Requirements`.

`disable-model-invocation`:
- Set to `true` for orchestrators and actions that should only run on explicit human invocation, not via auto-selection.

## Explicit Skill Invocation

When one skill invokes another in-process, declare it in `allowed-tools` as `Skill(other-skill)` and reference it in prose by its backticked name. Example audit pattern:

| Skill | Invokes in-process | `allowed-tools` | Prose reference form |
|---|---|---|---|
| `integrate` | `conflict-resolution`, `new-bug`, `git-conventions` | `Skill(conflict-resolution), Skill(new-bug), Skill(git-conventions)` | `` Invoke the `conflict-resolution` skill `` |
| `code-review` | `git-conventions` | `Skill(git-conventions)` | `` Commit using the `git-conventions` skill `` |

Descriptive mentions — referring to skills the caller will invoke, or skills downstream in the chain — do not need a declaration. Example: `tdd` mentions `escalation-consultation` in prose to say *"the active loop forwards the request via `escalation-consultation`"*, but `tdd` itself does not invoke it, so it is not in `allowed-tools`.

## Escalation Mechanics Live Here

Agents carry only a one-paragraph `## Escalation` pointer. The actual mechanics — retry thresholds, boundary-violation triggers, the 4-field escalation request block — live in the skill. When you add or change a threshold, change it in the skill and the agent needs no edit.

Uniform 4-field block (mandatory shape when a skill can return `ESCALATE`):

```text
Problem: [what went wrong]
Attempted: [what was tried, including retry count or review cycle]
Failed because: [why it did not work]
Question: [specific decision or guidance needed]
```

## Self-Contained `.claude/` Rule

Skills must not reference content outside `.claude/`. If a cross-cutting rule (e.g. git conventions, coding standards) is needed in multiple skills, extract it into its own skill (see `git-conventions`). If it is needed in only one role, embed it in that role's agent `Quality Bar` (see `developer.md` coding standards, `reviewer.md` review checklist).

## Progressive Disclosure

Keep `SKILL.md` focused on the core workflow. Move detail out when it is conditional, large, or only needed for some variants:

- Put reusable templates in `assets/` (see `new-task/assets/TEMPLATE-task.md`).
- Put domain references, schemas, examples, or long policies in `references/`.
- Put deterministic or fragile operations in `scripts/`.

Reference every optional file directly from `SKILL.md` using `${CLAUDE_SKILL_DIR}/...` or `.claude/skills/<skill>/...`. Keep references one level deep so the agent can find and read the right file without chasing nested links.

## Validation And Evaluation

Before treating a skill as ready:

- Create at least three representative scenarios the skill should handle.
- Test that the skill triggers for the right requests.
- Test that it does not trigger for adjacent out-of-scope requests.
- Observe whether the agent reads the right referenced files.
- Iterate when the agent skips required steps, misses references, or overuses irrelevant detail.

For skills with scripts:

- Prefer running scripts over asking the model to recreate deterministic logic.
- Make script errors specific and actionable.
- Document required packages and environment assumptions.
- Use forward-slash paths.
- Add validation loops for critical operations.

## Anti-Patterns

- Embedding role identity or authority in a skill.
- Inventing a custom verdict vocabulary (`Gate 2 Verdict:`, `Review Status:`) instead of aligning with the caller's `Result:` shape.
- Prose-only escalation without the 4-field structured block.
- Inconsistent spawn wording (`Spawn the X role`, `invoke the X agent`). Use `**Spawn the <Role> subagent**` uniformly.
- Declaring `Skill(x)` in `allowed-tools` when the skill only references `x` descriptively and never invokes it.
- Referencing `ai-process/` paths. Skills must be self-contained within `.claude/`.
