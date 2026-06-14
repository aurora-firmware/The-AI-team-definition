# New ADR

Create a new Architecture Decision Record (ADR) using `ai-team adr new --json`.

## Input Requirements

Provide these values directly when possible:
- `title` — required
- `description` — required
- `status` — required (`proposed`, `accepted`, or `superseded`)
- `supersedes` — optional ADR reference (for example, `ADR-002`)
- `affected_specs` — optional list of affected spec IDs (for example, `S-002`)

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask only for the missing fields before proceeding.

## Procedure

1. Resolve inputs from the caller. Use `$ARGUMENTS` as `title` when it is the only provided input.
2. Build the CLI command:
   - Base: `ai-team adr new "<title>" --status "<status>" --json`
   - Add `--supersedes "<supersedes>"` only when `supersedes` is provided.
   - Add `--affects-spec "<spec_id>"` once per item when `affected_specs` is provided.
3. Execute the command and parse the JSON response to capture:
   - `id` (for example, `ADR-003`)
   - `path` (absolute path to the created ADR file)
4. Open the created ADR file and fill body sections from the supplied `description`, replacing placeholder section content where appropriate.
5. Confirm the file exists under `project/decisions/` and return the CLI response values (`id` and `path`).
