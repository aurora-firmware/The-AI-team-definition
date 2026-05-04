---
name: new-task
description: Create a new task from the template
argument-hint: "[optional: task title]"
allowed-tools: Read, Glob, Write, Bash
---

# New Task

Create a new task.

## Input Requirements

Provide these values directly when possible:
- `title` — required
- `description` — required
- `priority` — required (`critical`, `high`, `medium`, or `low`)
- `assigned-role` — optional; defaults to `unassigned`

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask for the missing values before proceeding.

## Procedure

1. Read the template at `${CLAUDE_SKILL_DIR}/assets/TEMPLATE-task.md`.
2. Resolve inputs:
   - Use the caller-provided `title`, `description`, `priority`, and `assigned-role` when they are present.
   - If invoked directly and some required fields are missing, ask only for the missing fields.
   - Use `$ARGUMENTS` as the title when it is the only provided input.
3. Run `bash "${CLAUDE_SKILL_DIR}/assets/next-task-id.sh"` to get the next task ID (e.g., `T-003`).
4. Generate a filename with the ID prefix: `T-NNN-<lowercase-hyphenated-title>.md` (e.g., `T-001-implement-auth-flow.md`).
5. Copy the template to `project/tasks/pending/<filename>.md`.
6. Fill in the frontmatter:
   - `id`: the next sequential ID (e.g., "T-001")
   - `title`: the resolved title
   - `status`: "pending"
   - `priority`: the resolved priority
   - `assigned-role`: the resolved assigned role
   - `created`: output of `date +%Y-%m-%d`
7. Fill in the Description section with the resolved description.
8. Leave Acceptance Criteria, Dependencies, Files to Touch, and Verification as placeholders for the Planner or user to complete unless the caller explicitly provided values for them.
9. Verify the drafted task (or the placeholders that will be completed) can satisfy the Task Quality Rules below.
10. Confirm the file was created in `project/tasks/pending/`.

## Task Quality Rules

Every task file produced by this skill must be:

- **Atomic** — one clear outcome. If the task delivers two independent outcomes, split it into two tasks.
- **One-shottable** — completable in a single agent session without running out of context. Rules of thumb: touches at most **3–4 files**, has at most **5 acceptance criteria**, and the Description fits in roughly **20 lines**. If a draft task exceeds any of these, split it or narrow the scope.
- **Verifiable** — has a concrete `Verification` command that proves the task is done. If no automated command is possible, the Verification section states the exact manual steps.
- **Self-contained** — the Description provides enough context for an agent to start without asking follow-up questions. Any prior decisions, files, or conventions the task depends on are named explicitly.
- **EARS-compliant acceptance criteria** — every AC matches one of the five EARS patterns documented in the template (Ubiquitous, Event-driven, Unwanted-behaviour, State-driven, Optional). An AC that resists EARS usually means the task is not atomic.
- **Dependency-honest** — if the task reads or modifies something that another pending task creates, list that other task ID under `Dependencies`.

Rules that govern the *set of tasks* (no two tasks modifying the same file without a dependency, full coverage of the specification) are enforced by the `spec-breakdown` skill, not here. `new-task` enforces per-task shape; `spec-breakdown` enforces the plan as a whole.

## Common Pitfalls

- **Task is really two tasks** — reads like "Implement X AND migrate Y". Split.
- **Description is a ticket title, not enough to start** — agent has to open the spec or ask questions. Expand.
- **Acceptance criteria are aspirational, not testable** — "Works well under load" is not an AC. Name the measurable behaviour.
- **No verification command** — if the task has no way to prove it's done, its acceptance criteria are not specific enough.
- **Hidden dependency** — the task reads a file a sibling task creates but no dependency is listed. The `spec-breakdown` Gate 2 preflight will catch this, but it's cheaper to catch here.
