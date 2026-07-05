---
title: "ai-team CLI Documentation"
version: "0.1"
status: approved
created: 2026-05-14
author: planner
---

# ai-team CLI Documentation

## Purpose

The `ai-team` CLI was built under the development spec `project/specs/ai-team-python-cli.md` (26 completed tasks, T-001–T-026). That spec described the CLI to be *built*; it does not serve as documentation of the CLI as it now *is*. Today the `cli/` package has no documentation of its own: no `README.md`, no `docs/` folder. A human installing the CLI must reconstruct its behaviour from the README's "Using This Framework" section, `guides/setup-guide.md`, and `ai-team --help`. A maintainer extending the CLI has nothing describing its module layout or release process. And `ai-process/architecture/component-map.md` — the authoritative description of how skills compose — does not mention the CLI at all, even though the action skills now invoke it.

This specification defines documentation for the `ai-team` CLI, placed under a new `cli/docs/` folder, covering both end users (humans running `ai-team` in a consuming project) and maintainers (people developing the CLI inside this repo). It also updates `ai-process/architecture/component-map.md` so the architecture layer records where the CLI is used together with the skills, and archives the original development spec now that the documentation supersedes it as the source of truth for CLI behaviour.

The expected outcome: a reader can install, initialise, and operate the CLI — and a maintainer can extend it — from `cli/docs/` alone; the architecture layer accurately reflects the CLI's role; and there is a single, non-contradictory source of truth for what the CLI does.

## Exclusions

What this specification explicitly does NOT cover:

- **Custom documentation-generation script.** The command reference is produced by Typer's built-in `utils docs` command, not by a bespoke generator script in `cli/scripts/`. A custom generator was considered and rejected to avoid maintaining generation code.
- **A separate maintainer document.** End-user and maintainer content share `cli/docs/usage.md`; this spec does not create a distinct `architecture.md` or `contributing.md` under `cli/docs/`.
- **A hosted documentation site.** No MkDocs, Sphinx, Read the Docs, or published docs website. Documentation is plain Markdown read in-repo.
- **`guides/` and `cli/README.md` as documentation homes.** The CLI documentation lives in `cli/docs/`. This spec does not add a `cli/README.md` or a `guides/cli-guide.md`; existing CLI mentions in `README.md` and `guides/setup-guide.md` stay as brief pointers and are updated only to link into `cli/docs/`.
- **Changes to CLI behaviour.** This is a documentation spec. It does not add, remove, or alter any CLI command, flag, or output. The one code-adjacent change is adding the `typer-cli` tooling dependency required to run `utils docs`.
- **Re-documenting the framework process.** `cli/docs/` documents the CLI tool.
  The AI-team workflow, gates, and roles remain owned by `ai-process/` and the
  package-owned scaffold source definitions that generate exported agent and
  skill files.

## Architecture

### Design Principles

1. **Docs become the source of truth.** Once `cli/docs/` exists, it — not the development spec — describes the CLI as it is. The development spec is archived to prevent two contradictory descriptions.
2. **Generation over transcription for the reference.** The exhaustive command/flag reference is generated from the Typer app itself, so it cannot drift from the code. Hand-written prose is reserved for things a generator cannot produce: workflows, the project folder structure, and maintainer guidance.
3. **Two files, two jobs.** `usage.md` is hand-written and explains *how to use and maintain* the CLI. `commands.md` is generated and is the *exhaustive reference*. The split keeps the generated file replaceable without touching hand-written content.
4. **Committed, not built on demand.** `commands.md` is checked into the repository so it is readable without a build step, mirroring how `cli/` already commits its bundled init scaffolds.
5. **The architecture layer must mention the CLI.** Per `CLAUDE.md`, `ai-process/` is the specification layer; `component-map.md` must therefore record the CLI as a component the skills compose with.

### System Diagram

