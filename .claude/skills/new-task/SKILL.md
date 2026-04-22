---
name: new-task
description: Create a new task from the template
argument-hint: "[optional: task title]"
disable-model-invocation: true
allowed-tools: Read, Glob, Write
---

Create a new task.

1. Read the template at `${CLAUDE_SKILL_DIR}/assets/TEMPLATE-task.md`.
2. Ask for: task title, description, priority (critical/high/medium/low), and assigned role (or unassigned). Use `$ARGUMENTS` as the title if provided.
3. Determine the next task ID by scanning existing files in `project/tasks/` (all subdirectories) for the highest `T-NNN` ID, then increment.
4. Generate a filename with the ID prefix: `T-NNN-<lowercase-hyphenated-title>.md` (e.g., `T-001-implement-auth-flow.md`).
5. Copy the template to `project/tasks/pending/<filename>.md`.
6. Fill in the frontmatter:
   - `id`: the next sequential ID (e.g., "T-001")
   - `title`: the provided title
   - `status`: "pending"
   - `priority`: the provided priority
   - `assigned-role`: the provided role or "unassigned"
   - `created`: today's date
7. Fill in the Description section with the provided description.
8. Leave Acceptance Criteria, Dependencies, Files to Touch, and Verification as placeholders for the Planner or user to complete.
9. Confirm the file was created in `project/tasks/pending/`.
