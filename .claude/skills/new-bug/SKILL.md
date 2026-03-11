---
name: new-bug
description: Create a new bug report from the template
argument-hint: "[optional: bug title]"
disable-model-invocation: true
allowed-tools: Read, Glob, Write
---

Create a new bug report.

1. Read the template at `.claude/skills/new-bug/assets/TEMPLATE-bug.md`.
2. Ask for: bug title, severity (critical/high/medium/low), and a summary of the issue. Use `$ARGUMENTS` as the title if provided.
3. Determine the next bug ID by scanning existing files in `bugs/` (all subdirectories) for the highest `B-NNN` ID, then increment.
4. Generate a filename: lowercase, hyphenated, based on the title (e.g., `crash-on-empty-input.md`).
5. Copy the template to `bugs/open/<filename>.md`.
6. Fill in the frontmatter:
   - `id`: the next sequential ID (e.g., "B-001")
   - `title`: the provided title
   - `severity`: the provided severity
   - `status`: "open"
   - `created`: today's date
7. Fill in the Summary section with the provided description.
8. Leave Reproduction Steps, Expected/Actual Behavior, and Environment as placeholders.
9. Confirm the file was created in `bugs/open/`.
