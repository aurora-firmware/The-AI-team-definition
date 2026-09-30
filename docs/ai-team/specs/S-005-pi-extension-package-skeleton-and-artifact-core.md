---
title: 'Pi extension: package skeleton and artifact core'
version: '0.1'
status: draft  # draft | review | approved | superseded
created: '2026-09-30'
author: planner
id: S-005
---

# Pi extension: package skeleton and artifact core

<!--
This spec describes requirements and measurable criteria in prose.
It is not the implementation. Do not paste full configuration files,
build manifests, or implementation code into the sections below.
Concrete code belongs in the tasks the spec-breakdown skill produces
and in the Developer's output. See the Spec Authoring Guide for the
content contract this template implements.
-->

## Purpose

The AI-team framework can only be used from Claude Code and Codex today, and every
deterministic action (creating specs, tasks, bugs, ADRs and change requests, moving them
through lifecycle states, listing, validating, reporting) depends on the Python `ai-team`
binary being installed and on `PATH`. We want the pi coding agent to run the whole
AI-team process natively as a pi package, and the first prerequisite is a package that
pi can load and an in-process replacement for the binary. When this spec is done,
`pi install <path-to-pi-package>` gives a pi session an `ai_team` tool that performs
every CLI action with no Python installed, pi-rendered AI-team skills that call that
tool instead of the shell, and artifacts that are byte-identical to what the Python CLI
writes for the same inputs. Success is measured by a shared golden-fixture suite that
passes against both implementations.

This is sub-project 1+2 of a five-part effort (1 package skeleton, 2 artifact core,
3 agent runner, 4 process layer, 5 dev/bug loops). Sub-projects 3–5 get their own specs.

## Exclusions

What this specification explicitly does NOT cover:

- **Spawning role agents (agent runner).** Running developer, reviewer, integrator,
  architect and planner as isolated pi subprocesses is sub-project 3 and needs its own
  spec, including the dev container for end-to-end testing. It also owns rendering the
  agent definitions for pi. This spec does not sync or ship agent definitions.
- **Implicit process behaviour and gates.** System-prompt injection, `/` commands for
  the loops, and `tool_call` guards enforcing role rules are sub-project 4.
- **Dev-loop and bug-loop orchestration in pi.** This is sub-project 5.
- **Retiring or rewriting the Python CLI.** The human chose to keep the Python CLI as the
  implementation for Claude Code and Codex. The TypeScript core is a second
  implementation held to parity by fixtures, not a replacement.
- **A separate copy of skills, agents or templates for pi.** Rejected because the copies
  would drift. Sources stay single-sourced in `cli/src/ai_team/init/sources` and
  `cli/src/ai_team/templates`.
- **One pi tool per CLI command, or tools grouped by artifact type.** Rejected in favour
  of a single CLI-shaped tool, to keep the context cost to one schema and make the skill
  translation mechanical.
- **Leaving skill bodies unchanged and asking the model to translate `ai-team …` calls
  at runtime (preamble approach), or accepting raw argv strings.** Rejected because
  neither can be verified at build time and both undercut the goal of deterministic
  actions.
- **Semantic-only parity, or TypeScript tests that shell out to the Python CLI.**
  Rejected in favour of shared golden fixtures with byte-identical output.
- **Scaffolding `.claude/` or `.codex/` from pi.** Pi's `init` covers only the artifact
  layout and root guidance, because skills and agents come from the package.
- **Publishing to the npm registry.** Install from a local path is enough for this spec.
  npm publishing is a follow-up release-pipeline decision.

## Architecture

### Design Principles

- **Single source of truth for process content.** Every skill body, skill header, agent
  definition and artifact template that the pi package ships must be generated from the
  existing sources under `cli/src/ai_team/`. Nothing under the pi package's generated
  resources may be hand-edited.
- **Byte-identical artifacts.** For every fixture case, the TypeScript core and the
  Python CLI must produce the same file tree, byte for byte, and the same JSON result
  payload. Only absolute root paths are normalised when comparing.
- **Existing exports stay identical.** The Claude Code and Codex scaffolds generated after
  this work must be byte-identical to those generated before it, except where a fixture
  or ADR explicitly says otherwise.
