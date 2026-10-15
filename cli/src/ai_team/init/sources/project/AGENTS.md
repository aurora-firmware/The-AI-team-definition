# Project Guidance for Agents

This `project/` directory is the canonical workspace for project artifacts used
by agent workflows.

## Folder Purpose

- `specs/` contains approved specs that define what to build.
- `decisions/` contains ADRs and design amendments.
- `docs/reports/` contains status reports generated on demand; it is git-ignored by default.
- `docs/` contains project-local docs for commands, conventions, and policies.

Work items — tasks, bugs, and change-requests — are not stored here. They live in the local
tracker (`ai-team tracker path`), outside version control, and agents read and
change them only through `ai-team` commands.

Agents should update these folders through the documented workflow so project
state remains consistent across roles.