```
  ┌──────────────────────┐         ┌──────────────────────────────┐
  │  Typer app           │  intro- │  cli/scripts/gen_docs.sh     │
  │  (ai_team.cli +      │  spect  │  wraps `typer ... utils docs`│
  │   commands/*)        │────────▶│  → writes cli/docs/commands.md│
  └──────────────────────┘         └──────────────────────────────┘
                                              │ commits
                                              ▼
  ┌───────────────────────────────────────────────────────────────┐
  │  cli/docs/                                                    │
  │    usage.md      ← hand-written: install, init, workflows,     │
  │                    project folder structure, maintainer notes │
  │    commands.md   ← generated: every command, subcommand, flag  │
  └───────────────────────────────────────────────────────────────┘
        ▲                                   ▲
        │ linked from                       │ referenced by
        │                                   │
  ┌─────────────┐                  ┌──────────────────────────────┐
  │ README.md   │                  │ ai-process/architecture/     │
  │ setup-guide │                  │ component-map.md             │
  └─────────────┘                  │  (new CLI ↔ skills section)  │
                                   └──────────────────────────────┘

  project/specs/ai-team-python-cli.md  ──move──▶  project/specs/archive/
        (development spec, now superseded by cli/docs/)
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| `cli/docs/usage.md` | Hand-written guide: installation, `init`, daily command workflows, the expected `project/` folder structure, and a maintainer section (module map, how to add a command, test/build/release). | Single file for both audiences, per the chosen approach. Owns everything a generator cannot produce. |
| `cli/docs/commands.md` | Generated exhaustive reference: every command group, subcommand, argument, and flag, including global flags. | Produced by Typer's built-in `utils docs`. Committed to the repo. Regenerated, never hand-edited. |
| `cli/scripts/gen_docs.sh` | Thin wrapper invoking `typer ai_team.cli utils docs` (or equivalent) and writing the output to `cli/docs/commands.md`. | Sibling to the existing `cli/scripts/sync_init_scaffolds.py`. Keeps the regeneration command in one place. |
| `cli/pyproject.toml` | Declares `typer-cli` as a tooling/dev dependency so `utils docs` is available. | Only code-adjacent change in this spec. |
| `ai-process/architecture/component-map.md` | Gains a section mapping which skills invoke which `ai-team` commands (e.g. `new-task` → `ai-team task new`, `status-report` → `ai-team status` + `ai-team report`). | Architecture layer now records the CLI's role. |
| `project/specs/archive/ai-team-python-cli.md` | The original development spec, moved here and marked `superseded`. | Preserved as design rationale/history; no longer the source of truth. |
| `README.md`, `guides/setup-guide.md` | Existing CLI mentions stay brief and gain links into `cli/docs/`. | Not documentation homes; just pointers. |

## Components

### Component 1: `cli/docs/usage.md` (hand-written guide)

**Purpose:** The narrative documentation a human reads to install, operate, and maintain the CLI.
**Estimated size:** Medium.
**Interfaces:** Consumes nothing programmatically. Must cover, at minimum:
- **Installation** — `pipx install` (published and local-build paths), the `python scripts/sync_init_scaffolds.py` + `uv build` local flow, Python version requirement.
- **Initialisation** — `ai-team init`, the `--tools` / `--include-ai-process` / `--dry-run` / `--force` flags, what gets scaffolded, the `.ai-team.toml` marker.
- **Daily workflows** — task-oriented sequences (create-and-ship a task, file-and-resolve a bug, generate a Gate 5 report), not an exhaustive flag list.
- **Expected project folder structure** — the `project/` layout the CLI reads and writes: `specs/` (+ `archive/`), `tasks/{pending,in-progress,completed,blocked}/`, `bugs/{open,in-progress,resolved}/`, `decisions/`, `docs/`, and the `.ai-team.toml` marker plus locator resolution order.
- **Maintainer section** — module map (`ai_team.cli`, `core/`, `commands/`, `templates/`, `init/`, `render`), how to add a new command, how to run tests, how to build and release, and how to regenerate `commands.md`.
- A link to `commands.md` for the exhaustive reference.

### Component 2: `cli/docs/commands.md` (generated reference)

**Purpose:** The exhaustive, drift-proof reference for every command, subcommand, argument, and flag.
**Estimated size:** Small authored effort (generated content); the file itself may be large.
**Interfaces:** Produced from the Typer app via `typer-cli`'s `utils docs`. Committed to the repo. Carries a header note stating it is generated and must not be hand-edited, and naming the regeneration command.

### Component 3: `cli/scripts/gen_docs.sh` + `typer-cli` dependency

**Purpose:** Make regeneration a single, documented command and ensure the tooling to do so is declared.
**Estimated size:** Small.
**Interfaces:** `gen_docs.sh` wraps the `typer ... utils docs` invocation and writes `cli/docs/commands.md`. `cli/pyproject.toml` gains `typer-cli` as a dev/tooling dependency. A Contributing rule (in `README.md` and/or `CLAUDE.md`) instructs maintainers to run it whenever a command or flag changes — mirroring the existing `sync_init_scaffolds.py` rule.

### Component 4: `ai-process/architecture/component-map.md` update

**Purpose:** Record in the architecture layer where the CLI is used together with the skills.
**Estimated size:** Small.
**Interfaces:** Adds a section/table mapping action skills to the `ai-team` commands they invoke (`new-spec` → `ai-team spec new`, `new-task` → `ai-team task new`, `new-bug` → `ai-team bug new`, `new-adr` → `ai-team adr new`, `status-report` → `ai-team status` + `ai-team report`). No skill files change in this spec — only the architecture document.

### Component 5: Archive the development spec

**Purpose:** Eliminate the contradiction between the build-time spec and the new docs by retiring the spec as the source of truth.
**Estimated size:** Small.
**Interfaces:** Move `project/specs/ai-team-python-cli.md` to `project/specs/archive/`, set its frontmatter `status: superseded`, and add an Amendment Log line pointing to `cli/docs/` as the current source of truth.

## Workflow

### Authoring flow

```
Add typer-cli to cli/pyproject.toml
  ↓
