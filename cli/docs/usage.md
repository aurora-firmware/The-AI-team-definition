# ai-team CLI Usage Guide

This guide covers installation, initialisation, daily workflows, the expected
`project/` folder structure, and a maintainer section. For an exhaustive list
of every command, flag, and argument, see [commands.md](commands.md).

---

## Table of Contents

1. [Installation](#installation)
2. [Initialisation](#initialisation)
3. [Daily Workflows](#daily-workflows)
4. [Project Folder Structure](#project-folder-structure)
5. [For Maintainers](#for-maintainers)

---

## Development warning

For every invocation, `ai-team` emits this warning exactly once:

```text
Warning: ai-team is under development. Please report issues at https://github.com/aurora-firmware/The-AI-team-definition/issues
```

The warning goes to stderr for help, version, successful commands, failed
commands, and commands that emit JSON. Normal human-readable and JSON output
remains on stdout, so redirect or parse stdout without including the warning.

---

## Installation

**Requirements:** Python 3.14 or later.

### From GitHub Releases

```bash
pipx install https://github.com/<org>/<repo>/releases/download/<tag>/ai_team-<version>-py3-none-any.whl
```

### From a local build

Clone this repository, then:

```bash
cd cli
python scripts/sync_init_scaffolds.py   # refreshes bundled scaffold snapshots
uv build
pipx install --force dist/*.whl
```

`sync_init_scaffolds.py` copies the current `.claude/agents/`, `.claude/skills/`,
and project skeleton into the package so that `ai-team init` ships up-to-date
scaffolds. Always run it before `uv build`.

### Verify the install

```bash
ai-team --version
```

---

## Initialisation

`ai-team init` scaffolds a fresh AI-team repository. Run it from the target
project's root directory.

```bash
ai-team init [PATH] [OPTIONS]
```

`PATH` defaults to `.` (the current directory).

### Flags

| Flag | Description |
|---|---|
| `--tools TEXT` | Comma-separated tool names to scaffold (e.g. `claude`, `codex`, `all`, `none`). |
| `--dry-run` | Print what would be written without touching the filesystem. |
| `--force` | Overwrite existing files. Without this flag the command refuses to overwrite. |
| `--no-interactive` | Skip all prompts. Requires `--tools` to be provided explicitly. |
| `--create-root-guidance` | When used with `--no-interactive`, create root `CLAUDE.md` and `AGENTS.md` from starter templates. Defaults to false (skipped). |

### What gets scaffolded

`ai-team init` never copies `ai-process/`. All scaffolded files come from
package-owned snapshots bundled inside the `ai_team.init.scaffolds` package.

Running `ai-team init . --tools claude` writes:

```
project/
  specs/
  tasks/
    pending/
    in-progress/
    completed/
    blocked/
  bugs/
    open/
    in-progress/
    resolved/
  decisions/
  docs/
.claude/
  agents/
  skills/
.ai-team.toml
```

Running `ai-team init . --tools codex` additionally writes:

```
.codex/
  agents/   ← Codex-format .toml agent definitions
  skills/   ← Codex-format SKILL.md skill definitions
```

Use `--tools all` (or `--tools claude,codex`) to scaffold both tool sets at once.

Each folder is created with a `.gitkeep` placeholder so git tracks the
empty directories.

`.ai-team.toml` is the marker file that tells the CLI where the project root
is. It records the tools selected and the framework version used.

### Root guidance files

After scaffolding the project skeleton and tool files, `ai-team init` offers to
create root-level `CLAUDE.md` and `AGENTS.md` from starter templates. These files
tell AI tools how to build, test, and run your project.

- **Interactive mode** (default): the CLI prompts once per file. Answer `y` to
  create a starter template, or `n` to skip.
- **`--no-interactive --create-root-guidance`**: creates both files without
  prompting. Useful in CI or scripted setup flows.
- **`--no-interactive` without `--create-root-guidance`**: skips both files and
  prints a reminder to add them manually.

Existing root guidance files are never overwritten unless `--force` is also passed.

### Example: preview then initialise

```bash
# Preview without writing
ai-team init . --tools claude --no-interactive --dry-run

# Initialise for real (interactive: prompts for root CLAUDE.md and AGENTS.md)
ai-team init . --tools claude

# Non-interactive with root guidance files
ai-team init . --tools claude --no-interactive --create-root-guidance

# Initialise with both Claude and Codex tool scaffolds
ai-team init . --tools all --no-interactive
```

---

## Daily Workflows

### Check the repository layout

Run the read-only layout diagnostic from anywhere inside an initialized
repository:

```bash
ai-team check-layout
```

The command runs four ordered validation levels:

1. **Level 1 — expected directories.** Checks the configured project directory,
   every lifecycle directory in the current project scaffold, and the agent and
   skill directories for each configured tool. Extra directories are allowed.
2. **Level 2 — artifact names and frontmatter.** Checks managed specs, tasks,
   bugs, change requests, and decisions for the expected filename, required
   frontmatter, and agreement between lifecycle location and status.
3. **Level 3 — root guidance.** Checks `CLAUDE.md` for configured Claude tools
   and `AGENTS.md` for configured Codex tools. Each required file must contain
   non-placeholder `Build and Install`, `Test`, `Run`, `Lint and Format`, and
   `Key Conventions` guidance.
4. **Level 4 — version alignment.** Checks that the framework version recorded
   in `.ai-team.toml` exactly matches the running CLI distribution version.

Each finding reports `Level`, `Path`, `Problem`, and `Suggested fix`. Findings
are ordered by level and then path. A clean repository prints an explicit
success message and returns exit code 0; one or more findings are all reported
before the command returns exit code 1.

`check-layout` only observes the repository: it does not repair, create, move,
rename, rewrite, or delete files or directories. Suggested fixes are guidance
for the user, and no project guidance command is executed.

### Create and ship a task

```bash
# 1. Create a new pending task
ai-team task new "Add user onboarding flow" --priority high --assigned-role developer

# 2. Start work (moves to tasks/in-progress/)
ai-team task start T-001

# 3. Mark complete (moves to tasks/completed/)
ai-team task complete T-001
```

If a task gets stuck:

```bash
# Block with a reason
ai-team task block T-001 --reason "Waiting for API contract from backend team"

# Unblock when the blocker is resolved
ai-team task unblock T-001
```

List all tasks (all states) or filter by state:

```bash
ai-team list tasks
ai-team list tasks --state in-progress
```

Show a specific task (rendered markdown):

```bash
ai-team show T-001
```

### File and resolve a bug

```bash
# 1. File a new bug
ai-team bug new "Login crashes on empty token" --severity high

# 2. Start investigation (moves to bugs/in-progress/)
ai-team bug start B-001

# 3. Resolve when fixed (moves to bugs/resolved/)
ai-team bug resolve B-001
```

List bugs:

```bash
ai-team list bugs
ai-team list bugs --state open
```

### Create a spec or ADR

```bash
# New specification (lands in project/specs/ as S-NNN-<slug>.md)
ai-team spec new "Billing reconciliation" --author "planner" --status draft

# New Architecture Decision Record (lands in project/decisions/)
ai-team adr new "Use PostgreSQL for ledger storage" --status proposed
```

### File a change request

Change requests capture proposed changes before they are planned as tasks.
They land in `project/change-requests/` with a `CR-NNN-<slug>.md` filename.

```bash
# Create a new pending change request (lands in project/change-requests/)
ai-team change-request new "Revamp onboarding flow"

# Emit machine-readable output for agent use
ai-team change-request new "Revamp onboarding flow" --json
```

List change requests, specs, and ADRs:

```bash
ai-team list change-requests
ai-team list specs
ai-team list adrs
```

### Generate a Gate 5 status report

Gate 5 is the human sign-off before merging `dev-agent` to `main`. These two
commands give the context needed:

```bash
# Inline summary in the terminal
ai-team status

# Write a full progress report to project/docs/reports/
ai-team report

# Override the output path
ai-team report --out /tmp/custom-report.md
```

`ai-team status` shows counts of active specs, tasks by state, bugs by state,
in-progress tasks, blocked tasks, critical/high bugs, and the latest
integration result from git history.

`ai-team report` renders the same data into a markdown file using the bundled
report template.

### Validate artifacts

```bash
# Validate all artifact types
ai-team validate --all

# Validate tasks and bugs only
ai-team validate --tasks --bugs

# Validate change requests only
ai-team validate --change-requests

# Emit JSON for scripting
ai-team validate --json
```

Exit code is 1 if any error-level finding is reported.

### Archive old artifacts

Completed tasks and resolved bugs older than a threshold are moved to
`project/archive/YYYY-MM/`:

```bash
# Preview what would be archived (default: older than 90 days)
ai-team archive --dry-run

# Archive with a custom threshold
ai-team archive --older-than 30d
```

Supported units: `d` (days), `w` (weeks), `m` (months, = 30 days),
`y` (years, = 365 days).

---

## Project Folder Structure

Every command that reads or writes artifacts resolves the project root through
the **locator**, which tries four strategies in order:

1. **Explicit `root=` argument** — only when callers pass `root` programmatically.
2. **`AI_TEAM_ROOT` environment variable** — set this to override auto-detection
   in CI or scripts:
   ```bash
   export AI_TEAM_ROOT=/path/to/repo
   ```
3. **Walk up from `cwd` looking for `.ai-team.toml`** — uses the `[project] dir`
   value from the file as the artifact folder name.
4. **Walk up from `cwd` looking for a folder named `project`** — the
   convention-based fallback.

If no project root is found the CLI exits with a `ProjectRootNotFound` error
and suggests running `ai-team init`.

### The `.ai-team.toml` marker

`ai-team init` writes `.ai-team.toml` in the repository root with content
similar to:

```toml
[project]
dir = "project"

[init]
tools = ["claude"]
framework_version = "0.1.0"
```

The `[project] dir` key is what the locator reads in strategy 3. You can
change this key if your project uses a different folder name than `project`.

### Expected layout

```
<repo-root>/
  .ai-team.toml               ← locator marker; written by ai-team init
  project/                    ← artifact root (name comes from [project] dir)
    specs/                    ← feature specifications
      archive/                ← superseded spec versions
    tasks/
      pending/                ← tasks not yet started
      in-progress/            ← tasks actively being worked on
      completed/              ← finished tasks
      blocked/                ← tasks with a recorded blocking reason
    bugs/
      open/                   ← newly filed bugs
      in-progress/            ← bugs under active investigation
      resolved/               ← fixed bugs
    decisions/                ← Architecture Decision Records (ADR-NNN-*.md)
    docs/                     ← project-specific docs: coding guidelines,
                              │  commands, stack-specific notes
    archive/
      YYYY-MM/                ← old completed/resolved artifacts (ai-team archive)
```

Artifact filenames follow the patterns `T-NNN-<slug>.md` (tasks),
`B-NNN-<slug>.md` (bugs), `S-NNN-<slug>.md` (specs), and `ADR-NNN-<slug>.md`
(ADRs). The CLI allocates the next sequential ID by scanning all state folders
for a given artifact type. Legacy spec files without the `S-NNN-` prefix are
also accepted by validation.

---

## For Maintainers

### Module map

The `ai_team` package lives in `cli/src/ai_team/` and is structured as:

| Module / Package | Purpose |
|---|---|
| `ai_team.cli` | Root Typer app and console-script entry point (`ai-team`). |
| `ai_team.commands/` | One module per command group; auto-discovered at startup. |
| `ai_team.core/` | Pure-Python helpers with no Typer dependency. |
| `ai_team.core.locator` | Project root resolution (four-strategy locator). |
| `ai_team.core.ids` | Sequential ID allocation (`T-NNN`, `B-NNN`, etc.). |
| `ai_team.core.fs` | Artifact file read/write helpers. |
| `ai_team.core.models` | Dataclasses for task, bug, spec, and ADR frontmatter. |
| `ai_team.core.templates` | Loads bundled Markdown templates from the package. |
| `ai_team.core.validate` | Artifact metadata validation logic. |
| `ai_team.templates/` | Bundled Markdown artifact templates (task, bug, spec, adr, report). |
| `ai_team.init/` | Scaffold data for `ai-team init`. |
| `ai_team.init.scaffolds/` | Package-owned snapshots: project skeleton, `.claude/` agents and skills, and `.codex/` agents and skills. |
| `ai_team.render` | Rich console and JSON output helpers. |

### How to add a new command

1. Create a new module in `cli/src/ai_team/commands/`, e.g. `my_cmd.py`.
2. Expose two module-level attributes:
   - `NAME: str` — the subcommand name as it appears on the CLI.
   - `app: typer.Typer` — the Typer application for the command group.
3. No changes to `cli.py` or `commands/__init__.py` are needed; auto-discovery
   picks up the new module via `pkgutil.iter_modules` at startup.

A broken command module (import error or missing attributes) is skipped silently
so it cannot crash the whole CLI.

### How to run the tests

```bash
cd cli
uv run pytest
```

Run a specific test file:

```bash
uv run pytest tests/test_task_new.py -v
```

### How to maintain scaffold sources

The scaffold files shipped inside the package are **package-owned copies** —
they are not read from the repository's `.claude/` or `.codex/` trees at
runtime. This means any change to the canonical agent or skill definitions
must be reflected in the bundled snapshots before the next release.

The generator script `scripts/sync_init_scaffolds.py` keeps the snapshots
in sync. It reads from:

- `cli/src/ai_team/init/sources/agents/` — source agent definitions for
  each tool (`.claude/agents/`, `.codex/agents/`)
- `cli/src/ai_team/init/sources/skills/` — source skill definitions for
  each tool (`.claude/skills/`, `.codex/skills/`)

and writes the processed output into:

- `cli/src/ai_team/init/scaffolds/claude/` — `.claude/` snapshot (agents and skills)
- `cli/src/ai_team/init/scaffolds/codex/` — `.codex/` snapshot (agents and skills)
- `cli/src/ai_team/init/scaffolds/project/` — project skeleton

Run `sync_init_scaffolds.py` whenever the canonical agent or skill files
change. The script is also run automatically at the start of the local-build
installation step (see `From a local build` above).

`ai-team init` never copies `ai-process/`. The specification layer is
intentionally excluded from the scaffold — only the implementation layer
(agents, skills) and the project skeleton are bundled.

### How to build and release

Before building, refresh the bundled scaffold snapshots so `ai-team init` ships
the latest `.claude/agents/`, `.claude/skills/`, `.codex/agents/`, and
`.codex/skills/`:

```bash
cd cli
python scripts/sync_init_scaffolds.py
uv build
```

The wheel and source distribution land in `cli/dist/`. To publish a release on
GitHub:

```bash
gh release create <tag> cli/dist/*.whl cli/dist/*.tar.gz cli/docs/commands.md
```

To install the local wheel for manual testing:

```bash
pipx install --force cli/dist/*.whl
```

### How to regenerate `commands.md`

`cli/docs/commands.md` is a generated file — do not edit it by hand. Regenerate
it with:

```bash
bash cli/scripts/gen_docs.sh
```

Run this from the repository root. The script calls `typer ai_team.cli utils docs`
via `uv run` and prepends the generated-file header.
