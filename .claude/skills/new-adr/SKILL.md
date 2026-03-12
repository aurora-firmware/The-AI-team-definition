---
name: new-adr
description: Create a new Architecture Decision Record from the template
argument-hint: "[optional: decision title]"
disable-model-invocation: true
allowed-tools: Read, Glob, Write
---

Create a new Architecture Decision Record (ADR).

1. Read the template at `.claude/skills/new-adr/assets/TEMPLATE-adr.md`.
2. Ask for: decision title and the context (what situation requires this decision). Use `$ARGUMENTS` as the title if provided.
3. Determine the next ADR number by scanning existing files in `project/decisions/` for the highest `NNN-` prefix, then increment. If no ADRs exist yet, start at 001.
4. Generate a filename: `NNN-<lowercase-hyphenated-title>.md` (e.g., `001-use-filesystem-task-tracking.md`).
5. Copy the template to `project/decisions/<filename>.md`.
6. Fill in the frontmatter:
   - `number`: the sequential number
   - `title`: the provided title
   - `status`: "proposed"
   - `created`: today's date
7. Fill in the Context section with the provided context.
8. Leave Decision, Consequences, and Alternatives as placeholders for discussion.
9. Confirm the file was created and note that the status should be changed to "decided" once the decision is finalized.
