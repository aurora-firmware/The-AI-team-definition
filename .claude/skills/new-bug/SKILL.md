---
name: new-bug
description: Create a new bug report via the ai-team CLI
argument-hint: "[optional: bug title]"
allowed-tools: Read, Write, Bash
---

# New Bug

Create a new bug report using `ai-team bug new --json`.

## Input Requirements

Required (passed to the `ai-team` CLI):
- `title`
- `severity` (`critical`, `high`, `medium`, or `low`)

Optional (passed to the `ai-team` CLI):
- `task` (task reference such as `T-021`)

Agent-consumed (used to fill body sections after file creation; NOT passed to the CLI):
- `description` — free-form prose the agent uses when populating body sections in step 4;
  not a CLI flag and must not be passed as a CLI argument
- `details` (extra section content to replace placeholders after file creation)

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask only for the missing fields before proceeding.

## Procedure

1. Resolve inputs from the caller. Use `$ARGUMENTS` as `title` when it is the only provided input.
2. Build the CLI command:
   - Base: `ai-team bug new "<title>" --severity "<severity>" --json`
   - Add `--task "<task>"` only when `task` is provided.
   - Do NOT pass `description` or `details` to the CLI — the CLI has no `--description` flag.
3. Execute the command and parse the JSON response to capture the created bug file path and ID.
4. Open the created bug file and fill the body from the supplied `description`. This step is done by the agent after the file is created — not by the CLI.
5. If `details` content is provided, replace only the matching details placeholders/sections supplied by the caller. Leave unspecified sections unchanged.
6. Confirm the file exists under `project/bugs/open/` and return the created path and ID.
