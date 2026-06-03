---
name: change-request
description: Create a new change-request artifact via the ai-team CLI
argument-hint: "[change request title]"
allowed-tools: Read, Write, Bash
---

# Change Request

Create a new change-request artifact using `ai-team change-request new --json`, then fill the body with the proposed scope change.

## Input Requirements

Provide these values directly when possible:
- `title` — required
- `description` — required; summarize the requested change, why it is needed, affected specs or tasks, and any known risk

When invoked directly and required fields are missing, ask only for the missing fields before proceeding.

## Procedure

1. Resolve inputs:
   - Use the caller-provided `title` and `description` when present.
   - Use `$ARGUMENTS` as the title when it is the only provided input.
   - If the title or description is still missing, ask for the missing value.

2. Create the artifact:
   - Run `ai-team change-request new "<title>" --json`.
   - Parse the JSON response to capture `id` and `path`.

3. Open the created file and replace template placeholders with the supplied description.
   - Keep the frontmatter produced by the CLI.
   - Preserve the template structure unless the human explicitly requested a different format.
   - Mark unknown details as `[TODO]` instead of inventing them.

4. Confirm the created file exists and return the CLI response values.

## Quality Criteria

- The artifact id and path come from the CLI response.
- The title is reflected in the file heading.
- The body states the requested change, reason, affected artifacts, and unresolved questions.
- Unknown or unconfirmed details remain marked `[TODO]`.

## Output Format

Always return:

```text
Result: PASS | FAIL | BLOCKED

Summary:
- <brief statement of the change request created>

Artifacts:
- <change-request file created>

Evidence:
- <CLI command result or reason not run>

Obstacles Encountered:
- <missing input, unresolved scope issue, or "none">

Next Owner:
- <Human | Planner | none>

Next Action:
- <specific follow-up required, or "none">
```
