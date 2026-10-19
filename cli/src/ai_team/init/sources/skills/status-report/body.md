# Status Report

Reporting is for humans and runs only on demand: the human invokes `/status-report`.
The development and bug-fix loops never invoke this skill — they end with a short run summary instead.

## Input Requirements

- **Project state** — `{{project_dir}}/specs/` and `{{project_dir}}/decisions/` in the repository; tasks, bugs, and change-requests in the local tracker, read through `ai-team list`.
- **Integration evidence** — completed task Work Logs, resolved bug Work Logs, or recent integration commits when available.
- **AI team CLI** — `ai-team status` and `ai-team report` are available.

## Procedure

### Step 1: Generate Inline Summary

Run the CLI status command from the repository root:

```bash
ai-team status
```

The command scans the project state directories, excludes template files and `.gitkeep`, reads primary artifact metadata, inspects integration evidence, and prints the inline Gate 5 summary.

### Step 2: Count Current State

Count specs and ADRs in `{{project_dir}}/specs/` and `{{project_dir}}/decisions/`, excluding template files and `.gitkeep`.
Count tasks and bugs by status with `ai-team list tasks --json` and `ai-team list bugs --json` (the `state` field is the frontmatter `status`):
- tasks: `planned`, `pending`, `in-progress`, `completed`, `blocked`, `cancelled`
- bugs: `open`, `in-progress`, `resolved`

### Step 3: Read Primary Artifacts

Read active specifications and list title, status, and latest amendment or version if present.
For each task with status `in-progress`, read the frontmatter and list ID, title, and assigned role.
For each task with status `blocked`, read the frontmatter and Work Log section to identify the blocking reason.
For each open bug with severity `critical` or `high`, list ID, title, and severity.

### Step 4: Inspect Integration Evidence

Inspect recent integration evidence from completed task Work Logs, resolved bug Work Logs, and recent integration commits when available.
Record the latest integration-test result or state that no integration evidence was found.

### Step 5: Produce Inline Summary

Use `ai-team status` output as the inline summary. If the command cannot run, manually present the report in this format:

```markdown
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

If there are blocked tasks or critical/high bugs, add a `Recommended Actions` section suggesting next steps.

### Step 6: Write Full Report (Only When Asked)

Skip this step unless the human explicitly asked for a report file. The inline summary is the default output.

When a file is requested, run the CLI report command from the repository root:

```bash
ai-team report
```

By default, it writes `{{project_dir}}/docs/reports/progress-report-[today's date].md` and creates `{{project_dir}}/docs/reports/` if needed.
The full report includes completed tasks, in-progress details, blocked items with action needed, bug listing, next actions, and risks or concerns.
`{{project_dir}}/docs/reports/` is ignored by the scaffolded `{{project_dir}}/.gitignore`, so the file does not dirty the working tree.
Tell the human the file path. Commit it only if the human asks and the project tracks reports.

## Output Format

- **Inline summary:** Gate 5 status summary using the markdown structure above.
- **Report file:** `{{project_dir}}/docs/reports/progress-report-[today's date].md`, only when the human asked for one.
- **Evidence:** latest integration result or a clear statement that no integration evidence was found.

## Quality Criteria

- Counts exclude templates and `.gitkeep`.
- Critical and high severity bugs are explicitly listed.
- Blocked tasks include the blocking reason when one is recorded.
- The latest integration evidence is recorded or explicitly marked as not found.
- The report gives the human enough context for Gate 5 final merge sign-off.

## Common Pitfalls

- Treating Gate 5 as a code review instead of a status sign-off.
- Omitting critical or high severity open bugs.
- Reporting green status without integration evidence.
- Writing a report file nobody asked for — the inline summary is the default output.