Write cli/scripts/gen_docs.sh; run it → cli/docs/commands.md (committed)
  ↓
Write cli/docs/usage.md (install, init, workflows, folder structure, maintainer section)
  ↓
Update ai-process/architecture/component-map.md with the CLI ↔ skills mapping
  ↓
Move project/specs/ai-team-python-cli.md → project/specs/archive/ (status: superseded)
  ↓
Update README.md / guides/setup-guide.md CLI mentions to link into cli/docs/;
add the "regenerate commands.md" Contributing rule
```

### Maintenance flow (after this spec ships)

```
Maintainer changes a CLI command or flag
  ↓
Runs cli/scripts/gen_docs.sh
  ↓
Commits the updated cli/docs/commands.md alongside the code change
  ↓
Updates cli/docs/usage.md by hand if a workflow or the folder structure changed
```

## Configuration

```toml
# cli/pyproject.toml — new tooling dependency (illustrative; exact group/section
# to match the project's existing dependency layout)
[dependency-groups]
dev = [
  "typer-cli",   # provides `typer ... utils docs` for generating cli/docs/commands.md
  # ...existing dev dependencies
]
```

```
# cli/docs/commands.md — header note (exact wording decided during implementation)
<!-- GENERATED FILE — do not edit by hand.
     Regenerate with: bash cli/scripts/gen_docs.sh -->
```

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | Add `typer-cli` dev dependency to `cli/pyproject.toml`; add `cli/scripts/gen_docs.sh` wrapping `typer ... utils docs`; generate and commit `cli/docs/commands.md`. | Nothing |
| 2 | Write `cli/docs/usage.md`: installation, `init`, daily workflows, expected `project/` folder structure, maintainer section; link to `commands.md`. | Phase 1 (so it can link to a real `commands.md`) |
| 3 | Update `ai-process/architecture/component-map.md` with the CLI ↔ skills mapping section. | Nothing (parallel with 1–2) |
| 4 | Move `project/specs/ai-team-python-cli.md` to `project/specs/archive/`, set `status: superseded`, add Amendment Log pointer to `cli/docs/`. | Phases 1–2 (docs must exist before the spec is retired) |
| 5 | Update `README.md` and `guides/setup-guide.md` CLI mentions to link into `cli/docs/`; add the "regenerate `commands.md`" Contributing rule to `README.md` / `CLAUDE.md`. | Phases 1–2 |

## Open Questions

- [TODO] Exact `typer ... utils docs` invocation and whether the installed console-script name or the module path is the right target — confirm during Phase 1.
- [TODO] Which dependency group in `cli/pyproject.toml` `typer-cli` belongs to (dev group vs optional extra) — match the project's existing convention during Phase 1.
- [TODO] Whether `commands.md` generation should be wired into CI as a drift check (regenerate and `git diff --exit-code`) — recommended, but treat as a follow-up unless trivial to add in Phase 5.

## Amendment Log

| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| 2026-07-05 | Replaced stale repo-local `.claude/` ownership wording with package-owned scaffold source ownership. | S-004 architecture consistency review found the archived documentation spec contradicted the approved scaffold ownership model. | none |
