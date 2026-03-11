---
title: "Setup Guide — Starting a New Project"
status: approved
created: 2026-03-10
---

# Setup Guide — Starting a New Project

This guide walks you through bootstrapping a new project using the AI team framework.

## Prerequisites

- A git repository for your new project.
- Claude Code (or another AI agent platform that reads `CLAUDE.md`).

## Quick Path

If you have Claude Code available, run `/bootstrap-project` inside your new repo. It will create the directory structure, copy templates, and generate a starter CLAUDE.md. Then skip to Step 5 below.

## Manual Setup

### Step 1: Create the Directory Structure

In your new project root, create these directories:

```bash
mkdir -p specifications/archive
mkdir -p tasks/pending tasks/in-progress tasks/completed tasks/blocked
mkdir -p bugs/open bugs/resolved
mkdir -p decisions
mkdir -p templates
mkdir -p docs/architecture docs/guidelines docs/processes docs/guides
mkdir -p .claude/agents
mkdir -p .claude/skills
```

Add `.gitkeep` files to keep empty directories in git:

```bash
for dir in specifications/archive tasks/pending tasks/in-progress tasks/completed tasks/blocked bugs/open bugs/resolved; do
  touch "$dir/.gitkeep"
done
```

### Step 2: Copy the Framework Files

Copy the following files from this repository into your new project, preserving the directory structure:

**Templates (bundled as skill assets):**
- `.claude/skills/new-spec/assets/TEMPLATE-specification.md`
- `.claude/skills/new-task/assets/TEMPLATE-task.md`
- `.claude/skills/new-bug/assets/TEMPLATE-bug.md`
- `.claude/skills/new-adr/assets/TEMPLATE-adr.md`
- `.claude/skills/write-plan/assets/roadmap.md`
- `.claude/skills/tdd/assets/test-plan.md`
- `.claude/skills/tdd/assets/test-report.md`
- `templates/handoff-note.md`
- `.claude/skills/status-report/assets/progress-report.md`

**Agent definitions (copy to `.claude/agents/`):**
- `TEMPLATE-agent.md`
- `planner.md`
- `architect.md`
- `implementer.md`
- `reviewer.md`
- `integrator.md`

**Skill definitions (copy to `.claude/skills/<name>/SKILL.md`):**
- `brainstorm`, `write-plan`, `code-review`, `tdd`, `debug`, `conflict-resolution`
- `new-spec`, `new-task`, `new-bug`, `new-adr`, `status-report`, `bootstrap-project`

**Process and guidelines docs (copy as-is):**
- `docs/processes/workflow-overview.md`
- `docs/processes/quality-gates.md`
- `docs/processes/escalation-procedure.md`
- `docs/guidelines/coding-standards.md`
- `docs/guidelines/review-checklist.md`
- `docs/guidelines/markdown-conventions.md`
- `docs/architecture/system-overview.md`
- `docs/architecture/component-map.md`

### Step 3: Create Your Project's CLAUDE.md

Create a `CLAUDE.md` in your project root. Start with this structure and customize the first section:

```markdown
# [Your Project Name]

> **Project purpose:** [One-sentence description of what this project builds.]

---

## Repository Map

| Folder | Purpose |
|---|---|
| `specifications/` | Technical specifications for features and systems |
| `tasks/` | Task tracking: `pending/`, `in-progress/`, `completed/`, `blocked/` |
| `bugs/` | Bug reports: `open/`, `resolved/` |
| `decisions/` | Architecture Decision Records (ADRs) |
| `templates/` | Reusable document formats |
| `docs/` | Architecture, guidelines, and process documentation |
| `.claude/agents/` | Agent role definitions |
| `.claude/skills/` | Reusable skill definitions (each as `<name>/SKILL.md`) |
| `src/` | Source code (adjust to your project layout) |
| `tests/` | Test files (adjust to your project layout) |

---

## How to Work Here

- Use TEMPLATE files when creating new documents.
- All documents use Markdown with YAML frontmatter.
- Tasks move between directories: `pending/` → `in-progress/` → `completed/` or `blocked/`.
- Architecture decisions require ADRs in `decisions/`.
- Documents must be self-contained and readable on their own.

## Tech Stack

- **Language:** [e.g., Python 3.11+, TypeScript 5.x]
- **Framework:** [e.g., FastAPI, Next.js]
- **Test framework:** [e.g., pytest, vitest]
- **Build command:** `[e.g., npm run build]`
- **Test command:** `[e.g., pytest tests/]`
- **Lint command:** `[e.g., ruff check .]`

## Conventions

- Filenames: lowercase with hyphens.
- ADRs: numbered sequentially (`NNN-short-title.md`).
- All docs: YAML frontmatter with `title`, `status`, `created`.
- Follow coding standards in `docs/guidelines/coding-standards.md`.
```

### Step 4: Customize for Your Stack

**`docs/guidelines/coding-standards.md`** — Add language-specific sections:
- For Python: add sections on type hints, import ordering, docstring style.
- For TypeScript: add sections on strict mode, interface vs. type, module resolution.
- For any language: specify your formatter, linter, and their configuration.

**`.claude/settings.json`** — Configure permissions for your project:
```json
{
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

### Step 5: Verify the Setup

Run these checks to confirm everything is in place:

1. **Directory structure**: All folders exist with templates in place.
   ```bash
   ls .claude/skills/new-spec/assets/TEMPLATE-specification.md
   ls .claude/skills/new-task/assets/TEMPLATE-task.md
   ls .claude/skills/new-bug/assets/TEMPLATE-bug.md
   ls .claude/skills/new-adr/assets/TEMPLATE-adr.md
   ```

2. **Slash commands work**: Run `/status-report` — it should produce an empty report with zero counts.

3. **Create a test task**: Run `/new-task` and verify a file appears in `tasks/pending/`.

4. **Delete the test task**: Remove the test file you just created.

### Step 6: Start Working

Your project is ready. The typical workflow is:

1. **Describe a feature** — write what you want built.
2. **Brainstorm** — the planner agent explores approaches and produces a specification (`/new-spec`).
3. **Approve the spec** — human reviews and approves (Gate 1).
4. **Break into tasks** — the planner decomposes the spec into atomic tasks.
5. **Approve the task plan** — human reviews tasks (Gate 2).
6. **Execute** — the implementer agent works through tasks sequentially using TDD.
7. **Review** — reviewer agent checks each completed task (Gate 3).
8. **Integrate** — integrator agent merges and runs integration tests (Gate 4).
9. **Final approval** — human approves the merged result (Gate 5).

For the full workflow details, see `docs/processes/workflow-overview.md`.
