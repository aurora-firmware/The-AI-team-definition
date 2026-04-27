---
name: new-adr
description: Create a new Architecture Decision Record from the template
argument-hint: "[optional: decision title]"
allowed-tools: Read, Glob, Write, Bash
---

Create a new Architecture Decision Record (ADR).

## Input Requirements

Provide these values directly when possible:
- `title` — required
- `context` — required

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask only for the missing fields before proceeding.

## Procedure

1. Read the template at `${CLAUDE_SKILL_DIR}/assets/TEMPLATE-adr.md`.
2. Resolve inputs from the caller. Use `$ARGUMENTS` as the title when it is the only provided input.
3. Run `bash "${CLAUDE_SKILL_DIR}/assets/next-adr-number.sh"` to get the next ADR number (e.g., `003`). The script starts at `001` when no ADRs exist yet.
4. Generate a filename: `NNN-<lowercase-hyphenated-title>.md` (e.g., `001-use-filesystem-task-tracking.md`).
5. Copy the template to `project/decisions/<filename>.md`.
6. Fill in the frontmatter:
   - `number`: the sequential number
   - `title`: the resolved title
   - `status`: "proposed"
   - `created`: output of `date +%Y-%m-%d`
7. Fill in the Context section with the resolved context.
8. Leave Decision, Consequences, and Alternatives as placeholders for discussion.
9. Confirm the file was created and note that the status should be changed to "decided" once the decision is finalized.
