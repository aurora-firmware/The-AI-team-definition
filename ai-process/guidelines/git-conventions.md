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
| `dev-agent` | Integration target and canonical lifecycle state | The integration procedure merges task branches here; the Integrator handles manual merges and conflicts; the Planner merges planning branches here after Gate 2; Reviewers, Architects, and active loops commit docs and lifecycle state here |
| `plan/S-NNN-short-description` or `plan/CR-NNN-short-description` | Planning branch for one spec or change-request: the spec or change-request, spec amendments, ADRs raised by its consistency review, and its task files | Planner and Architect only — no source code |
| `task/T-NNN-short-description` | Single task implementation branch | Developer only for source, tests, and project artifacts |
| `bug/B-NNN-short-description` | Single bug diagnosis and fix branch | Developer only for source, tests, and project artifacts |

**Rules:**
- No automated role ever commits to `main`.
- `dev-agent` receives merge commits from the integration procedure or the Integrator role (code), and direct commits from non-Developer roles and active loops (docs/specs/task files/bug files — no direct source code).
- Developer always works on a task branch, never on `dev-agent`.
- Task branches are created when the Developer picks up a task and deleted after successful integration into `dev-agent`.
- Bug branches are created when the bug-fix loop picks up a bug.
  Existing-defect bug branches are based on `dev-agent`; task-regression bug branches are based on the bug report's `source_branch`.
- Planning branches are created from `dev-agent` when a spec or change-request is created. Every planning artifact for that work is committed there, never directly on `dev-agent`.
  The Planner merges the planning branch into `dev-agent` with `--no-ff` only after Gate 2 passes, then deletes it with `git branch -d`.
  `dev-agent` therefore never carries a spec amendment without the task plan that implements it. Abandoning a spec or change-request means the human deletes its planning branch.
- Task and bug files are canonical on `dev-agent`. Implementation branches may contain copies for context, but lifecycle state is read from and committed to `dev-agent`.
- Task-regression bug branches may not contain the bug report file because they are based on preserved task branches. The bug-fix loop must pass canonical bug content from `dev-agent` to the Developer and Reviewer, and record their log and verdict entries back on `dev-agent`.

### Opening a Planning Branch

The skill that creates a spec or change-request opens its planning branch:

1. Run the before-point Workspace Hygiene check, then `git checkout dev-agent`.
2. Run `git branch --list 'plan/*'`. IDs are allocated from the files on the current branch, so two open planning branches can allocate the same spec, change-request, or task ID.
   If another planning branch is open, stop and ask the human whether to merge or abandon it first, or to continue and renumber at merge time.
3. Run the CLI command that allocates the artifact ID. The new file is untracked.
4. Run `git checkout -b plan/<id>-<slug>`. The untracked file carries over; commit it there.

When an approved spec already on `dev-agent` needs a breakdown and has no planning branch, open one the same way and skip step 3.

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
| **Planner** | Each spec, change-request, amendment, or task file is finalized | `plan/…` |
| **Planner** | One merge commit per planning branch after Gate 2 passes | `dev-agent` |
| **Developer** | After each implementation cycle for source, tests, and project artifacts | `task/T-NNN-…` or `bug/B-NNN-…` |
| **Development Loop / Bug-Fix Loop** | After lifecycle moves and after recording Developer Diagnosis Log or Work Log handoffs | `dev-agent` |
| **Reviewer** | After writing Review Verdict entries to canonical task or bug files | `dev-agent` |
| **Architect** | After producing an ADR or amendment | `plan/…` when raised during planning; otherwise `dev-agent` |
| **Integrator** | One merge commit per task or bug branch merged into its target branch | target branch |

<!-- Implementation-layer copy: .claude/skills/git-conventions/SKILL.md — changes must be made to both files atomically. -->

## Workspace Hygiene

A dirty working tree must never block a procedure, and no procedure may leave one behind.
Every orchestrating procedure (`dev-loop`, `bug-loop`, `integrate`, `spec-breakdown`) runs the hygiene check:

- **Before** — at startup and before every branch switch.
- **After** — after every merge, and before reporting the procedure complete or stopped.

### Hygiene Check

1. Run `git status --porcelain --untracked-files=all`. Empty output means the tree is clean — continue.
2. Classify each entry and act on it:

| Entry | Action |
|---|---|
| Generated artifact — test or tool caches, coverage output, build output, logs, generated reports, merge leftovers such as `*.orig` | Add the narrowest matching pattern to the repository `.gitignore` and commit it on the current branch: `chore(gitignore): ignore <pattern>`. Never ignore source, test, spec, task, bug, or decision files. |
| Produced by the current step and inside its scope — for example a bug file filed by this step | Commit it on the branch the owning rule names. |
| Anything else — unknown untracked files, or tracked changes this step did not make | Park it: `git stash push --include-untracked -m "ai-team: <work-item or procedure> parked at <step>"`. |

3. Re-run step 1. The tree must be clean before continuing.

### Restoring Parked Changes

When the procedure that parked changes ends — on success or on a stop — return to the branch where they were parked and restore them:

1. Find the entry by its message in `git stash list` and run `git stash pop stash@{n}` for that entry only.
2. If the pop conflicts, stop and report. Git keeps the stash entry on conflict; leave it there for the human.
3. List every park and restore in the procedure's final report, so the human can see what was moved.

### Never

- Never run `git clean`, delete untracked files, or discard changes the current step did not make (`git restore`, `git checkout -- <path>`).
- Never run `git stash drop` or `git stash clear`.
- Never park changes while a merge, rebase, or revert is in progress — finish or abort that operation first.

## Hard Rules

- No `--no-verify`. Fix the hook failure instead.
- No `--force` or `--force-with-lease` on shared branches (`dev-agent`, `main`).
- No amending commits that have already been pushed.
- Never commit secrets, `.env` files, or credentials.
- Never discard or delete work the current step did not create — park it as described in Workspace Hygiene.
- No routine forced branch deletion (`git branch -D`) during integration. Use safe deletion (`git branch -d`) only. If `-d` is refused, stop and report instead of forcing deletion.
