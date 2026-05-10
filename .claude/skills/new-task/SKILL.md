---
name: new-task
description: Create a new task from the template
argument-hint: "[optional: task title]"
allowed-tools: Read, Write, Bash
---

# New Task

Create a new task.

## Input Requirements

Provide these values directly when possible:
- `title` — required
- `description` — required when the caller wants Description filled immediately
- `priority` — required (`critical`, `high`, `medium`, or `low`)
- `assigned-role` — optional; defaults to `unassigned`
- `acceptance-criteria` — optional list to replace `AC-1 ...` placeholders

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask for the missing values before proceeding.

## Procedure

1. Resolve inputs:
   - Use the caller-provided `title`, `description`, `priority`, and `assigned-role` when they are present.
   - If invoked directly and some required fields are missing, ask only for the missing fields.
   - Use `$ARGUMENTS` as the title when it is the only provided input.
2. Run `ai-team task new "<title>" --priority <priority> [--assigned-role <assigned-role>] --json`.
3. Parse the JSON response and capture:
   - `id` (e.g., `T-003`)
   - `path` (absolute path to the created file)
4. If `description` was provided, replace the default text in `## Description` with the caller-provided content.
5. If `acceptance-criteria` were provided, replace placeholder `AC-*` lines in `## Acceptance Criteria` with the caller-provided list.
6. Leave Dependencies, Files to Touch, and Verification as placeholders unless the caller explicitly provided values for those sections.
7. Verify the drafted task (or placeholders that will be completed) can satisfy the Task Quality Rules below.
8. Confirm creation using the CLI response values (`id` and `path`).

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
