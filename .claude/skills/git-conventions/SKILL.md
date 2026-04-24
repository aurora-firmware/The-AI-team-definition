---
name: git-conventions
description: Branch model, commit message format, per-role commit rules, and hard git rules for the AI team. Use whenever any role commits, merges, or creates a branch — consult this skill for the authoritative branch model and commit format.
allowed-tools: Read
---

# Git Conventions

These rules apply to all AI roles working within any project that uses this framework.
Project-specific commit scopes and any overrides belong in the project's own `CLAUDE.md`.

## Branch Model

| Branch | Purpose | Who touches it |
|---|---|---|
| `main` | Production-ready releases | Human only — never automated roles |
| `dev-agent` | Integration target and canonical lifecycle state | The integration procedure merges task branches here; the Integrator handles manual merges and conflicts; Planners, Reviewers, Architects, and active loops commit docs and lifecycle state here |
| `task/T-NNN-short-description` | Single task implementation branch | Developer only for source, tests, and project artifacts |
| `bug/B-NNN-short-description` | Single bug diagnosis and fix branch | Developer only for source, tests, and project artifacts |

**Rules:**
- No automated role ever commits to `main`.
- `dev-agent` receives merge commits from the integration procedure or the Integrator role (code), and direct commits from non-Developer roles and active loops (docs/specs/task files/bug files — no direct source code).
- Developer always works on a task branch, never on `dev-agent`.
- Task branches are created when the Developer picks up a task and deleted after successful integration into `dev-agent`.
- Bug branches are created when the bug-fix loop picks up a bug.
  Existing-defect bug branches are based on `dev-agent`; task-regression bug branches are based on the bug report's `source_branch`.
- Task and bug files are canonical on `dev-agent`. Implementation branches may contain copies for context, but lifecycle state is read from and committed to `dev-agent`.
- Task-regression bug branches may not contain the bug report file because they are based on preserved task branches. The bug-fix loop must pass canonical bug content from `dev-agent` to the Developer and Reviewer, and record their log and verdict entries back on `dev-agent`.

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
| **Developer** | After each implementation cycle for source, tests, and project artifacts | `task/T-NNN-…` or `bug/B-NNN-…` |
| **Development Loop / Bug-Fix Loop** | After lifecycle moves and after recording Developer Diagnosis Log or Work Log handoffs | `dev-agent` |
| **Reviewer** | After writing Review Verdict entries to canonical task or bug files | `dev-agent` |
| **Architect** | After producing an ADR or amendment | `dev-agent` |
| **Integrator** | One merge commit per task or bug branch merged into its target branch | target branch |

## Hard Rules

- No `--no-verify`. Fix the hook failure instead.
- No `--force` or `--force-with-lease` on shared branches (`dev-agent`, `main`).
- No amending commits that have already been pushed.
- Never commit secrets, `.env` files, or credentials.

## Quality Criteria

- Every commit message parses as `<type>(<component>): <description>`.
- Each role commits only on the branch(es) listed for it above.
- Branch names use the exact `task/T-NNN-...` or `bug/B-NNN-...` prefix.
- No commit to `main` is ever produced by an automated role.
- No commit uses `--no-verify`, `--force`, or amends a pushed commit.

## Common Pitfalls

- Repeating the task or bug ID in the commit message — the branch name already carries it.
- Committing implementation code to `dev-agent` — implementation belongs on a task or bug branch.
- Merging lifecycle-file edits from an implementation branch — task and bug files are canonical on `dev-agent`.
- Using `--no-verify` to bypass a hook failure — fix the underlying cause instead.
