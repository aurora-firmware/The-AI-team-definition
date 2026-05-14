---
name: new-spec
description: Create a new specification document via the ai-team CLI
argument-hint: "[optional: specification title]"
allowed-tools: Read, Write, Bash
---

# New Spec

Create a new specification document using `ai-team spec new --json`.

## Input Requirements

Required (passed to the `ai-team` CLI):
- `title` — required

Optional (passed to the `ai-team` CLI):
- `author` — defaults to `planner` when omitted
- `status` — defaults to `draft` when omitted

Agent-consumed (used to fill body sections after file creation; NOT passed to the CLI):
- `description` — free-form prose the agent uses when populating body sections in step 4;
  not a CLI flag and must not be passed as a CLI argument

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask for the missing values before proceeding.

## Procedure

1. Resolve inputs:
   - Use the caller-provided `title`, `author`, and `status` for the CLI command.
   - Capture any `description` provided by the caller for use in step 4.
   - Use `$ARGUMENTS` as the title when it is the only provided input.
2. Build the CLI command:
   - Base: `ai-team spec new "<title>" --json`
   - Add `--author "<author>"` only when `author` is provided; otherwise allow the CLI default.
   - Add `--status "<status>"` only when `status` is provided; otherwise allow the CLI default.
   - Do NOT pass `description` to the CLI — the CLI has no `--description` flag.
3. Execute the command and parse the JSON response to capture:
   - `id` (for example, `S-003`)
   - `path` (absolute path to the created file)
4. Open the created spec file and fill body sections from the supplied `description`, replacing placeholder section content where appropriate. This step is done by the agent after the file is created — not by the CLI.
5. Leave sections that still need exploration marked with `[TODO]`.
6. Confirm the created file exists and return the CLI response values (`id` and `path`).
7. Remind that the new spec requires human Gate 1 approval unless the caller explicitly says it is already being prepared for that gate.
