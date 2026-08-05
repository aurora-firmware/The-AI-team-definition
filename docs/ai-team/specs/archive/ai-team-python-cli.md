---
title: "ai-team Python CLI"
version: "0.1"
status: superseded
created: 2026-05-10
author: planner
---

# ai-team Python CLI

## Purpose

Today, navigating the AI-team artifacts in a consuming project (specs, tasks, bugs, ADRs) requires reading the filesystem by hand or running ad-hoc bash scripts (e.g., `.claude/skills/status-report/scripts/status-summary.sh`). Markdown templates for new artifacts are duplicated across multiple skills as static assets, and there is no single tool that scaffolds the framework into a fresh repository.

This specification defines a Python CLI named `ai-team`, packaged with **uv**, distributable via **pipx**, that gives humans a single command-line entry point to:

- Browse and inspect AI-team artifacts (`list`, `show`, `status`).
- Create new artifacts from templates (`task new`, `bug new`, `spec new`, `adr new`).
- Move artifacts through their lifecycle (pending → in-progress → completed/blocked; open → in-progress → resolved).
- Validate artifact frontmatter, branch-naming conventions, and cross-references.
- Generate progress reports (replacing `status-summary.sh`).
- Bootstrap the framework into a fresh project (`init`) with interactive selection of AI tool integrations and optional `ai-process/` documentation.

The CLI is built on **Typer + Rich** for a humans-first terminal experience, with an opt-in `--json` flag on read commands so skills and agents can call it programmatically. Once shipped, the existing skill scripts (`status-summary.sh`, etc.) and bundled markdown templates (`new-task`, `new-bug`, `new-spec`, `new-adr` assets) are migrated into the CLI package; affected `SKILL.md` files are updated to invoke the CLI rather than embed scripts and templates of their own.

The expected outcome is one source of truth for artifact scaffolding, lifecycle, and reporting; a faster way for humans to navigate the project; and a reproducible one-command setup for new consumers of the framework.

## Exclusions

- **Textual TUI dashboard.** No interactive `view` dashboard built on Textual is part of this spec; `list`/`show`/`status` render with Rich tables and trees only. A future spec may graduate `view` to an interactive TUI.
- **Plugin / entry-point extensibility.** Third-party packages cannot register additional `ai-team` subcommands. The command tree is closed and shipped with the package.
- **Project-specific commands.** No test, build, lint, deploy, or package-manager wrappers. Per `CLAUDE.md`, the framework must not hardcode project-specific commands; those continue to be discovered by agents from the consuming project's `CLAUDE.md`/README/build config.
- **Orchestration and agent spawning.** The CLI does not run `dev-loop`, `bug-loop`, `code-review`, `tdd`, or any other orchestrator skill, and does not spawn subagents. Those remain skill orchestrators invoked by the AI inside Claude Code / Codex.
- **Agent-first JSON contract.** JSON output is a humans-first afterthought (`--json` on read commands only). Write/lifecycle commands are not required to support JSON in v1.
- **Multi-project workspace management.** Equivalent of openspec's `workspace` commands (linking multiple repos, planning across them) is out of scope for v1.
- **Shell completion installer.** No `ai-team completion install` in v1; users can wire completions manually using Typer's built-in mechanism if they wish.
- **Editing artifact bodies.** The CLI scaffolds and moves files but does not provide an in-CLI editor for artifact contents; users edit markdown in their editor of choice.

## Architecture

### Design Principles

1. **Framework, not project.** The CLI manages AI-team artifacts only; it never embeds or assumes project-specific commands or stacks. This mirrors `CLAUDE.md`'s framework-vs-project separation.
2. **Humans first, agents second.** Default output is Rich-formatted for terminals; `--json` is available on read commands for skill/agent consumption.
3. **One source of truth for templates and scripts.** Markdown templates and helper scripts live as package data inside `ai_team`; skills reference the CLI rather than carrying their own copies.
4. **Self-locating.** The CLI walks up from `cwd` to find the project root (a folder named `project/` by default), with a `--root <path>` / `--project-dir <name>` override for non-standard layouts.
5. **Side-effects are explicit.** Every write or move command echoes the file paths it touched; `--dry-run` is supported on lifecycle and `init` commands.
6. **Validation is consultative, not coercive.** `validate` reports issues with exit codes suitable for CI, but the CLI never silently rewrites artifacts to satisfy validation.

### System Diagram

