---
title: "AI Process Implementation Review"
status: draft
created: 2026-04-22
---

# AI Process Implementation Review

This review checks whether `.claude/agents/` and `.claude/skills/` consistently implement the authoritative `ai-process/` documents.

## Summary

The agents are broadly aligned with the intended boundary: agents define roles, while skills define procedures.
The main inconsistencies are in state handling, branch handling, review verdict formats, and a hardcoded integration test command.

## Findings And Suggestions

### 1. Task-regression bug branches can lose the bug report file

**Severity:** High

`bug-loop` moves the bug file to `project/bugs/in-progress/` and commits that move on `dev-agent`, then creates task-regression bug branches from the bug report's `source_branch`.
That preserved task branch may not contain the moved bug file, but the Developer prompt expects `project/bugs/in-progress/<bug-file>` to exist on the bug branch.

Relevant files:

- `.claude/skills/bug-loop/SKILL.md`
- `ai-process/processes/workflow-overview.md`

**Why this matters:**

The ai-process requires task-regression bugs to branch from the preserved source branch, but the bug report is the contract for diagnosis, review, and fix verification.
If the bug branch does not contain the bug file, the Developer and Reviewer do not have the artifact they are instructed to update.

**Suggestion:**

Define one explicit ownership model:

- Option A: bug files are copied or checked into the bug branch after branching from `source_branch`.
- Option B: bug files remain `dev-agent` state only, and Developer/Reviewer prompts must read/update the bug file on `dev-agent` through a defined state-sync step.

Option A is simpler for branch-local diagnosis logs.

### 2. Review verdict branch and commit ownership is underspecified

**Severity:** High

The ai-process says the Reviewer owns review verdicts, and git conventions say the Reviewer commits verdicts on `dev-agent`.
The current `dev-loop` and `bug-loop` launch the Reviewer after Developer work on the task or bug branch, but they do not specify where verdict edits are made or who commits them.

Relevant files:

- `ai-process/processes/workflow-overview.md`
- `ai-process/guidelines/git-conventions.md`
- `.claude/skills/dev-loop/SKILL.md`
- `.claude/skills/bug-loop/SKILL.md`
- `.claude/skills/code-review/SKILL.md`

**Why this matters:**

Without a defined branch/commit path, verdict entries may land on task or bug branches, while the loop reads task and bug state from `dev-agent`.
This creates a risk that the loop cannot see the verdict, or that review metadata is committed on the wrong branch.

**Suggestion:**

Update `dev-loop`, `bug-loop`, and `code-review` to state:

- Reviewer appends the verdict to the work item file in the canonical state branch.
- Reviewer commits the verdict according to `git-conventions.md`.
- The active loop reads the verdict only after that commit exists.

If branch-local work item files are preferred, update `git-conventions.md` and the workflow docs to match that model.

### 3. Task review template contradicts the verdict format parsed by the loops

**Severity:** Medium

The task template instructs reviewers to append headings like `### Review 1 — PASS|FAIL`.
The `code-review` skill writes `### Review Verdict — [date]`, and `dev-loop` parses `### Review Verdict`.

Relevant files:

- `.claude/skills/new-task/assets/TEMPLATE-task.md`
- `.claude/skills/code-review/SKILL.md`
- `.claude/skills/dev-loop/SKILL.md`
- `ai-process/processes/workflow-overview.md`

**Why this matters:**

The loop depends on a stable heading format.
A task created from the template points the Reviewer toward a different format than the parser expects.

**Suggestion:**

Update `TEMPLATE-task.md` to use the canonical review format:

```markdown
### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- Reviewer notes...
```

### 4. Bug template lacks the review verdict section expected by bug-loop

**Severity:** Medium

`new-bug` says to leave “Review Verdicts” instructional comments empty, but the bug template has no review section.
`bug-loop` later reads the most recent `### Review Verdict` entry.

Relevant files:

- `.claude/skills/new-bug/SKILL.md`
- `.claude/skills/new-bug/assets/TEMPLATE-bug.md`
- `.claude/skills/bug-loop/SKILL.md`

**Why this matters:**

The bug flow expects review verdicts to be first-class bug artifacts.
The template should make that state explicit.

**Suggestion:**

Add a `## Review` or `## Review Verdicts` section to `TEMPLATE-bug.md` using the same canonical heading as task reviews.

### 5. `code-review` routes PASS to Integrator instead of the active loop

**Severity:** Medium

The component map says the Reviewer hands verdicts back to the Development Loop or Bug-Fix Loop.
The loops then invoke integration.
The `code-review` skill currently says that a PASS should hand off to the integrator.

Relevant files:

- `ai-process/architecture/component-map.md`
- `.claude/skills/code-review/SKILL.md`

