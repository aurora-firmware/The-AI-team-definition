---
name: new-bug
description: Create a new bug report from the template
argument-hint: "[optional: bug title]"
disable-model-invocation: true
allowed-tools: Read, Glob, Write, Bash
---

Create a new bug report.

1. Read the template at `${CLAUDE_SKILL_DIR}/assets/TEMPLATE-bug.md`.
2. Ask for intake details. Use `$ARGUMENTS` as the title if provided.
   Required:
   - bug title
   - severity (critical/high/medium/low)
   - summary of the issue and impact
   - reproduction status (confirmed/intermittent/not yet reproduced)
   - reproduction steps or failing command/test
   - expected behavior
   - actual behavior
   - logs, stack trace, failing assertion, screenshot reference, or other evidence
   - environment details
   - branch context (`source_branch` for task-regression bugs; otherwise `dev-agent` unless stated)
   - suspected area, or `unknown`
   - fix verification command or manual check
3. Run `bash "${CLAUDE_SKILL_DIR}/assets/next-bug-id.sh"` to get the next bug ID (e.g., `B-003`).
4. Generate a filename with the ID prefix: `B-NNN-<lowercase-hyphenated-title>.md` (e.g., `B-001-crash-on-empty-input.md`).
5. Copy the template to `project/bugs/open/<filename>.md`.
6. Fill in the frontmatter:
   - `id`: the next sequential ID (e.g., "B-001")
   - `title`: the provided title
   - `severity`: the provided severity
   - `status`: "open"
   - `created`: output of `date +%Y-%m-%d`
   - `source_branch`: the provided branch for task-regression bugs, or leave blank for existing-defect bugs
7. Fill in the Summary, Reproduction Status, Evidence, Reproduction Steps, Expected Behavior, Actual Behavior, Environment, Related, Suspected Area, and Fix Verification sections from the intake details.
8. If reproduction is not yet confirmed, still create the bug, but explicitly record what evidence exists and the first diagnostic step the Developer should try.
9. Leave Diagnosis Log, Work Log, and Review sections empty except for their instructional comments.
10. Confirm the file was created in `project/bugs/open/`.
