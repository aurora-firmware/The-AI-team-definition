---
name: new-spec
description: Create a new specification document via the ai-team CLI
argument-hint: "[optional: specification title]"
allowed-tools: Read, Write, Bash
---

# New Spec

Create a new specification document using `ai-team spec new --json`.

## Input Requirements

Provide these values directly when possible:
- `title` — required
- `description` — required
- `author` — optional; defaults to `AI Agent`
- `status` — optional; defaults to `draft`

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask for the missing values before proceeding.

## Procedure

1. Resolve inputs:
   - Use the caller-provided `title`, `description`, `author`, and `status` when they are present.
   - If invoked directly and some required fields are missing, ask only for the missing fields.
   - Use `$ARGUMENTS` as the title when it is the only provided input.
2. Build the CLI command:
   - Base: `ai-team spec new --json --title "<title>" --description "<description>"`
   - Add `--author "<author>"` only when `author` is provided; otherwise allow the CLI default.
   - Add `--status "<status>"` only when `status` is provided; otherwise allow the CLI default.
3. Execute the command and parse the JSON response to capture:
   - `id` (for example, `S-003`)
   - `path` (absolute path to the created file)
4. Open the created spec file and fill body sections from the supplied `description`, replacing placeholder section content where appropriate.
5. Leave sections that still need exploration marked with `[TODO]`.
6. Confirm the created file exists and return the CLI response values (`id` and `path`).
7. Remind that the new spec requires human Gate 1 approval unless the caller explicitly says it is already being prepared for that gate.