- **Deterministic actions never go through the model.** A pi-rendered skill must never
  instruct the model to run the `ai-team` binary. Every deterministic action goes through
  the `ai_team` tool, and every tool-call snippet in a rendered skill must validate
  against the tool schema at build time.
- **Mixed teams are safe.** A Python CLI process and a pi session working on the same
  project at the same time must never allocate the same artifact ID.
- **The core is free of pi.** The artifact core must be usable and testable without the
  pi runtime. Only a thin adapter depends on the pi extension API.
- **Project root from the session, not the process.** The tool resolves the project from
  the pi session's working directory with the same resolution order as the Python
  locator, so that later child agents running in other directories (worktrees) behave
  correctly.
- **Pi's config is untouched during development.** Manual and automated verification
  must be possible without modifying the developer's real pi agent directory.

### System Diagram

```
 cli/src/ai_team/init/sources ──┐        cli/src/ai_team/templates
  (skill body.md + metadata,    │                 │
   agents, root guidance)       ▼                 ▼
                    ┌──────────────────────────────────────┐
                    │ sync_init_scaffolds.py               │
                    │  targets: claude | codex | pi        │
                    │  renders {{ai-team …}} placeholders  │
                    └───────┬───────────────┬──────────────┘
                            │               │
            cli/…/scaffolds/{claude,codex}  pi/resources/ (generated)
                                            skills/ templates/ tool-map
                                                 │
   pi session ── ai_team tool call ──► pi adapter (tool schema, result shaping)
                                                 │
                                                 ▼
                                    TS artifact core (pure) ──► project artifact tree
                                                 ▲                     ▲
                    fixtures/parity/ ── vitest ──┘                     │
                    fixtures/parity/ ── pytest ──► Python CLI core ────┘
                                  (shared .ai-team.lock between both)
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| Scaffold sync (extended) | Renders sources for the claude, codex and pi targets, including placeholder rendering | Existing script, gains a `pi` target. Consumes the command map. |
| Command map | Single table of CLI commands, arguments, flags, defaults and their tool-field names | Generated or maintained in one place and consumed by the sync and the TS schema. |
| Pi package manifest | Declares the extension entry and the generated skills to pi | Pi host packages are peer dependencies. |
| Pi adapter | Registers the `ai_team` tool, validates input, resolves the project root from the session, and shapes results and errors | The only component importing the pi API. |
| TS artifact core | Implements every CLI action: models, IDs, locking, filesystem, locator, layout, validation, templates, command handlers | Pure TypeScript. Injectable clock. |
| Parity fixtures | Declares the expected tree and JSON for each command case | Repo-level. Owned by neither implementation. |
| Fixture runners | Execute every fixture case against one implementation | One pytest runner and one vitest runner. Both auto-discover cases. |
| Python CLI (amended) | Gains an injectable clock and a lock that interoperates with the TS core | Behaviour otherwise unchanged. |

## Components

### Component 1: Pi package skeleton

**Purpose:** A `pi/` npm package beside `cli/` that pi loads from a local path, with generated resources and a TypeScript toolchain for type checking and tests.
**Estimated size:** Small.
**Interfaces:** Exposes a pi package manifest (extension entry, skills directory). Consumes generated `pi/resources/`.

### Component 2: Scaffold sync pi target and placeholder rendering

**Purpose:** Extends the existing sync so that shared skill bodies use `{{ai-team …}}` placeholders, rendered as CLI calls for claude and codex and as `ai_team` tool calls for pi. Also adds a `[pi]` header section per skill.
**Estimated size:** Medium.
**Interfaces:** Consumes skill sources, templates and the command map. Produces the claude, codex and pi resource trees. Fails the sync on unknown commands or flags.

### Component 3: `ai_team` tool (pi adapter)

**Purpose:** A single model-callable tool whose input is a union discriminated on `command`, mirroring every CLI leaf command, and whose output is a short text summary plus the CLI's JSON payload.
**Estimated size:** Small–medium.
**Interfaces:** Exposed to the model through pi's tool registration. Consumes the TS artifact core and the session working directory.

### Component 4: TypeScript artifact core

**Purpose:** A one-to-one port of the Python core and command modules, producing identical artifacts and JSON payloads.
**Estimated size:** Large.
**Interfaces:** Exposes one handler per command taking a resolved project root and typed input. Consumes templates from generated resources and a clock.

### Component 5: Shared parity fixtures and runners

**Purpose:** A repo-level golden-fixture suite that both implementations must pass, seeded once from the current Python CLI and then maintained as the contract.
**Estimated size:** Medium.
**Interfaces:** Fixture cases (command, clock, before tree, after tree, result JSON). One runner per implementation.

### Component 6: Python CLI parity amendments

**Purpose:** Adds a single injectable source of "today" and makes ID-allocation locking interoperate with the TS core's lock.
**Estimated size:** Small.
**Interfaces:** Clock override (see Configuration Requirements). The lock file at the existing `.ai-team.lock` path.

## Tool contract

**Contract.** The `ai_team` tool accepts exactly one command per call. Command names are
the CLI's leaf command paths, space-separated. Positional arguments become named fields,
and flags become camelCase fields with the CLI's defaults and allowed values.

| `command` | Required fields | Optional fields |
|---|---|---|
| `spec new` | `title` | `author`, `status` |
| `task new` | `title` | `priority`, `assignedRole`, `spec` |
| `task start` / `task complete` / `task unblock` | `id` | — |
| `task block` | `id`, `reason` | — |
| `bug new` | `title` | `severity`, `task` |
| `bug start` / `bug resolve` | `id` | — |
| `adr new` | `title` | `status`, `supersedes` |
| `change-request new` | `title` | — |
| `list tasks` / `list bugs` / `list specs` / `list adrs` | — | `state` |
| `list change-requests` | — | — |
| `show` | `identifier` | — |
| `status` | — | — |
| `report` | — | `out` |
| `validate` | — | `scope` (`all`, `tasks`, `bugs`, `specs`, `adrs`, `change-requests`) |
| `archive` | — | `olderThan`, `dryRun` |
| `check-layout` | — | — |
| `init` | — | `path`, `force`, `dryRun`, `createRootGuidance` |

- The tool never takes a `json` field. It always returns the payload the CLI emits with
  `--json` as structured details, plus a one-to-three-line human-readable summary for the
  model. For commands that have no `--json` mode in the CLI, the details are the structured
  equivalent of the CLI's output, and fixtures pin them.
- `init` in pi omits the CLI's `--tools` and `--no-interactive` options.
- Domain errors (unknown identifier, invalid state transition, validation failure, lock
  timeout, project root not found) come back as tool errors carrying the same message
  text as the CLI's error output. Unexpected exceptions come back as tool errors with a
  one-line message, never a stack trace.
- The command table above is derived from the CLI at the time of writing. If the CLI
  gains or changes a command, the command map is the single place that changes, and the
  sync and schema checks enforce agreement.

## Skill placeholder contract

**Contract.** A shared skill body refers to a CLI action only through the marker
`{{ai-team <command> <args…>}}`. The content is the CLI argv without `--json`, and it
uses the existing `<placeholder>` and `[optional]` conventions.

- The claude and codex targets render the marker as the backticked CLI invocation with
  `--json` appended where the command supports it, reproducing today's text exactly.
- The pi target renders it as an instruction to call the `ai_team` tool with the
  equivalent input object.
- Prose mentions of the CLI (for example "the status-report skill runs …") also use the
  marker, so pi-rendered text never refers to running a binary.
- Pi skill headers come from a new `[pi]` section in each skill's `metadata.toml`,
  carrying at least `name` and `description` per the Agent Skills specification that pi
  implements. This adds a target and does not change the Claude/Codex parity decided in
  ADR-001.

## Workflow

```
Maintainer edits a skill body, template or CLI command
  ↓
