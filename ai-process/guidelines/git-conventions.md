---
title: "Git Conventions"
status: approved
created: 2026-03-25
---

# Git Conventions

These rules apply to all AI roles working within any project that uses this framework.
Project-specific commit scopes and any overrides belong in the project's own `CLAUDE.md`.

## Branch Model

| Branch | Purpose | Who touches it |
|---|---|---|
| `main` | Production-ready releases | Human only — never automated roles |
| `dev-agent` | Integration target | The integration procedure merges task branches here; the Integrator handles manual merges and conflicts; Planners, Reviewers, and Architects commit docs here |
| `task/T-NNN-short-description` | Single task implementation | Developer only |
| `bug/B-NNN-short-description` | Single bug diagnosis and fix | Developer only |

**Rules:**
- No automated role ever commits to `main`.
- `dev-agent` receives merge commits from the integration procedure or the Integrator role (code), and direct commits from non-Developer roles (docs/specs/task files — no source code).
- Developer always works on a task branch, never on `dev-agent`.
- Task branches are created when the Developer picks up a task and deleted after successful integration into `dev-agent`.
- Bug branches are created when the bug-fix loop picks up a bug.
  Existing-defect bug branches are based on `dev-agent`; task-regression bug branches are based on the bug report's `source_branch`.

## Commit Message Format

```
<type>(<component>): <description>
```

- **type** — `feat`, `fix`, `test`, `docs`, `chore`
- **component** — architecture area (project-specific; see project `CLAUDE.md`)
- **description** — imperative, lowercase, no period, ≤ 72 chars total

The branch name already carries task and role context — do not repeat it in the message.

**Examples:**
```
feat(db): add conversations table migration
fix(ui): correct sidebar active state color
test(api): cover SSE disconnection edge case
docs(specs): add phase2 boardroom role selection
chore(tasks): move T-004 to completed
```

## When Each Role Commits

| Role | Commits when | Branch |
|---|---|---|
| **Planner** | Each spec or task file is finalized | `dev-agent` |
| **Developer** | After each TDD red→green→refactor cycle; once more before the final Work Log entry | `task/T-NNN-…` or `bug/B-NNN-…` |
| **Reviewer** | After writing review verdict (task or bug file only) | `dev-agent` |
| **Architect** | After producing an ADR or amendment | `dev-agent` |
| **Integrator** | One merge commit per task or bug branch merged into its target branch | target branch |

## Hard Rules

- No `--no-verify`. Fix the hook failure instead.
- No `--force` or `--force-with-lease` on shared branches (`dev-agent`, `main`).
- No amending commits that have already been pushed.
- Never commit secrets, `.env` files, or credentials.
