---
name: status-report
description: Generate a project status report by scanning task and bug directories
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
---

Generate a project status report.

1. Scan the following directories and count files (excluding TEMPLATE files and .gitkeep):
   - `project/tasks/pending/` — pending tasks
   - `project/tasks/in-progress/` — tasks in progress
   - `project/tasks/completed/` — completed tasks
   - `project/tasks/blocked/` — blocked tasks
   - `project/bugs/open/` — open bugs
   - `project/bugs/in-progress/` — bugs being fixed
   - `project/bugs/resolved/` — resolved bugs

2. For each task in `project/tasks/in-progress/`, read the frontmatter and list: ID, title, assigned role.

3. For each task in `project/tasks/blocked/`, read the frontmatter and list: ID, title, and check the Notes section for blocking reason.

4. For each bug in `project/bugs/open/` with severity "critical" or "high", list: ID, title, severity.

5. Present the report in this format:

```
## Status Report — [today's date]

### Summary
- Pending tasks: N
- In progress: N
- Completed: N
- Blocked: N
- Open bugs: N (X critical/high)
- Bugs in progress: N

### In Progress
[list of in-progress tasks with ID, title, role]

### Blocked
[list of blocked tasks with ID, title, blocking reason]

### Critical/High Bugs
[list of critical and high severity open bugs]
```

6. If there are blocked tasks or critical bugs, add a "Recommended Actions" section suggesting next steps.

7. After displaying the inline summary above, generate a full written report using the template at `.claude/skills/status-report/assets/progress-report.md`.
   Save it to `ai-process/progress-report-[today's date].md`.
   The full report includes: completed tasks table, in-progress details, blocked items with action needed, bug listing, next actions, and risks/concerns.
