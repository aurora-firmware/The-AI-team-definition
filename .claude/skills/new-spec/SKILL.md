---
name: new-spec
description: Create a new specification document from the template
argument-hint: "[optional: specification title]"
allowed-tools: Read, Glob, Write, Bash
---

Create a new specification document.

## Input Requirements

Provide these values directly when possible:
- `title` — required
- `description` — required
- `author` — optional; defaults to `AI Agent`
- `status` — optional; defaults to `draft`

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask for the missing values before proceeding.

## Procedure

1. Read the template at `${CLAUDE_SKILL_DIR}/assets/TEMPLATE-specification.md`.
2. Resolve inputs:
   - Use the caller-provided `title`, `description`, `author`, and `status` when they are present.
   - If invoked directly and some required fields are missing, ask only for the missing fields.
   - Use `$ARGUMENTS` as the title when it is the only provided input.
3. Run `bash "${CLAUDE_SKILL_DIR}/assets/slugify.sh" "<title>"` and append `.md` to get the filename (e.g., `user-authentication.md`).
4. Copy the template to `project/specs/<filename>.md`.
5. Fill in the frontmatter:
   - `title`: the resolved title
   - `version`: "0.1"
   - `status`: the resolved status
   - `created`: output of `date +%Y-%m-%d`
   - `author`: the resolved author
6. Replace placeholder headings and sections with content based on the resolved description.
7. Leave sections that need more exploration marked with `[TODO]`.
8. Confirm the file was created and remind that it needs human review (Gate 1: Spec Approval) unless the caller explicitly says it is being prepared directly for that gate.
