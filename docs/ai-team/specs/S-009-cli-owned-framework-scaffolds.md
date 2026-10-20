---
title: CLI-owned framework scaffolds and remove ai-process init export
version: '0.1'
status: approved  # draft | review | approved | superseded
created: '2026-05-14'
author: planner
id: S-009
---

# CLI-owned framework scaffolds and remove ai-process init export

## Purpose

The framework currently has multiple product copies of the agent and skill definitions:
the repository-root `.claude/` and `.codex/` folders, and the bundled init scaffold
copies inside the `ai-team` CLI package. The CLI also bundles an `ai-process/` snapshot
and exposes `ai-team init --include-ai-process`, which means the tooling can export a
duplicate of the process specification even though the process layer should remain the
authoritative documentation in this repository.

This specification makes the CLI package the only product source of truth for exported
framework definitions. Repository-root `.claude/` and `.codex/` remain present, but only
as ordinary local project configuration for working on this repository. They are not
the product source and are not symlinked into packaged assets. `ai-team init` continues
to scaffold Claude and Codex agent/skill files for consuming projects, but it no longer
offers or copies `ai-process/`.

The expected outcome is a cleaner ownership model: the CLI owns installable/exported
framework assets, the process docs remain in `ai-process/` only, and documentation no
longer describes root `.claude/` / `.codex/` folders as the product implementation layer.

## Exclusions

What this specification explicitly does NOT cover:

- **Exporting `ai-process/` by another route.** This removes `init` support for copying
  `ai-process/`; it does not add a replacement `ai-team export ai-process` command.
- **Generating agents from a structured schema.** Claude and Codex agent definitions may
  remain separate packaged assets in this scope. A future spec may define a richer
  canonical model for generating agents.
- **Changing workflow semantics.** The AI-team process, gates, role responsibilities,
  escalation chain, and task/bug lifecycle semantics stay unchanged.
- **Making root `.claude/` or `.codex/` generated.** Those folders remain normal local
  project configuration for this repository. They are not symlinked, generated, or used
  as product sources.

## Architecture

### Design Principles

1. **CLI package owns exported framework assets.** Anything copied into a consuming
   project by `ai-team init` lives under `cli/src/ai_team/init/` as package-owned data.
2. **Root tool folders are local configuration.** Repository-root `.claude/` and
   `.codex/` are for developing this repository with those tools, not for shipping the
   framework.
3. **Shared skill text, tool-specific headers.** Claude and Codex skills share the same
   procedural body text. Tool-specific frontmatter/header differences are generated from
   package-owned metadata so the body cannot drift.
4. **No process duplication.** `ai-process/` remains the specification layer in this
   repository and is not bundled into the CLI init scaffolds.
5. **Documentation follows ownership.** README, guides, CLI docs, and architecture docs
   must describe the new package-owned scaffolding model and remove stale instructions
   about syncing from root `.claude/` / `.codex/` or including `ai-process/`.

### System Diagram

```
Repository root (development workspace)
  .claude/                 local Claude project config only
  .codex/                  local Codex project config only
  ai-process/              authoritative process specification, not exported by init
  cli/
    src/ai_team/init/
      sources/
        skills/<name>/body.md
        skills/<name>/metadata.toml
        agents/claude/*.md
        agents/codex/*.toml
      scaffolds/
        project/           empty lifecycle skeleton
        claude/            generated/copied package scaffold output
        codex/             generated/copied package scaffold output

ai-team init --tools claude,codex
  copies package scaffolds only
  writes project/, .claude/, .codex/, .ai-team.toml
  never writes ai-process/
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| `cli/src/ai_team/init/sources/` | Canonical package-owned source assets for exported framework definitions. | Owns shared skill body text, skill metadata, and tool-specific agent definitions. |
| Skill scaffold generator | Produces Claude and Codex skill files from shared body text plus tool-specific frontmatter/header metadata. | May be integrated into the existing scaffold sync script or replace it with a package-source-first generator. |
| `cli/src/ai_team/init/scaffolds/` | Generated/copied package data consumed by `ai-team init`. | Contains `project/`, `claude/`, and `codex/`; does not contain `ai-process/`. |
| `ai-team init` | Copies selected tool scaffolds and the `project/` skeleton into a target repo. | Removes `--include-ai-process`, process prompt, process copy logic, and marker field. |
| Tests | Enforce that generated Claude/Codex skill bodies match the canonical shared body and that `init` no longer exposes/copies `ai-process/`. | Prevents drift and CLI contract regression. |
| Documentation | Explains the new source-of-truth boundary and updated init behavior. | Includes `ai-process/`, README, setup/customization guides, and `cli/docs/`. |

## Components

### Component 1: Package-Owned Scaffold Sources

**Purpose:** Move exported framework source assets into the CLI package so the CLI owns
what it ships.
**Estimated size:** Medium.
**Interfaces:** Provides canonical skill bodies and metadata to the generator, and
tool-specific agent files to scaffold copying. The source tree must not read from
repository-root `.claude/`, `.codex/`, or `ai-process/`.

The exact file layout can be adjusted during implementation, but it must preserve these
ownership rules:

- shared skill body text is stored once;
- Claude-specific skill frontmatter is stored as metadata, not duplicated in body text;
- Codex-specific skill header/frontmatter or wrapper fields are stored as metadata, not
  duplicated in body text;
- Claude and Codex agent definitions are package-owned assets.

### Component 2: Skill Scaffold Generation

**Purpose:** Generate Claude and Codex skill files from one shared body text per skill.
**Estimated size:** Medium.
**Interfaces:** Consumes package-owned skill body and metadata files; writes generated
files under `cli/src/ai_team/init/scaffolds/claude/skills/` and
`cli/src/ai_team/init/scaffolds/codex/skills/`.

Generated skill files must preserve identical procedural body text across Claude and
Codex outputs. Differences are limited to tool-specific metadata/frontmatter/header
fields. Tests should compare normalized body text between generated Claude and Codex
skill files.

### Component 3: Init Command Contract

**Purpose:** Keep `ai-team init` as the way to scaffold consuming repositories, while
removing process-doc export behavior.
**Estimated size:** Small to medium.
**Interfaces:** Updates `cli/src/ai_team/commands/init.py`, command docs, and tests.

Required behavior:

- `--tools claude`, `--tools codex`, `--tools claude,codex`, `--tools all`, and
  `--tools none` select package-owned tool scaffolds.
- `claude` scaffolds `.claude/agents/` and `.claude/skills/`.
- `codex` scaffolds `.codex/agents/` and `.codex/skills/` as real files/directories,
  not symlinks to `.claude/`.
- `--include-ai-process` is no longer accepted.
- Interactive init no longer asks whether to include an `ai-process` snapshot.
- `.ai-team.toml` no longer records `include_ai_process`.
- The package scaffold tree no longer contains `ai-process/`.

### Component 4: Documentation Realignment

**Purpose:** Update docs so the product/source boundary is consistent everywhere.
**Estimated size:** Medium.
**Interfaces:** Touches `ai-process/`, README, setup/customization guides, CLI docs, and
generated command docs where appropriate.

Documentation must state:

- `ai-process/` is the authoritative process specification in this repository and is
  not exported by `ai-team init`.
- CLI package scaffold sources are the product source for exported agents and skills.
- Root `.claude/` and `.codex/` are local project config for this repository, not the
  product source of the framework.
- The old scaffold sync rule from root `.claude/` / `.codex/` is removed or replaced
  with the package-source generator command.
- CLI command reference no longer lists `--include-ai-process`.

## Workflow

### Maintainer Asset Flow

```
Edit package-owned scaffold source asset
  ↓