Run the scaffold sync → claude, codex and pi resources regenerated
  ↓   (fails on unknown command/flag in a placeholder)
Run the Python tests (existing + parity fixtures) and the TS checks (types, unit, parity fixtures)
  ↓   (any fixture diff fails both sides)
★ Maintainer reviews fixture changes if a behaviour change was intended (fixtures are the contract)
  ↓
User: pi install <path to pi package> → new pi session
  ↓
Model loads an AI-team skill → calls ai_team {command, …}
  ↓
Adapter resolves project root from session cwd → core handler → artifact written under lock
  ↓
Model receives a summary plus the JSON payload
```

## Configuration Requirements

- **Clock override (both implementations)**
  - **What must exist:** a single way to fix "today" for artifact creation and archive
    cut-off calculations, so fixtures are deterministic.
  - **Where it lives:** an environment variable shared by both implementations, read in
    exactly one place in each. The name is chosen in the task and recorded in both
    implementations' docs.
  - **Constraints:** ISO-8601 date. Used only for testing, and not documented as a user
    feature.
  - **Missing-value behaviour:** the system date is used, which is today's behaviour.
- **Project root resolution**
  - **What must exist:** the same resolution as the Python locator (explicit root,
    `AI_TEAM_ROOT`, `.ai-team.toml` `[project] dir`, then the default `project` folder),
    starting from the pi session's working directory.
  - **Where it lives:** existing environment variable and project config file. No new
    settings.
  - **Constraints:** unchanged from the Python CLI.
  - **Missing-value behaviour:** a tool error with the same "project root not found"
    message as the CLI, which points to `init`.
- **Isolated pi config for development**
  - **What must exist:** documented use of `PI_CODING_AGENT_DIR` pointing at a scratch
    directory for manual smoke tests.
  - **Where it lives:** the pi package's developer README.
  - **Constraints:** must never point at the developer's real pi agent directory in
    automated tests.
  - **Missing-value behaviour:** automated tests do not start pi at all, so they are
    unaffected.
- **Runtime versions**
  - **What must exist:** a declared minimum Node version and a declared supported pi
    version range for the package.
  - **Where it lives:** the pi package manifest.
  - **Constraints:** the minimum pi version is the one verified during implementation
    (0.87.1 at the time of writing).
  - **Missing-value behaviour:** not applicable, because the fields are required.

## Success Criteria

1. From a clean checkout, the scaffold sync regenerates `pi/resources/` and the claude and
   codex scaffolds. The claude and codex outputs are byte-identical to the pre-change
   outputs, checked by the existing scaffold tests.
2. Every CLI leaf command in the Tool contract table has at least one parity fixture case,
   and every allowed value of every enum flag appears in at least one case.
3. The parity fixtures also cover these edge cases:
   - Unicode and punctuation titles
   - ID gaps and archived IDs
   - Every invalid lifecycle transition
   - Malformed frontmatter for `validate`
   - A broken tree for `check-layout`
   - The `archive` age boundary
4. The same fixture suite passes under the Python runner and the TS runner with zero
   normalisation beyond absolute root paths.
5. Two concurrent TS processes and a concurrent Python/TS pair each creating tasks in the
   same project never produce a duplicate ID across at least 50 repetitions.
6. Type checking of the pi package reports zero errors. Unit and parity tests pass.
7. No file under the pi package's generated skills contains a shell invocation of the
   `ai-team` binary (checked by an automated guard). Every rendered `ai_team` tool-call
   snippet validates against the tool schema (checked by an automated test).
8. Every variant of the tool's input union maps to a core handler, checked by an
   automated test.
9. A manual smoke test is recorded in the task's Work Log, with pi using a scratch
   `PI_CODING_AGENT_DIR`, the package loaded from a local path, and a scratch project.
   In that test, asking the agent to create a task via the new-task skill produces
   `T-001` through the `ai_team` tool without any shell call to `ai-team`.
10. The repo-level checks (`uv run pytest`, `uv run ruff format --check .`,
    `uv run ruff check .`) and the pi package's type and test checks all pass in CI.

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 1 | Parity groundwork in the Python CLI: injectable clock, interoperable lock, fixture format and Python runner, fixtures seeded from the current CLI | Nothing |
| 2 | Pi package skeleton, command map, sync `pi` target with placeholder rendering and `[pi]` headers, skill bodies converted to placeholders (claude/codex output unchanged) | Nothing (parallel with 1) |
| 3 | TS artifact core and TS fixture runner, reaching full parity with the fixture suite | Phase 1 |
| 4 | `ai_team` tool adapter, rendered-skill schema check, binary-invocation guard, manual smoke test, CI wiring | Phases 2 and 3 |

## Amendment Log

<!-- Optional. Use when an approved spec is amended after tasks are in flight.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| YYYY-MM-DD | Description of change | Reason for amendment | T-XXX, T-YYY |
-->
