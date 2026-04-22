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
| `dev` | Integration target | The integration procedure merges task branches here; the Integrator handles manual merges and conflicts; Planners, Reviewers, and Architects commit docs here |
| `task/T-NNN-short-description` | Single task implementation | Implementer only |

**Rules:**
- No automated role ever commits to `main`.
- `dev` receives merge commits from the integration procedure or the Integrator role (code), and direct commits from non-Implementer roles (docs/specs/task files — no source code).
- Implementer always works on a task branch, never on `dev`.
- Task branches are created when the implementer picks up a task and deleted after successful integration into `dev`.

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
| **Planner** | Each spec or task file is finalized | `dev` |
| **Implementer** | After each TDD red→green→refactor cycle; once more before the final Work Log entry | `task/T-NNN-…` |
| **Reviewer** | After writing review verdict (task file only) | `dev` |
| **Architect** | After producing an ADR or amendment | `dev` |
| **Integrator** | One merge commit per task branch merged into `dev` | `dev` |

## Hard Rules

- No `--no-verify`. Fix the hook failure instead.
- No `--force` or `--force-with-lease` on shared branches (`dev`, `main`).
- No amending commits that have already been pushed.
- Never commit secrets, `.env` files, or credentials.
