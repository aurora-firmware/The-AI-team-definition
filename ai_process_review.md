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

Post-fix status:

- Findings 1, 2, and 7 are now resolved in the authoritative `ai-process` documents.
- Findings 1 and 2 remain valid for the `.claude/skills` and `.claude/agents` implementation until the loops and role skills adopt the canonical `dev-agent` lifecycle-state model.
- Finding 7 is no longer valid after the workflow overview clarified Architect-first escalation.
- Findings 3, 4, 5, 6, 8, and 9 remain valid implementation issues.

## Findings And Suggestions

### 1. Task-regression bug branches can lose the bug report file

**Severity:** High

**Status:** Resolved in `ai-process`; still valid in `.claude/skills/bug-loop/SKILL.md`.

`bug-loop` moves the bug file to `project/bugs/in-progress/` and commits that move on `dev-agent`, then creates task-regression bug branches from the bug report's `source_branch`.
That preserved task branch may not contain the moved bug file, but the Developer prompt expects `project/bugs/in-progress/<bug-file>` to exist on the bug branch.

Relevant files:

- `.claude/skills/bug-loop/SKILL.md`
- `ai-process/processes/workflow-overview.md`

**Why this matters:**

The ai-process requires task-regression bugs to branch from the preserved source branch, but the bug report is the contract for diagnosis, review, and fix verification.
If the bug branch does not contain the bug file, the Developer and Reviewer do not have the artifact they are instructed to update.

**Suggestion:**

The ai-process now defines the ownership model: task and bug files are canonical lifecycle state on `dev-agent`.
Update `bug-loop` so task-regression bug branches do not need the bug file to exist on the implementation branch.
The loop must pass canonical bug content to the Developer and Reviewer, collect Diagnosis Log and Work Log handoffs, append them to the canonical bug file on `dev-agent`, and read only committed canonical Review Verdict entries.

### 2. Review verdict branch and commit ownership is underspecified

**Severity:** High

**Status:** Resolved in `ai-process`; still valid in `dev-loop`, `bug-loop`, `code-review`, and Reviewer implementation text.

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

The ai-process now states:

- Reviewer appends the verdict to the work item file in the canonical `dev-agent` state branch.
- Reviewer commits the verdict according to `git-conventions.md`.
- The active loop reads the verdict only after that commit exists.

Update `dev-loop`, `bug-loop`, `code-review`, and `.claude/agents/reviewer.md` to follow that model.

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

**Status:** Resolved in `ai-process`.

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

Completed. The workflow overview now says:

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

## Additional Findings After Ai-Process Fixes

### 10. Developer log handling still assumes branch-local work-item edits

**Severity:** High

The ai-process now says Developer Diagnosis Log and Work Log entries are handoffs recorded by the active loop in the canonical task or bug file on `dev-agent`.
Several implementation files still tell the Developer or procedure to append directly to the task or bug file.

Relevant files:

- `.claude/skills/dev-loop/SKILL.md`
- `.claude/skills/bug-loop/SKILL.md`
- `.claude/skills/tdd/SKILL.md`
- `.claude/skills/debug/SKILL.md`
- `.claude/agents/developer.md`

**Suggestion:**

Update the Developer-facing skills and agent to return log-entry content to the active loop instead of writing lifecycle files directly.
Update `dev-loop` and `bug-loop` to append those entries to the canonical work item on `dev-agent` and commit before invoking Reviewer.

### 11. Integration still treats lifecycle logs as source-branch merge content

**Severity:** Medium

The ai-process now makes task and bug files canonical on `dev-agent`, but `integrate` still says to preserve Work Log and Diagnosis Log content "as-is on merge".
That instruction assumes lifecycle logs are part of the source branch merge payload.

Relevant files:

- `.claude/skills/integrate/SKILL.md`

**Suggestion:**

Update `integrate` so it reads work-item state from the canonical `dev-agent` file before merge verification.
It should treat task and bug files as lifecycle state owned by the active loop, not as implementation artifacts to merge from task or bug branches.

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
git diff --check -- ai-process ai_process_review.md
rg -n "coding-guidelines|npm test|Next\\.js|Drizzle|Claude API|component patterns|append a Work Log|append.*Diagnosis Log|Append.*verdict|preserve the Work Log|Hand off to integrator" ai-process .claude/skills .claude/agents ai_process_review.md
```

Result: whitespace check passed.
The targeted scan found no remaining hardcoded project command or stack-specific technology mentions in `ai-process/`.
Remaining hits are the implementation issues recorded above in `.claude/skills/` and the review document itself.
