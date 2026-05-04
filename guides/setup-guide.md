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

## Setup Steps

### Step 1: Create the Directory Structure

In your new project root, create these directories:

```bash
mkdir -p project/specs/archive
mkdir -p project/tasks/pending project/tasks/in-progress project/tasks/completed project/tasks/blocked
mkdir -p project/bugs/open project/bugs/in-progress project/bugs/resolved
mkdir -p project/decisions
mkdir -p project/docs
mkdir -p .claude/agents
mkdir -p .claude/skills
# Optional for OpenAI Codex compatibility:
mkdir -p .codex
```

Add `.gitkeep` files to keep empty directories in git:

```bash
for dir in project/specs/archive project/tasks/pending project/tasks/in-progress project/tasks/completed project/tasks/blocked project/bugs/open project/bugs/in-progress project/bugs/resolved; do
  touch "$dir/.gitkeep"
done
touch project/docs/coding_guidelines.md
```

### Step 2: Copy the Framework Files

Copy the following files from this repository into your new project, preserving the directory structure:

**Templates (bundled as skill assets):**
- `.claude/skills/new-spec/assets/TEMPLATE-specification.md`
- `.claude/skills/new-task/assets/TEMPLATE-task.md`
- `.claude/skills/new-bug/assets/TEMPLATE-bug.md`
- `.claude/skills/new-adr/assets/TEMPLATE-adr.md`
- `.claude/skills/tdd/assets/test-plan.md`
- `.claude/skills/tdd/assets/test-report.md`
- `.claude/skills/status-report/assets/progress-report.md`

**Agent definitions (copy to `.claude/agents/`):**
- `planner.md`
- `architect.md`
- `developer.md`
- `reviewer.md`
- `integrator.md`

**Skill definitions (copy to `.claude/skills/<name>/SKILL.md`):**
- `brainstorm`, `spec-breakdown`, `spec-breakdown-review`, `code-review`, `tdd`, `debug`, `merge-conflicts`
- `dev-loop`, `integrate`, `bug-loop`
- `escalation-review`, `git-conventions`
- `new-spec`, `new-task`, `new-bug`, `new-adr`, `status-report`

If you use OpenAI Codex, keep skills available under `.codex/skills` and define project-scoped custom agents as `.codex/agents/*.toml`. Those TOML files should translate each Claude-style agent into Codex's custom-agent schema: `name`, `description`, and `developer_instructions`, with optional Codex-native settings such as `model`, `model_reasoning_effort`, and `sandbox_mode`.

### Step 3: Create Your Project's CLAUDE.md

Create a `CLAUDE.md` in your project root. Start with this structure and customize the first section:

```markdown
# [Your Project Name]

> **Project purpose:** [One-sentence description of what this project builds.]

---

## Repository Map

| Folder | Purpose |
|---|---|
| `project/specs/` | Technical specifications for features and systems |
| `project/tasks/` | Task tracking: `pending/`, `in-progress/`, `completed/`, `blocked/` |
| `project/bugs/` | Bug reports: `open/`, `in-progress/`, `resolved/` |
| `project/decisions/` | Architecture Decision Records (ADRs) |
| `project/docs/` | Project-specific guidance for commands, coding conventions, and operations |
| `.claude/agents/` | Agent role definitions |
| `.claude/skills/` | Reusable skill definitions (each as `<name>/SKILL.md`) |
| `[source path]` | Source code location for this project |
| `[test path]` | Test file location for this project |

---

## How to Work Here

- Use TEMPLATE files when creating new documents.
- All documents use Markdown with YAML frontmatter.
- Tasks move between directories: `pending/` → `in-progress/` → `completed/` or `blocked/`.
- Architecture decisions require ADRs in `project/decisions/`.
- Documents must be self-contained and readable on their own.

## Tech Stack

- **Language/runtime:** [project-specific]
- **Frameworks/libraries:** [project-specific]
- **Test framework:** [project-specific]
- **Build command:** `[project-specific command]`
- **Test command:** `[project-specific command]`
- **Lint command:** `[project-specific command]`
- **Run/dev command:** `[project-specific command]`
- **Additional verification:** [project-specific checks]

## Conventions

- Filenames: lowercase with hyphens.
- ADRs: numbered sequentially (`NNN-short-title.md`).
- All docs: YAML frontmatter with `title`, `status`, `created`.
- Follow coding standards in `ai-process/guidelines/coding-standards.md`.
- Follow project-specific coding rules in `project/docs/coding_guidelines.md`.
```

### Step 4: Customize for Your Stack

**`project/docs/coding_guidelines.md`** — Add project-specific rules:
- Stack and framework conventions.
- Formatter, linter, and dependency policy.
- Naming conventions and file layout.
- Testing conventions and where test fixtures live.
- Any commands not already listed in `CLAUDE.md`.

Keep `ai-process/guidelines/coding-standards.md` as the framework's general, language-agnostic baseline unless you intentionally fork the process.

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

3. **Create a test task**: Run `/new-task` and verify a file appears in `project/tasks/pending/`.

4. **Delete the test task**: Remove the test file you just created.

5. **Project guidance exists**: Confirm `CLAUDE.md` names the project commands and points to `project/docs/coding_guidelines.md` or equivalent project-local guidance.

### Step 6: Start Working

Your project is ready. The typical workflow is:

1. **Describe a feature** — write what you want built.
2. **Brainstorm** — the planner agent explores approaches and produces a specification (`/new-spec`).
3. **Approve the spec** — human reviews and approves (Gate 1).
4. **Break into tasks** — the planner decomposes the spec into atomic tasks.
5. **Run Gate 2 preflight** — the architect validates the task plan before development starts.
6. **Run `/dev-loop`** — autonomously implements, reviews, and integrates each task. Gate 3 code review and Gate 4 integration verification happen inside the loop.
7. **Fix bugs with `/bug-loop`** — when open bugs exist, the loop diagnoses first, then fixes, reviews, and integrates.
8. **Final approval** — human approves the merge from `dev-agent` to `main` (Gate 5).

For the full workflow details, see `ai-process/processes/workflow-overview.md`.
