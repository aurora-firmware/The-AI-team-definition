---
name: new-bug
description: Create a new bug report via the ai-team CLI
argument-hint: "[optional: bug title]"
allowed-tools: Read, Write, Bash
---

# New Bug

Create a new bug report using `ai-team bug new --json`.

## Input Requirements

Required:
- `title`
- `description`
- `severity` (`critical`, `high`, `medium`, or `low`)

Optional:
- `task` (task reference such as `T-021`)
- `details` (extra section content to replace placeholders after file creation)

For **integration-filed regression bugs** (bugs discovered during or after integration of a
task branch), the following additional fields are required:
- `source_branch` — the task or bug branch where the regression was introduced (e.g. `task/T-021-...`).
- `expected` — the expected behaviour before the regression.
- `actual` — the actual (broken) behaviour observed.
- `evidence` — reproduction steps, test output, logs, or other observable evidence.
- `fix_verification` — the test command or manual step that will confirm the regression is resolved.

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask only for the missing fields before proceeding.

## Procedure

1. Resolve inputs from the caller. Use `$ARGUMENTS` as `title` when it is the only provided input.
2. Build the CLI command:
   - Base: `ai-team bug new "<title>" --severity "<severity>" --json`
   - Add `--task "<task>"` only when `task` is provided.
3. Execute the command and parse the JSON response to capture the created bug file path and ID.
4. Open the created bug file and fill the body from the supplied `description`.
5. If `details` content is provided, replace only the matching details placeholders/sections supplied by the caller. Leave unspecified sections unchanged.
6. For regression bugs, populate the regression fields in the bug file:
   - Set `source_branch` in the frontmatter or body as applicable.
   - Fill in the expected and actual behaviour sections.
   - Fill in the evidence section with reproduction steps and observable output.
   - Fill in the fix-verification section.
7. Confirm the file exists under `project/bugs/open/` and return the created path and ID.