**Why this matters:**

This blurs the process boundary.
Reviewer should record the verdict; orchestration belongs to the active loop.

**Suggestion:**

Change the PASS behavior in `code-review` to:

> Record PASS in the work item. The active loop reads the verdict and routes to integration.

### 6. `integrate` hardcodes `npm test`

**Severity:** Medium

Gate 4 requires unit and integration tests on the source and destination branch.
The `integrate` skill currently runs `npm test` for both phases.

Relevant files:

- `ai-process/processes/quality-gates.md`
- `.claude/skills/integrate/SKILL.md`

**Why this matters:**

This framework is meant to be reusable across projects.
Hardcoding `npm test` makes the integration procedure Node-specific and may skip project-specific integration checks.

**Suggestion:**

Make the integration test command configurable.
Recommended lookup order:

1. Work item verification command.
2. Project-specific docs such as `project/docs/coding_guidelines.md`.
3. Repository package or build configuration.
4. Ask the human or stop with `BLOCKED` if no test command can be determined.

### 7. Escalation timing is slightly ambiguous in the ai-process

**Severity:** Low

The workflow overview says that on third review failure or ESCALATE the development loop moves the task to `blocked/` and stops.
The escalation section says roles should consult the Architect first, then escalate to human if unresolved.
The current `dev-loop` follows the Architect-first interpretation.

Relevant files:

- `ai-process/processes/workflow-overview.md`
- `ai-process/processes/escalation-procedure.md`
- `.claude/skills/dev-loop/SKILL.md`

**Why this matters:**

The implementation may be correct, but the process text can be read two ways.
This increases the risk of future drift.

**Suggestion:**

Clarify the workflow overview so it says:

> On third review failure or ESCALATE, the development loop consults the Architect. If the Architect cannot resolve the issue, the task moves to `blocked/` and the loop stops for human action.

## Positive Alignment

- The component map and implementation now include first-class Architect procedures: `gate-2-preflight` and `escalation-consultation`.
- Agents mostly define roles, authority, scope, and handoffs rather than embedding procedure steps.
- Bug fixing is diagnosis-first, which matches the updated workflow and avoids a weak task-like bug loop.
- There is no standalone test-runner agent, which avoids hiding diagnostic output from the main workflow.
- The `debug`, `tdd`, `bug-loop`, and `code-review` skills now reflect bug diagnosis evidence as part of the implementation and review contract.

## Hardcoded Commands And Language-Specific Mentions

This section records a follow-up scan for project-specific commands, stack-specific coding guidance, and mentions of specific programming languages in `ai-process/`, `.claude/skills/`, and `.claude/agents/`.

### 8. `integrate` hardcodes a project-specific test command

**Severity:** Medium

`integrate` runs `npm test` on both the source branch and destination branch.
This is a Node-specific command and violates the framework boundary documented in `CLAUDE.md`: this repository should not hardcode test commands for consuming projects.

Relevant files:

- `.claude/skills/integrate/SKILL.md`

**Suggestion:**

Replace the hardcoded command with a lookup procedure:

1. Read the work item's verification command.
2. Read project-local guidance such as the target project's `CLAUDE.md`, project docs, README, or build configuration.
3. Use the discovered project command for both pre-merge and post-merge verification.
4. Stop with `BLOCKED` if no command can be found.

### 9. `tdd` contains stack-specific coding guidance

**Severity:** Medium

`tdd` references project-specific technologies in its input requirements: `Next.js`, `Drizzle`, `Claude API`, and component patterns.
Those are examples from a particular software project, not framework-level rules.

Relevant files:

- `.claude/skills/tdd/SKILL.md`

**Suggestion:**

Replace the stack-specific text with generic project-local discovery language:

> Read `ai-process/guidelines/coding-standards.md` for framework standards and read the target project's coding guidelines, README, package/build configuration, and human-provided instructions for stack-specific rules.

### Scan Notes

The Python fenced-code example in `ai-process/guidelines/markdown-conventions.md` is not treated as an issue.
It is an illustrative Markdown syntax example, not project-specific guidance.

The scan also found generic shell fences such as ` ```bash ` in templates and skills.
Those are used as placeholders for project-discovered commands rather than hardcoded project commands.
They are lower risk than `npm test`, but the project may still choose to standardize on neutral `text` fences for command placeholders if it wants zero shell-specific examples.

Git commands in integration and loop skills were not treated as project-specific command violations.
They implement the framework's own branch and merge model, which is part of `ai-process/guidelines/git-conventions.md`.

## Validation Performed

Ran:

```bash
git diff --check -- .claude/skills .claude/agents ai-process
```

Result: passed.
