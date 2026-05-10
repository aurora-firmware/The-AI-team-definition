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

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask only for the missing fields before proceeding.

## Procedure

1. Resolve inputs from the caller. Use `$ARGUMENTS` as `title` when it is the only provided input.
2. Build the CLI command:
   - Base: `ai-team bug new --json --title "<title>" --description "<description>" --severity "<severity>"`
   - Add `--task "<task>"` only when `task` is provided.
3. Execute the command and parse the JSON response to capture the created bug file path and ID.
4. If `details` content is provided, open the created bug file and replace only the matching details placeholders/sections supplied by the caller. Leave unspecified sections unchanged.
5. Confirm the file exists under `project/bugs/open/` and return the created path and ID.
