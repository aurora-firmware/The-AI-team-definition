---
name: new-bug
description: Create a new bug report from the template
argument-hint: "[optional: bug title]"
allowed-tools: Read, Glob, Write, Bash
---

# New Bug

Create a new bug report.

## Input Requirements

Required:
- `title`
- `severity` (`critical`, `high`, `medium`, or `low`)
- `summary`
- `reproduction-status` (`confirmed`, `intermittent`, or `not yet reproduced`)
- `reproduction-steps`
- `expected-behavior`
- `actual-behavior`
- `evidence`
- `environment`
- `source-branch` (required for task-regression bugs; blank for existing defects on `dev-agent`)
- `suspected-area` (or `unknown`)
- `fix-verification`

When invoked by another skill, the caller should provide every required field in the invocation text and this skill must use them without asking follow-up questions.
When invoked directly by a human and required fields are missing, ask only for the missing fields before proceeding.

## Procedure

1. Read the template at `${CLAUDE_SKILL_DIR}/assets/TEMPLATE-bug.md`.
2. Resolve inputs from the caller. Use `$ARGUMENTS` as the title when it is the only provided input.
3. Run `bash "${CLAUDE_SKILL_DIR}/assets/next-bug-id.sh"` to get the next bug ID (e.g., `B-003`).
4. Generate a filename with the ID prefix: `B-NNN-<lowercase-hyphenated-title>.md` (e.g., `B-001-crash-on-empty-input.md`).
5. Copy the template to `project/bugs/open/<filename>.md`.
6. Fill in the frontmatter:
   - `id`: the next sequential ID (e.g., "B-001")
   - `title`: the resolved title
   - `severity`: the resolved severity
   - `status`: "open"
   - `created`: output of `date +%Y-%m-%d`
   - `source_branch`: the resolved branch for task-regression bugs, or leave blank for existing-defect bugs
7. Fill in the Summary, Reproduction Status, Evidence, Reproduction Steps, Expected Behavior, Actual Behavior, Environment, Related, Suspected Area, and Fix Verification sections from the resolved intake details.
8. If reproduction is not yet confirmed, still create the bug, but explicitly record what evidence exists and the first diagnostic step the Developer should try.
9. Leave Diagnosis Log, Work Log, and Review sections empty except for their instructional comments.
10. Confirm the file was created in `project/bugs/open/`.
