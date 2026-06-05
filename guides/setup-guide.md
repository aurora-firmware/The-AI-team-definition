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
- `pipx` installed (`python -m pip install --user pipx` if needed).

## Setup Steps

### Step 1: Install the `ai-team` CLI

Download the wheel from the project's GitHub Releases page:

```bash
pipx install https://github.com/<org>/<repo>/releases/download/<tag>/ai_team-<version>-py3-none-any.whl
```

Install from a local wheel build while developing this repository:

```bash
pipx install /path/to/The-AI-team-definition/cli/dist/*.whl
```

Initialize the AI team structure in your target repository:

```bash
ai-team init . --tools claude --no-interactive
```

Daily commands you will use most often:

```bash
ai-team status
ai-team task new
ai-team task start <task-id>
ai-team validate
ai-team report
```

For a full usage walkthrough see [`cli/docs/usage.md`](../cli/docs/usage.md); for an exhaustive command and flag reference see [`cli/docs/commands.md`](../cli/docs/commands.md).

### Release hygiene

Public releases must not include secrets, tokens, passwords, environment
variable values, usernames, emails, machine paths, hostnames, or any other data
that could identify or compromise this machine. Before publishing a release,
scan newly added docs, examples, and scratch files for sensitive material and
replace it with placeholders if needed.

### Step 2: Create the Directory Structure

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

### Step 3: Export the Framework Files

Run `ai-team init` to export the bundled agent definitions, skill definitions, and templates into your project:

```bash
ai-team init . --tools claude --no-interactive
```

This exports from the CLI package scaffold sources:

- **Agent definitions** into `.claude/agents/`
- **Skill definitions** into `.claude/skills/<name>/SKILL.md`
- **Templates** as skill assets under `.claude/skills/*/assets/`
- **Project state directories** under `project/`
- **`.ai-team.toml`** configuration file

For OpenAI Codex compatibility, add `--tools codex` (or `--tools claude,codex`) to also export `.codex/agents/*.toml` Codex agent files. Those TOML files translate each Claude-style agent into Codex's custom-agent schema: `name`, `description`, and `developer_instructions`, with optional Codex-native settings such as `model`, `model_reasoning_effort`, and `sandbox_mode`.

The `ai-process/` specification documents are not exported. They live in the AI team definition meta-repository and serve as the authoritative spec for the rules the agents and skills implement. You do not need them in your project.

### Step 4: Create Your Project's CLAUDE.md and AGENTS.md

Create a `CLAUDE.md` and `AGENTS.md` in your project root. The test instructions in these files are especially important: `dev-loop` starts baseline command discovery from root project guidance, then follows clear references to project-local docs such as `project/docs/coding_guidelines.md`, README files, build configuration, or other documented test instructions. If no automated baseline command is documented, or the available guidance is ambiguous, `dev-loop` will ask the human for the intended command or for explicit confirmation that no automated baseline test is available before claiming a task.

`ai-team init` can scaffold starter versions of both root guidance files when they are missing. Run `ai-team init . --tools claude` interactively and answer the prompts, or pass `--create-root-guidance` with `--no-interactive` to create them non-interactively. Existing root guidance files are never overwritten unless `--force` is also set.

Start your `CLAUDE.md` with this structure and customize the first section:

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

### Step 5: Customize for Your Stack

**Baseline test instructions** — Fill in the command agents should run to execute the test suite. Put it in root guidance (`CLAUDE.md` or `AGENTS.md`) or clearly reference a project-local doc that contains it. `dev-loop` reads project guidance at startup; if the command is missing or ambiguous, the loop asks for human clarification before claiming a task. If your project has no automated tests, state that explicitly so the loop can record the confirmation and continue.

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

### Step 6: Verify the Setup

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

5. **Project guidance exists**: Confirm root guidance has a real baseline test command or clearly points to `project/docs/coding_guidelines.md` or equivalent project-local guidance that contains it. If the project has no automated baseline test, state that explicitly.

### Step 7: Verify Packaging and Installation End-to-End (Maintainers)

`scripts/sync_init_scaffolds.py` generates the bundled scaffold output in `cli/src/ai_team/init/scaffolds/` from the package-owned source assets in `cli/src/ai_team/init/sources/`. Run this script before every build to ensure `ai-team init` ships up-to-date scaffolds.

Run this sequence from a clean shell to confirm the package builds, installs, and initializes correctly:

```bash
cd cli && python scripts/sync_init_scaffolds.py && uv build \
  && pipx install --force dist/*.whl \
  && d=$(mktemp -d) && ai-team init "$d" --tools claude --no-interactive \
  && ai-team --version && ai-team status \
  && test -d "$d/project" && test -d "$d/.claude" && test -f "$d/.ai-team.toml"
```

### Step 8: Start Working

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
