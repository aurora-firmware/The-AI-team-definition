---
title: Local Work-Item Tracker
version: '0.1'
status: draft  # draft | review | approved | superseded
created: '2026-10-15'
author: planner
id: S-006
---

# Local Work-Item Tracker

<!--
This spec describes requirements and measurable criteria in prose.
It is not the implementation. Do not paste full configuration files,
build manifests, or implementation code into the sections below.
-->

## Purpose

Task and bug lifecycle state lives inside the project repository today: each state is a folder, every state change is a file move, and every move, Work Log, and Review Verdict is a commit on `dev-agent`.
Processing one task therefore costs about four lifecycle commits and six to eight branch switches on top of the actual work, and task-regression bugs need their content relayed by hand because their branch does not contain the bug file.
This spec moves tasks and bugs out of version control into a local tracker folder configured in `.ai-team.toml`, and makes the frontmatter `status` field the only source of lifecycle state.
When it is done, recording any lifecycle change — claim, Work Log, verdict, completion — produces no commit and no branch switch, and the only commits a task produces are its implementation commits and its merge commit.

This is phase 1 of moving task tracking out of the repository. Phase 2 (an external GitHub backend) is excluded below and depends on the CLI and skill seams this spec creates.

## Exclusions

- **GitHub or any other remote tracker backend.** Deferred to phase 2. This spec only ensures that skills reach tracker data through `ai-team` commands, so that a later backend does not change the skills a second time.
- **Moving specs, change-requests, ADRs, or docs.** They are design documents that belong next to the code and stay in the project directory under version control.
- **Sharing the tracker across machines or collaborators.** The tracker is local to one working copy. Making the tracker folder its own repository, or syncing it, is left to the human.
- **History of task and bug files.** Git history no longer records lifecycle changes. The Work Log and Review Verdict entries inside each file remain the record.
- **Changing the Work Log, Diagnosis Log, or Review Verdict formats.** Only where they are written changes, not what they contain.
- **Shared ID allocation for specs and change-requests.** Task and bug IDs come from the single tracker folder and stop colliding across planning branches; spec and change-request IDs keep today's allocation.

## Architecture

### Design Principles

- **One source of truth for state.** A work item's lifecycle state is its frontmatter `status` value. No folder, filename, or branch encodes state.
- **Outside version control, inside the workspace.** The tracker is never committed, survives branch switches untouched, and lives where a dev container mounts the workspace by default.
- **One tracker per repository.** Every git worktree of a repository resolves the same tracker folder, so a Developer working in a worktree and a loop working in the main checkout see the same state.
- **Skills never touch tracker paths directly.** Skills locate, create, and transition work items only through `ai-team` commands. Appending log or verdict text to a file whose path a command returned is allowed.
- **Existing projects migrate explicitly.** No command silently moves files out of a repository. Migration is one explicit command, and other commands warn while unmigrated files remain.

### System Diagram

```
 .ai-team.toml ──[tracker] dir──┐
                                ▼
 ai-team CLI ──────────► <tracker>/tasks/T-NNN-*.md   status: planned … completed
 (new, set-status,       <tracker>/bugs/B-NNN-*.md    status: open … resolved
  list, show, status,    <tracker>/archive/YYYY-MM/
  report, validate,               ▲
  archive, migrate)               │ append Work Log / Verdict to returned path
                                  │
 skills (loops, integrate, ───────┘        project repo (git)
 code-review, spec-breakdown)  ───────►   specs, CRs, ADRs, source, tests
```

### Responsibility Separation

| Component | Responsibility | Interface notes |
|---|---|---|
| Tracker configuration | Resolve the tracker folder for the current repository | Reads `.ai-team.toml`; exposes the resolved absolute path to every command |
| Work-item store | Create, find, transition, archive tasks and bugs by ID | Field-based state; one flat folder per kind |
| CLI commands | Human and skill entry points for tracker data | Existing command names keep working; state filters read the `status` field |
| Migration | Move legacy folder-based items into the tracker | One explicit command; idempotent |
| Process skills and docs | Drive lifecycle through CLI commands, without lifecycle commits | Loops, integrate, code-review, spec-breakdown, git-conventions, workflow docs |

## Components

### Component 1: Tracker Configuration
- **Purpose:** resolve one tracker folder per repository from `.ai-team.toml`, shared by all worktrees.
- **Estimated size:** small.
- **Interfaces:** consumed by every CLI command; exposed through a command that prints the resolved path.

### Component 2: Field-Based Work-Item Store
- **Purpose:** store tasks and bugs in flat per-kind folders with state in the `status` field.
- **Estimated size:** medium.
- **Interfaces:** ID allocation, lookup by ID, status transition, archive.

