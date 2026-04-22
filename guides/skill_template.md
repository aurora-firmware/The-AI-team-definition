---
title: "Skill Template"
status: draft
created: 2026-04-22
---

# Skill Template

Use this template when creating a new skill for this framework.
It follows the Claude skill authoring best practices: keep `SKILL.md` concise, make discovery metadata specific, use progressive disclosure for detail, provide clear workflows, and include validation loops for quality-critical work.

Source guidance: [Claude Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

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

Only create `assets/`, `references/`, or `scripts/` when the skill needs them.
Do not add extra documentation files such as `README.md`, quick references, or changelogs.

## SKILL.md Template

````markdown
---
name: skill-name
description: Does the specific work this skill is responsible for. Use when the user asks for [trigger], when a workflow reaches [process point], or when [artifact/context] must be handled.
allowed-tools: Read, Glob, Grep, Bash
---

# Skill Title

## Purpose

One short paragraph stating what this skill does and the outcome it produces.
Do not explain general concepts the model already knows.

## When To Use

- Use when [specific trigger or request].
- Use when [specific artifact/state/process condition].
- Do not use when [nearby but out-of-scope case].

## Inputs

- **Input artifact:** `path/or/artifact-name`
- **Required context:** [spec, task, bug, ADR, branch, logs, user answer]
- **Required tools or dependencies:** [tool/script/package], or `none`

Stop and escalate or ask for clarification if a required input is missing and cannot be inferred safely.

## Procedure

1. Read the input artifact and relevant prior context.
2. Identify the concrete work required and the acceptance or completion criteria.
3. Perform the smallest sufficient action that satisfies the criteria.
4. Validate the result using the checks below.
5. Record the outcome in the required output location.

Keep steps sequential and deterministic when order matters.
For flexible work, describe decision points instead of over-specifying implementation.

## Validation

- Run or perform [primary verification].
- Check [required artifact/state/output].
- If validation fails, fix the issue and repeat validation before finishing.
- If validation cannot be run, record why and provide the best available evidence.

## Output

- **Updated files:** [which files or directories this skill may write]
- **Log entry or verdict:** [required heading/format if any]
- **Final response:** [what the caller should be told]

## Escalation

Escalate when:

- [condition that requires human or Architect input]
- [condition that would change an approved specification]
- [condition that cannot be resolved after the allowed retry/validation loop]

Use this format:

```text
Problem: [what went wrong]
Attempted: [what was tried]
Failed because: [why it did not work]
Question: [specific decision or help needed]
```

## References

Read these only when needed:

- `references/reference-topic.md` — use for [specific condition].
- `assets/TEMPLATE-example.md` — copy when creating [artifact].
- `scripts/helper.py` — run for [deterministic operation].

## Quality Criteria

- The skill triggered only for the intended use case.
- The procedure produced the expected artifact or state transition.
- Validation evidence is recorded.
- The implementation stayed within the skill's scope.
- The instructions remained concise and avoided duplicate reference content.

## Common Pitfalls

- Using a vague description that does not help skill discovery.
- Putting large reference material directly in `SKILL.md`.
- Offering many equivalent options instead of a recommended default.
- Skipping validation or failing to define what success means.
- Mixing role identity or authority into a procedure skill.
````

## Frontmatter Guidance

`name`:

- Use lowercase letters, numbers, and hyphens only.
- Keep it short and specific.
- Prefer gerund, noun phrase, or action-oriented names consistently across the skill set.
- Avoid vague names such as `helper`, `utils`, or `tools`.

`description`:

- Write in third person.
- State what the skill does and when to use it.
- Include concrete trigger words, artifacts, and process states.
- Keep it specific enough to distinguish the skill from neighboring skills.

Optional fields depend on the agent platform.
For this repo, use existing skill conventions for `allowed-tools`, `argument-hint`, and `disable-model-invocation`.

## Progressive Disclosure

Keep `SKILL.md` focused on the core workflow.
Move detail out when it is conditional, large, or only needed for some variants:

- Put reusable templates in `assets/`.
- Put domain references, schemas, examples, or long policies in `references/`.
- Put deterministic or fragile operations in `scripts/`.

Reference every optional file directly from `SKILL.md`.
Keep references one level deep so the agent can find and read the right file without chasing nested links.

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