Run scaffold generator
  ↓
Generated claude/codex scaffold outputs update under cli/src/ai_team/init/scaffolds/
  ↓
Run tests that compare shared skill bodies and init behavior
  ↓
Commit source asset, generated scaffold output, tests/docs updates together
```

### Consumer Init Flow

```
ai-team init . --tools claude,codex --no-interactive
  ↓
Copies project/ lifecycle skeleton
  ↓
Copies .claude/ from package-owned Claude scaffold, if selected
  ↓
Copies .codex/ from package-owned Codex scaffold, if selected
  ↓
Writes .ai-team.toml without include_ai_process
  ↓
Never writes ai-process/
```

## Configuration

The `.ai-team.toml` marker written by init keeps the selected tools and framework
version, but no longer records an `include_ai_process` value.

Illustrative shape:

```toml
[project]
dir = "project"

[init]
tools = ["claude", "codex"]
framework_version = "0.1.0"
```

Tool-specific skill metadata may be TOML, YAML, or another simple structured format
chosen during implementation. The format must be easy to validate in tests and must not
require reading root `.claude/` or `.codex/`.

## Alternatives Considered

### Direct Package Copies

Keep separate Claude and Codex scaffold files directly under the CLI package and copy
them as-is. This is simpler, but it permits the shared skill body text to drift between
tool formats unless every change is manually duplicated or heavily tested.

### Shared Skill Body With Generated Tool Scaffolds

Store each skill body once and generate Claude/Codex skill files with tool-specific
metadata. This is the chosen direction because it removes the meaningful duplication
while keeping implementation scope manageable.

### Fully Structured Framework Model

Model agents and skills as structured data and generate every tool artifact from that
schema. This is cleaner long-term but too broad for this change; it would require a new
schema, migration rules, and broader review of all agent definitions.

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | Add package-owned scaffold source layout and move/copy current product agent and skill definitions into it. | Nothing |
| 2 | Add or update the scaffold generator so Claude and Codex skill files are generated from shared skill bodies plus tool metadata. | Phase 1 |
| 3 | Update bundled scaffold outputs: include `project/`, `claude/`, and `codex/`; remove bundled `ai-process/`; ensure Codex skills are real files, not symlinks. | Phase 2 |
| 4 | Update `ai-team init`: remove `--include-ai-process`, process prompt, process copy logic, and marker field; scaffold Codex when selected. | Phase 3 |
| 5 | Update tests for scaffold generation, init behavior, package-data reachability, and command docs. | Phases 2-4 |
| 6 | Update README, guides, `cli/docs/`, generated `cli/docs/commands.md`, and `ai-process/` docs to reflect the new ownership model. | Phases 3-4 |
| 7 | Remove stale sync instructions and any tests that assume root `.claude/` / `.codex/` are product sources. | Phases 5-6 |

## Amendment Log

<!-- Optional. Use when an approved spec is amended after tasks are in flight.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| YYYY-MM-DD | Description of change | Reason for amendment | T-XXX, T-YYY |
-->
