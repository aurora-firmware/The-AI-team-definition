---
name: new-spec
description: Create a new specification document from the template
argument-hint: "[optional: specification title]"
disable-model-invocation: true
allowed-tools: Read, Glob, Write, Bash
---

Create a new specification document.

1. Read the template at `${CLAUDE_SKILL_DIR}/assets/TEMPLATE-specification.md`.
2. Ask for the specification title and a brief description of what it covers (or use `$ARGUMENTS` if provided).
3. Run `bash "${CLAUDE_SKILL_DIR}/assets/slugify.sh" "<title>"` and append `.md` to get the filename (e.g., `user-authentication.md`).
4. Copy the template to `project/specs/<filename>.md`.
5. Fill in the frontmatter:
   - `title`: the provided title
   - `version`: "0.1"
   - `status`: "draft"
   - `created`: output of `date +%Y-%m-%d`
   - `author`: ask or use "AI Agent"
6. Replace placeholder headings and sections with content based on the description.
7. Leave sections that need more exploration marked with `[TODO]`.
8. Confirm the file was created and remind that it needs human review (Gate 1: Spec Approval).
