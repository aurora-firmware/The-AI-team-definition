---
name: new-adr
description: Create a new Architecture Decision Record via the ai_team tool
---

# New ADR

Create a new Architecture Decision Record (ADR) using the `ai_team` tool's `adr new` command.

## Input Requirements

Provide these values directly when possible:
- `title` — required
- `description` — required
- `status` — required (`proposed`, `accepted`, or `superseded`)
- `supersedes` — optional ADR reference (for example, `ADR-002`)

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask only for the missing fields before proceeding.

## Procedure

1. Resolve inputs from the caller. Use `$ARGUMENTS` as `title` when it is the only provided input.
2. Build the tool command:
   - Base: the `ai_team` tool call `{"command": "adr new", "title": "<title>", "status": "<status>"}`
   - Add `supersedes "<supersedes>"` only when `supersedes` is provided.
3. Execute the command and parse the JSON response to capture:
   - `id` (for example, `ADR-003`)
   - `path` (absolute path to the created ADR file)
4. Open the created ADR file and fill body sections from the supplied `description`, replacing placeholder section content where appropriate.
5. Confirm the file exists under `project/decisions/` and return the tool response values (`id` and `path`).
6. After recording the ADR, run the `architecture-consistency-review` skill — the Architect runs both ADR creation and this review — to check the decision against every approved spec and accepted ADR before treating it as settled.
