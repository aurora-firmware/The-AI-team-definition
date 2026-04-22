---
name: status-report
description: Generate a Gate 5 project status report by scanning specs, tasks, bugs, decisions, and integration evidence. Use when the development or bug-fix loop needs a summary, or when a human needs final merge sign-off context.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Bash
---

Generate a project status report.

1. Scan the following directories and count files (excluding TEMPLATE files and .gitkeep):
   - `project/specs/` — active specifications
   - `project/tasks/pending/` — pending tasks
   - `project/tasks/in-progress/` — tasks in progress
   - `project/tasks/completed/` — completed tasks
   - `project/tasks/blocked/` — blocked tasks
   - `project/bugs/open/` — open bugs
   - `project/bugs/in-progress/` — bugs being fixed
   - `project/bugs/resolved/` — resolved bugs
   - `project/decisions/` — ADRs

2. Read the active specifications and list title, status, and latest amendment or version if present.

3. For each task in `project/tasks/in-progress/`, read the frontmatter and list: ID, title, assigned role.

4. For each task in `project/tasks/blocked/`, read the frontmatter and list: ID, title, and check the Work Log section for the blocking reason.

5. For each bug in `project/bugs/open/` with severity "critical" or "high", list: ID, title, severity.

6. Inspect recent integration evidence from completed task Work Logs, resolved bug Work Logs, and recent integration commits when available. Record the latest integration-test result or state that no integration evidence was found.

7. Present the report in this format:

```
## Status Report — [today's date]

### Summary
- Active specs: N
- Pending tasks: N
- In progress: N
- Completed: N
- Blocked: N
- Open bugs: N (X critical/high)
- Bugs in progress: N
- ADRs: N
- Latest integration result: [result or not found]

### Specifications
[list active specs with title and status]

### In Progress
[list of in-progress tasks with ID, title, role]

### Blocked
[list of blocked tasks with ID, title, blocking reason]

### Critical/High Bugs
[list of critical and high severity open bugs]
```

8. If there are blocked tasks or critical/high bugs, add a "Recommended Actions" section suggesting next steps.

9. After displaying the inline summary above, generate a full written report using the template at `.claude/skills/status-report/assets/progress-report.md`.
   Save it to `project/docs/reports/progress-report-[today's date].md`.
   Create `project/docs/reports/` first if it does not exist.
   The full report includes: completed tasks table, in-progress details, blocked items with action needed, bug listing, next actions, and risks/concerns.