### Component 3: CLI Command Updates
- **Purpose:** make `task`, `bug`, `list`, `show`, `status`, `report`, `validate`, `archive`, `init`, and `check-layout` use the tracker and the `status` field.
- **Estimated size:** medium.
- **Interfaces:** existing command names and JSON output shapes; new generic status-transition and path commands; new `planned` and `cancelled` task states.

### Component 4: Migration
- **Purpose:** move legacy `tasks/<state>/` and `bugs/<state>/` files into the tracker.
- **Estimated size:** small.
- **Interfaces:** one `ai-team tracker migrate` command and a warning from other commands while legacy files remain.

### Component 5: Process Skills and Documentation
- **Purpose:** remove lifecycle commits, the "canonical on `dev-agent`" rule, and content relaying from the process.
- **Estimated size:** medium.
- **Interfaces:** `dev-loop`, `bug-loop`, `integrate`, `code-review`, `tdd`, `debug`, `new-task`, `new-bug`, `spec-breakdown`, `status-report`, `git-conventions`, the agent role files, and `ai-process/` docs.

## Workflow

1. `ai-team init` writes a `[tracker]` section with the default folder, creates the folder, and makes git ignore it. ★ Existing projects run `ai-team tracker migrate` once and commit the removal of the legacy folders.
2. `spec-breakdown` creates tasks with status `planned` on the planning branch's behalf; the tracker is shared, so the tasks exist immediately but stay invisible to `/dev-loop`.
3. After Gate 2 and the planning-branch merge, `spec-breakdown` sets that plan's tasks to `pending`. If a spec or change-request is abandoned, its planned tasks become `cancelled`.
4. `/dev-loop` lists `pending` tasks, sets the chosen one to `in-progress`, and creates the task branch. No commit.
5. The loop appends the Developer's Work Log and the Reviewer appends the Review Verdict to the task file, from whatever branch is checked out. No commit, no switch.
6. `integrate` reads the verdict from the task file, merges, and on success sets the task to `completed`. The merge commit is the only commit on `dev-agent`.
7. The bug loop follows the same pattern. Task-regression bug branches no longer need bug content relayed, because the bug file is outside every branch.
8. ★ The human runs `/status-report` on demand; it reads state from the tracker.

## Configuration Requirements

**Tracker folder**
- **What must exist:** a `dir` setting in a `[tracker]` section of `.ai-team.toml`.
- **Where it lives:** the repository's `.ai-team.toml`, beside the existing `[project]` section.
- **Constraints:** a relative path resolves against the main working tree of the repository, not the current worktree; an absolute path or a `~` path is used as given. Default value: `.ai-team/tracker`.
- **Missing-value behaviour:** when the section or key is absent, commands use the default folder. When the folder does not exist, creating a work item creates it; reading commands treat it as empty.

**Git ignore**
- **What must exist:** an ignore rule covering the tracker folder whenever it lies inside the repository.
- **Where it lives:** the repository's root `.gitignore`.
- **Constraints:** `ai-team init` and `ai-team tracker migrate` add the rule idempotently and never remove existing rules.
- **Missing-value behaviour:** `check-layout` reports a finding when the tracker folder is inside the repository and not ignored.

## Measurable Success Criteria

- After `ai-team init` in an empty git repository, the project directory contains no `tasks/` or `bugs/` folders, the tracker folder exists, and `git check-ignore` succeeds for it.
- Creating a task, moving it through every status, and appending text to it leaves `git status --porcelain` empty.
- `ai-team list tasks --state <s>` returns exactly the tasks whose `status` field is `<s>`, and its JSON shape is unchanged.
- Run from two worktrees of the same repository, `ai-team tracker path` prints the same absolute path.
- `ai-team validate` reports a finding for any task or bug whose `status` is not one of the allowed values, and no longer reports folder/status mismatches.
- On a project with legacy folders, `ai-team tracker migrate` moves every task and bug file into the tracker, keeps file contents unchanged, and sets `status` from the folder only where the two disagreed. A second run reports nothing to do. Until migration, every other tracker command prints a warning naming the legacy folders.
- In the generated `dev-loop`, `bug-loop`, `integrate`, and `code-review` skills, no step commits a task or bug file, and no step switches branches to record lifecycle state.
- The full CLI test suite passes, including tests updated from folder-based to field-based state.

## Implementation Order

1. **Tracker core** — configuration, worktree-aware path resolution, field-based store, ID allocation. Observable: the store unit tests pass.
2. **CLI commands** — all commands on the tracker, new status-transition and path commands, `init` and `check-layout` changes. Depends on phase 1. Observable: the success criteria for init, list, validate, and worktrees pass.
3. **Migration** — the migrate command and the legacy warning. Depends on phase 2. Observable: the migration criterion passes on a copy of this repository's own `docs/ai-team/`.
4. **Process skills and docs** — skills, agents, git conventions, workflow docs, regenerated scaffolds. Depends on phase 2. Observable: the generated-skill criterion passes.

## Amendment Log