```
                                          ┌──────────────────────────┐
                                          │  Consuming project repo  │
                                          │                          │
  ┌─────────────────┐    invokes          │  project/                │
  │  Human (term.)  │─────────────────────│    specs/                │
  └─────────────────┘                     │    tasks/{pending,…}     │
           │                              │    bugs/{open,…}         │
           ▼                              │    decisions/            │
  ┌─────────────────────────┐  reads/     │  .claude/                │
  │      ai-team CLI        │  writes ───►│    agents/               │
  │   (Typer + Rich app)    │             │    skills/               │
  └─────────────────────────┘             └──────────────────────────┘
           │
           │ uses
           ▼
  ┌─────────────────────────┐
  │  Package data (bundled) │
  │  • markdown templates   │
  │  • init scaffolds       │
  │  • init manifests       │
  └─────────────────────────┘
           ▲
           │ invokes (post-migration)
           │
  ┌─────────────────────────┐
  │  .claude/skills/*       │  → SKILL.md updated to call `ai-team …`
  │  (new-task, status-     │     instead of bundled scripts/templates
  │   report, etc.)         │
  └─────────────────────────┘
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| `ai_team.cli` | Typer app, root command, global flags (`--root`, `--project-dir`, `--json`, `--no-color`, `--version`). | Single entry point; subcommands registered explicitly. |
| `ai_team.commands.*` | One module per command group: `task`, `bug`, `spec`, `adr`, `report`, `validate`, `init`, `archive`. | Each module owns its subcommand definitions and Rich rendering. |
| `ai_team.core.locator` | Locate project root by walking up from `cwd`; honour `--root` / `--project-dir`. | Returns a `ProjectRoot` dataclass with all artifact-folder paths. |
| `ai_team.core.models` | Dataclasses for `Task`, `Bug`, `Spec`, `Adr` parsed from frontmatter; lifecycle state enums. | Pure data; no I/O. |
| `ai_team.core.fs` | Read/write/move artifact files, frontmatter parse/dump, atomic moves, idempotency checks. | Single chokepoint for filesystem mutation. |
| `ai_team.core.validate` | Frontmatter schema, branch-naming rules (`T-NNN`, `B-NNN`), reference integrity. | Pure functions returning structured findings. |
| `ai_team.templates` | Bundled markdown templates (`task.md`, `bug.md`, `spec.md`, `adr.md`) loaded via `importlib.resources`. | Migrated from `.claude/skills/*/assets/`. |
| `ai_team.init` | `init` scaffolding logic: copies `project/` skeleton, optionally `.claude/agents/` and `.claude/skills/` and `ai-process/`, prompts for AI tool integrations. | Bundles framework artefacts as package data. |
| `ai_team.render` | Rich console wrappers (tables, trees, panels) and JSON serialisation. | Single place to switch between human and `--json` output. |

### Command Surface (v1)

```
ai-team --version
ai-team init [path] [--tools claude,codex,…|all|none] [--include-ai-process] [--dry-run] [--force]

ai-team list (tasks|bugs|specs|adrs) [--state pending|in-progress|…] [--json]
ai-team show <ID|slug> [--json]
ai-team status [--json]                        # replaces status-summary.sh
ai-team report [--out <path>]                  # writes Gate 5 progress report

ai-team task new <title> [--spec S-NNN] [--role developer]
ai-team task start <T-NNN>                     # pending  → in-progress
ai-team task complete <T-NNN>                  # in-progress → completed
ai-team task block <T-NNN> --reason "<text>"   # → blocked
ai-team task unblock <T-NNN>                   # blocked → in-progress

ai-team bug new <title> [--severity critical|high|medium|low]
ai-team bug start <B-NNN>                      # open → in-progress
ai-team bug resolve <B-NNN>                    # in-progress → resolved

ai-team spec new <title>
ai-team adr new <title>

ai-team archive [--older-than 90d] [--dry-run]
ai-team validate [--all|--tasks|--bugs|--specs|--adrs] [--json]
```

Global flags accepted on every command:

| Flag | Purpose |
|---|---|
| `--root <path>` | Override project root (otherwise walk up from `cwd`). |
| `--project-dir <name>` | Override the artifact folder name (default `project`). |
| `--no-color` | Disable Rich styling (CI-friendly). |
| `--json` | Machine-readable output (read commands only). |
| `--version` | Print version and exit. |

## Components

### Component 1: CLI app shell (`ai_team.cli`)

**Purpose:** Typer root app, global flags, project-root resolution, version reporting, error formatting.
**Estimated size:** Small (~150 LoC).
**Interfaces:** Exposes the `ai-team` console-script entry point declared in `pyproject.toml`. Consumes `ai_team.core.locator` for project resolution and `ai_team.render` for error rendering.

### Component 2: Read commands (`list`, `show`, `status`, `report`)

**Purpose:** Inspect project state without mutating it; `report` writes a Gate 5 progress-report file.
**Estimated size:** Medium (~400 LoC including Rich renderers).
**Interfaces:** Reads through `ai_team.core.fs`; renders via `ai_team.render`; supports `--json`. `report` replaces `.claude/skills/status-report/scripts/status-summary.sh` and `assets/progress-report.md` (template moved into package).

### Component 3: Create commands (`task new`, `bug new`, `spec new`, `adr new`)

**Purpose:** Scaffold new artifacts from bundled templates with frontmatter prefilled (ID, date, status, author).
**Estimated size:** Medium (~300 LoC, mostly slugification and ID-allocation logic).
**Interfaces:** Loads templates via `importlib.resources` from `ai_team.templates`. Allocates next free `T-NNN` / `B-NNN` / `S-NNN` / `ADR-NNN` by scanning existing artifacts.

### Component 4: Lifecycle commands (`task start/complete/block/unblock`, `bug start/resolve`, `archive`)

**Purpose:** Move artifact files between state folders atomically.
**Estimated size:** Small–medium (~250 LoC).
**Interfaces:** Uses `ai_team.core.fs` for atomic moves. Updates `status:` field in frontmatter where applicable. Idempotent: re-running `task complete` on an already-completed task is a no-op with a clear message. `--dry-run` previews moves without writing.

### Component 5: Validation (`validate`)

**Purpose:** Check artifacts against frontmatter schema, branch-naming conventions (`T-NNN`, `B-NNN`), and cross-references (a task's `spec:` field points to an existing spec; a bug's `task:` field points to an existing task).
**Estimated size:** Medium (~350 LoC).
**Interfaces:** Pure-function findings layer in `ai_team.core.validate`; CLI command formats findings as Rich table or JSON. Exits non-zero on errors so CI can block on it.

### Component 6: Init (`init`)

**Purpose:** Scaffold a fresh repository with `project/` skeleton; optionally copy `.claude/agents/`, `.claude/skills/`, and `ai-process/` as bundled package data; interactive prompts for AI tool selection (claude, codex, both, custom).
**Estimated size:** Large (~500 LoC plus bundled assets).
**Interfaces:** Reads embedded asset tree (zipped or `importlib.resources` package data). Honours `--force` (overwrite), `--dry-run` (preview), and `--tools` (non-interactive selection). Writes a small `.ai-team.toml` marker to the new repo so the locator can find it without relying on folder names.

### Component 7: Skill migration (`.claude/skills/*` updates)

**Purpose:** Update affected `SKILL.md` files to call the CLI instead of bundled scripts/templates; delete migrated assets.
**Estimated size:** Medium (touches ~6 skills).
**Interfaces:** No code; markdown edits. In scope for this spec because the migration is the load-bearing reason for the CLI.

Affected skills (initial set, to be confirmed during task breakdown):

| Skill | What changes |
|---|---|
| `new-task` | `SKILL.md` invokes `ai-team task new`; delete `assets/TEMPLATE-task.md`. |
| `new-bug` | `SKILL.md` invokes `ai-team bug new`; delete `assets/TEMPLATE-bug.md`. |
| `new-spec` | `SKILL.md` invokes `ai-team spec new`; delete `assets/TEMPLATE-specification.md` and `assets/slugify.sh`. |
| `new-adr` | `SKILL.md` invokes `ai-team adr new`; delete `assets/TEMPLATE-adr.md`. |
| `status-report` | `SKILL.md` invokes `ai-team status` and `ai-team report`; delete `scripts/status-summary.sh` and `assets/progress-report.md`. |
| `git-conventions` | `SKILL.md` references `ai-team validate` for branch-name checks (no script change today, but worth aligning). |

## Workflow

End-to-end flow for a typical human session and for the CLI's own delivery.

### Human session

```
ai-team status                         # see project state
  ↓
ai-team task new "Add CLI scaffold"    # create T-042 from template
  ↓
ai-team task start T-042               # pending → in-progress
  ↓
(human edits files; AI runs dev-loop in Claude Code)
  ↓
ai-team validate --tasks               # confirm frontmatter / refs OK
  ↓
ai-team task complete T-042            # in-progress → completed
  ↓
ai-team report                         # Gate 5 progress report
```

### Skill invocation (post-migration)

```
Skill (e.g. new-task) reads SKILL.md
  ↓
SKILL.md instructs the model: "Run `ai-team task new <title> --json`"
  ↓
CLI scaffolds artifact, prints JSON describing the new file
  ↓
Skill continues with subsequent steps using the JSON output
```

### Init in a fresh repo

```
pipx install ai-team-cli
  ↓
cd new-repo && ai-team init
  ↓
Prompts: AI tools? include ai-process docs? confirm path?
  ↓
Scaffolds project/, .claude/agents/, .claude/skills/, optionally ai-process/
  ↓
Writes .ai-team.toml marker
  ↓
Prints next steps (gate 1 spec, /brainstorm, etc.)
```

## Configuration

The CLI itself requires no configuration to operate against a default repo layout. A minimal marker file is written by `init` so the locator can find the root reliably:

```toml
# .ai-team.toml (written by `ai-team init`)
[project]
# Folder containing specs/tasks/bugs/decisions; default "project".
dir = "project"

[init]
# Recorded for `ai-team update` to know what to refresh.
tools = ["claude", "codex"]
include_ai_process = true
framework_version = "0.1.0"
```

The locator's resolution order:

1. `--root <path>` flag, if provided.
2. `AI_TEAM_ROOT` environment variable, if set.
3. Walk up from `cwd` looking for `.ai-team.toml`; if found, use the configured `project.dir`.
4. Walk up from `cwd` looking for a folder named after `--project-dir` (default `project`).
5. Error with a clear message and a `init` hint.

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | Bootstrap `cli/` with uv: `pyproject.toml` (Python ≥3.14, deps: `typer`, `rich`, `pyyaml` or `ruamel.yaml`, `tomli-w`), src layout, console-script entry, smoke `ai-team --version`. | Nothing |
| 2 | Core: locator, models, fs, frontmatter parser. | Phase 1 |
| 3 | Read commands: `list`, `show`, `status` (no `report` yet) with Rich + `--json`. | Phase 2 |
| 4 | Create commands: `task new`, `bug new`, `spec new`, `adr new`; bundle templates as package data. | Phase 2 |
| 5 | Lifecycle commands: `task start/complete/block/unblock`, `bug start/resolve`, `archive`. | Phase 4 |
| 6 | `validate` command (frontmatter + branch-naming + cross-refs). | Phase 2 |
| 7 | `report` command + skill migration of `status-report` (CLI replaces `status-summary.sh` and embeds the progress-report template). | Phase 3, 6 |
| 8 | Skill migration of `new-task`, `new-bug`, `new-spec`, `new-adr` (delete bundled templates, update `SKILL.md` to invoke CLI). | Phase 4 |
| 9 | `init` command: bundle `project/`, `.claude/agents/`, `.claude/skills/`, optional `ai-process/` as package data; interactive tool selection; write `.ai-team.toml`. | Phases 1–8 stable |
| 10 | Packaging: `uv build`; smoke `pipx install dist/*.whl`; document install in `guides/setup-guide.md`. | Phase 9 |
| 11 | [TODO] CI: lint (ruff), type-check (mypy or pyright), unit tests (pytest), integration test that runs `ai-team init` into a temp dir and validates the result. | Phase 10 |

## Open Questions

- [TODO] Frontmatter library: `pyyaml` (ubiquitous, C-backed) vs `ruamel.yaml` (round-trip preserves comments/order). Decide during Phase 2; lean toward `ruamel.yaml` since artifacts have human-edited comments worth preserving.
- [TODO] ID allocation: scan all state folders and pick `max(N) + 1`, or maintain a counter in `.ai-team.toml`? Scanning is simpler and stateless; pick that unless concurrency becomes an issue.
- [TODO] Final list of skills affected by migration — confirm during Gate 2 task breakdown by grep over `.claude/skills/*/scripts/` and `.claude/skills/*/assets/`.
- [TODO] Whether `init` should write the `.ai-team.toml` marker in v1 or rely solely on folder-name walking. Writing the marker is more robust; recommended.
- [TODO] Python 3.14 install-base risk — some CI providers and Linux distros may not yet ship 3.14. Confirm uv's bootstrapping covers this gap; otherwise widen to 3.12+.

## Amendment Log

| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| 2026-05-14 | Spec archived; status set to `superseded`. `cli/docs/` (`cli/docs/commands.md`, `cli/docs/usage.md`) is now the current source of truth for CLI behaviour. | T-027 and T-028 delivered the authoritative docs in `cli/docs/`; keeping this spec active would leave two contradictory descriptions of the CLI. | T-030 |
