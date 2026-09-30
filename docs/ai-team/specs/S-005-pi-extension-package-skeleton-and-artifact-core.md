---
title: 'Pi extension: package skeleton and artifact core'
version: '0.2'
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
deterministic action depends on the Python `ai-team` binary being installed and on
`PATH`. Those actions are creating specs, tasks, bugs, ADRs and change requests, moving
them through lifecycle states, listing, validating and reporting. We want the pi coding
agent to run the whole AI-team process natively as a pi package, and the first
prerequisite is a package that pi can load plus an in-process replacement for the binary.
When this spec is done, `pi install <path-to-pi-package>` gives a pi session an `ai_team`
tool that performs every CLI action with no Python installed. The session also gets
pi-rendered AI-team skills that call that tool instead of the shell. Every action
produces the same artifacts and the same structured result as the Python CLI for the
same inputs. Success is measured by a shared golden-fixture suite that passes against
both implementations.

This is sub-project 1+2 of a five-part effort (1 package skeleton, 2 artifact core,
3 agent runner, 4 process layer, 5 dev/bug loops). Sub-projects 3–5 get their own specs.

## Exclusions

What this specification explicitly does NOT cover:

- **Spawning role agents (agent runner).** Running developer, reviewer, integrator,
  architect and planner as isolated pi subprocesses is sub-project 3. It needs its own
  spec, including the dev container for end-to-end testing, and it owns rendering the
  agent definitions for pi. This spec does not sync or ship agent definitions.
- **Implicit process behaviour and gates.** System-prompt injection, `/` commands for
  the loops, and `tool_call` guards enforcing role rules are sub-project 4.
- **Dev-loop and bug-loop orchestration in pi.** This is sub-project 5. The orchestrator
  skills (`dev-loop`, `bug-loop`, `integrate`) depend on subagent spawning. They are
  rendered for pi by the sync but are left out of the pi package manifest until
  sub-project 5, so a pi session never sees a skill it cannot execute.
- **Retiring or rewriting the Python CLI.** The human chose to keep the Python CLI as the
  implementation for Claude Code and Codex. The TypeScript core is a second
  implementation held to parity by fixtures, not a replacement.
- **A separate copy of skills, agents or templates for pi.** Rejected because the copies
  would drift. Sources stay single-sourced in `cli/src/ai_team/init/sources` and
  `cli/src/ai_team/templates`.
- **A hand-authored pi skill header.** Rejected for the same per-target authoring burden
  that ADR-001 rejected. The pi header is derived from the existing `[claude]` header.
- **One pi tool per CLI command, or tools grouped by artifact type.** Rejected in favour
  of a single CLI-shaped tool, to keep the context cost to one schema and make the skill
  translation mechanical.
- **Leaving skill bodies unchanged and asking the model to translate `ai-team …` calls
  at runtime (preamble approach), or accepting raw argv strings.** Rejected because
  neither can be verified at build time and both undercut the goal of deterministic
  actions.
- **Semantic-only parity, or TypeScript tests that shell out to the Python CLI.**
  Rejected in favour of shared golden fixtures.
- **Cross-implementation locking.** The human chose that each implementation keeps its
  own ID-allocation lock. Python keeps its crash-safe `flock` (the B-014 rationale), and
  the TypeScript core uses its own mechanism. Concurrent ID allocation by a Python process
  and a pi session in the same working tree is documented as unsupported. Separate clones
  never shared the lock anyway, and their ID collisions surface at merge as they do today.
- **New public `--json` flags or a public `check-layout` JSON contract.** Python gains
  structured results only as an internal interface for the fixture runner. The CLI's user
  surface is unchanged, and S-003's deferral of a machine-readable `check-layout` report
  contract still stands.
- **A `pi` value for `[init].tools`.** Adding one would require amending approved S-003
  (its Level 1 and Level 3 tool list). Pi `init` writes an empty tool list instead.
- **Scaffolding `.claude/` or `.codex/` from pi.** Pi's `init` covers only the artifact
  layout and root guidance, because skills and agents come from the package.
- **Publishing to the npm registry.** Install from a local path is enough for this spec.
  npm publishing is a follow-up release-pipeline decision.
- **Fixing S-002's `--filter state` wording drift.** It is pre-existing. The CLI uses
  `--state`, and fixing S-002's wording is a separate amendment to S-002.

## Architecture

### Design Principles

- **The owning guides change first.** The skill-authoring contract, the component map,
  the system overview, the repo agent guide and the setup guide must describe the pi
  target, the placeholder syntax and the parity fixtures before any implementation
  depends on them.
- **Single source of truth for process content.** Every skill body, skill header and
  artifact template that the pi package ships must be generated from the existing
  sources under `cli/src/ai_team/`. Nothing under the pi package's generated resources
  may be hand-edited.
- **Existing exports stay identical.** The generated Claude Code and Codex scaffold trees
  after this work must be byte-identical to those generated on the base commit.
- **Same artifacts, same structured results.** For every fixture case, both
  implementations must produce the same file tree byte for byte, the same exit status,
  and the same structured result. Only absolute root paths are normalised.
- **Deterministic actions never go through the model.** A pi-rendered skill must never
  instruct the model to run the `ai-team` binary. Every deterministic action goes through
  the `ai_team` tool, and every tool-call snippet in a rendered skill must validate
  against the tool schema at build time.
- **Crash-safe exclusion within each implementation.** Within one implementation,
  concurrent allocations never produce the same artifact ID. A crashed holder must never
  leave the project permanently locked, and a lock wait is bounded with the same timeout
  and error text as the Python CLI.
- **The core is free of pi.** The artifact core must be usable and testable without the
  pi runtime. Only a thin adapter depends on the pi extension API.
- **Project root from the session, not the process.** The tool resolves the project from
  the pi session's working directory with the same resolution order as the Python
  locator, so that later child agents running in other directories (worktrees) behave
  correctly.
- **Pi-initialised projects are valid to the Python CLI.** A project initialised by pi
  must pass the Python `check-layout` without findings, and the reverse must also hold.
- **Pi's config is untouched during development.** Manual and automated verification
  must be possible without modifying the developer's real pi agent directory.

### System Diagram

```
 guides/ + ai-process/architecture/ + CLAUDE.md  (updated first: Phase 0)
                               │
 cli/src/ai_team/init/sources ─┤        cli/src/ai_team/templates
  (skill body.md + [claude]/    │                 │
   [codex] headers)             ▼                 ▼
                    ┌──────────────────────────────────────┐
                    │ sync_init_scaffolds.py               │
                    │  targets: claude | codex | pi        │
                    │  renders {{ai-team …}} markers       │
                    │  pi header derived from [claude]     │
                    └───────┬───────────────┬──────────────┘
                            │               │
            cli/…/scaffolds/{claude,codex}  pi/resources/ (generated)
            (byte-identical to base)        skills/ templates/ command map
                                                 │
   pi session ── ai_team tool call ──► pi adapter (schema, hint rewrite, results)
                                                 │
                                                 ▼
                                    TS artifact core (pure, own lock) ──► artifact tree
                                                 ▲                          ▲
                fixtures/parity/ ── vitest ──────┘                          │
                fixtures/parity/ ── pytest ──► Python command modules ──────┘
                                  (structured results, own flock)
```

### Responsibility Separation

| Component | Responsibility | Notes |
|---|---|---|
| Framework docs | Describe the pi target, placeholder contract, command map and parity fixtures | `guides/skill_template.md`, `ai-process/architecture/component-map.md`, `ai-process/architecture/system-overview.md`, `CLAUDE.md`, `guides/setup-guide.md`. Updated before implementation. |
| Scaffold sync (extended) | Renders sources for the claude, codex and pi targets, including marker rendering and pi header derivation | Existing script, gains a `pi` target. Consumes the command map. |
| Command map | Single table of CLI commands, arguments, flags, defaults, tool-field names, and the framework version | Generated or maintained in one place and consumed by the sync, the TS schema and the TS `init`. |
| Pi package manifest | Declares the extension entry and the generated skills to pi, excluding orchestrator skills | Pi host packages are peer dependencies. |
| Pi adapter | Registers the `ai_team` tool, validates input, resolves the project root from the session, and shapes results, errors and pi-specific hints | The only component importing the pi API. |
| TS artifact core | Implements every CLI action: models, IDs, locking, filesystem, locator, layout, validation, templates, command handlers | Pure TypeScript. Injectable clock and version. |
| Parity fixtures | Declare the expected tree, exit status and structured result for each command case | Repo-level. Owned by neither implementation. |
| Fixture runners | Execute every fixture case against one implementation | One pytest runner and one vitest runner. Both auto-discover cases. |
| Python CLI (amended) | Gains an internal structured result for every command, an injectable clock and version, and verbatim marker rendering | The user-facing CLI output and flags are unchanged. |

## Components

### Component 0: Framework guide updates

**Purpose:** Updates the owning guides and architecture docs to the new contract before implementation, as CLAUDE.md requires.
**Estimated size:** Small–medium.
**Interfaces:** Consumed by developers and by every later phase. The skill guide defines the marker syntax, the pi header derivation and the pi applicability of the self-contained `.claude/` rule, `Skill(<name>)` references and `allowed-tools`.

### Component 1: Pi package skeleton

**Purpose:** A `pi/` npm package beside `cli/` that pi loads from a local path, with generated resources and a TypeScript toolchain for type checking and tests.
**Estimated size:** Small.
**Interfaces:** Exposes a pi package manifest (extension entry, non-orchestrator skills). Consumes generated `pi/resources/`.

### Component 2: Scaffold sync pi target and marker rendering

**Purpose:** Extends the existing sync so that shared skill bodies use `{{ai-team …}}` markers, rendered verbatim for claude and codex and as `ai_team` tool instructions for pi, with pi headers derived from `[claude]`.
**Estimated size:** Medium.
**Interfaces:** Consumes skill sources, templates and the command map. Produces the claude, codex and pi resource trees. Fails the sync on unknown commands or flags, and on markers the pi target cannot render.

### Component 3: `ai_team` tool (pi adapter)

**Purpose:** A single model-callable tool whose input is a union discriminated on `command`, mirroring every CLI leaf command. Its output is a short text summary plus the command's structured result.
**Estimated size:** Small–medium.
**Interfaces:** Exposed to the model through pi's tool registration. Consumes the TS artifact core and the session working directory.

### Component 4: TypeScript artifact core

**Purpose:** A one-to-one port of the Python core and command modules, producing identical artifacts and structured results.
**Estimated size:** Large.
**Interfaces:** Exposes one handler per command taking a resolved project root and typed input and returning a structured result. Consumes templates from generated resources, a clock and the framework version.

### Component 5: Shared parity fixtures and runners

**Purpose:** A repo-level golden-fixture suite that both implementations must pass, seeded once from the amended Python CLI and then maintained as the contract.
**Estimated size:** Medium.
**Interfaces:** Fixture cases (command, clock, version, before tree, after tree, exit status, structured result). One runner per implementation.

### Component 6: Python CLI parity amendments

**Purpose:** Gives every command module an internal structured result used by the fixture runner, and adds a single injectable source of "today" and of the framework version.
**Estimated size:** Medium.
**Interfaces:** Structured result per command, internal to the package. Clock and version overrides (see Configuration Requirements). The locking mechanism and the user-facing output are unchanged.

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
| `validate` | — | `all`, `tasks`, `bugs`, `specs`, `adrs`, `changeRequests` (combinable booleans, as in the CLI) |
| `archive` | — | `olderThan`, `dryRun` |
| `check-layout` | — | — |
| `init` | — | `path`, `force`, `dryRun`, `createRootGuidance` |

- The tool never takes a `json` field. Every command returns its structured result as
  the tool's details, plus a one-to-three-line human-readable summary for the model. For
  commands that have a `--json` mode, the structured result is exactly that JSON. For the
  rest, it is the internal structured result defined by this spec and pinned by fixtures.
- `init` in pi omits the CLI's `--tools` and `--no-interactive` options and always behaves
  like the CLI's non-interactive mode. It writes `.ai-team.toml` with an empty
  `[init].tools` list and a `framework_version` equal to the `ai-team` distribution version
  the package was built from. It writes root guidance only when `createRootGuidance` is
  set, and it never emits the "declined" note.
- Domain errors return tool errors whose core message text equals the CLI's error
  output. Examples are an unknown identifier, an invalid state transition, a validation
  failure, a lock timeout, or a project root that isn't found. The adapter may replace
  hints that point at the binary (for example "Run 'ai-team init'") with the equivalent
  tool instruction. The fixtures pin the core message, not the hint. Unexpected exceptions
  come back as tool errors with a one-line message, never a stack trace.
- The tool is not a CLI process and never emits S-003's development warning.
- The command table above is derived from the CLI at the time of writing. If the CLI
  gains or changes a command, the command map is the single place that changes, and the
  sync and schema checks enforce agreement.

## Skill marker contract

**Contract.** A shared skill body refers to a CLI action only through the marker
`{{ai-team <argv>}}`. The content is exactly the text the claude and codex targets emit
today after `ai-team `. That includes `--json` where the body uses it today, and the
existing `<placeholder>` and `[optional]` conventions. Surrounding backticks and code
fences stay in `body.md`, outside the marker.

- **Claude and codex:** the marker renders as `ai-team <argv>`, verbatim. Nothing is
  appended or removed, so today's generated text is reproduced exactly.
- **Pi, call form:** a marker whose argv includes every required positional of its
  command renders as an instruction to call the `ai_team` tool with the equivalent input
  object. `--json` is dropped. A code fence whose only content is markers renders for pi
  as prose tool-call instructions, with no fence. The sync fails if a fence mixes markers
  with other shell lines.
- **Pi, mention form:** a marker whose argv omits required positionals, such as the
  shortened `adr new --json` references in skill introductions, renders as a descriptive
  mention of the `ai_team` tool's command (for example "the `ai_team` tool's `adr new`
  command"), not as a call.
- **Prose mentions:** mentions of the CLI in prose use the marker too, so pi-rendered
  text never refers to running a binary.
- **Pi headers:** derived by the sync from the `name` and `description` in each skill's
  `[claude]` header, per the Agent Skills specification that pi implements. No `[pi]`
  section is authored. This extends ADR-001 to a third target without changing the
  Claude/Codex parity it decided. The Architect records the extension as an ADR.
- **Pi applicability of other skill conventions:** in-body `Skill(<name>)` references,
  the self-contained `.claude/` rule and `allowed-tools` are defined for the pi target by
  the updated skill guide (Phase 0). Only non-orchestrator skills ship in this spec.

## Workflow

```
Maintainer edits a skill body, template or CLI command
  ↓
Run the scaffold sync → claude, codex and pi resources regenerated
  ↓   (fails on unknown command or flag in a marker, or a mixed fence)
Run the Python tests (existing + parity fixtures) and the TS checks (types, unit, parity fixtures)
  ↓   (any fixture diff fails both sides)
★ Maintainer reviews fixture changes if a behaviour change was intended (fixtures are the contract)
  ↓
User: pi install <path to pi package> → new pi session
  ↓
Model loads an AI-team skill → calls ai_team {command, …}
  ↓
Adapter resolves project root from session cwd → core handler → artifact written under the TS lock
  ↓
Model receives a summary plus the structured result
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
- **Framework version (both implementations)**
  - **What must exist:** the value written to `[init].framework_version` and compared by
    `check-layout` must come from a single source. It must equal the `ai-team`
    distribution version in both implementations, with a test-only override so fixtures
    are stable across releases.
  - **Where it lives:** the Python distribution metadata, carried into the pi package by
    the sync (in the command map). The override is an environment variable shared by
    both implementations, read in one place in each.
  - **Constraints:** the same version string format as the Python distribution. The
    override is test-only.
  - **Missing-value behaviour:** the sync fails if it cannot determine the distribution
    version. At runtime, a missing override means the built-in version is used.
- **Project root resolution**
  - **What must exist:** the same resolution as the Python locator (explicit root,
    `AI_TEAM_ROOT`, `.ai-team.toml` `[project] dir`, then the default `project` folder),
    starting from the pi session's working directory.
  - **Where it lives:** existing environment variable and project config file. No new
    settings.
  - **Constraints:** unchanged from the Python CLI.
  - **Missing-value behaviour:** a tool error with the same core "project root not found"
    message as the CLI, with a hint pointing to the tool's `init` command.
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

1. `guides/skill_template.md`, `ai-process/architecture/component-map.md`,
   `ai-process/architecture/system-overview.md`, `CLAUDE.md` and `guides/setup-guide.md`
   describe the pi target, the marker contract, the pi header derivation, the command
   map, the parity fixtures and the pi package checks. They are merged before any Phase 2
   task starts.
2. After the sync, the generated `scaffolds/claude` and `scaffolds/codex` trees are
   byte-identical to those generated on the base commit. This is checked by an automated
   golden comparison. Existing tests that assert on raw `body.md` content are moved to
   assert on rendered output.
3. Every CLI leaf command in the Tool contract table has at least one parity fixture
   case, and every allowed value of every enum flag appears in at least one case.
4. The parity fixtures also cover these edge cases:
   - Unicode and punctuation titles
   - ID gaps and archived IDs
   - Every invalid lifecycle transition
   - Malformed frontmatter for `validate`
   - A broken tree for `check-layout`
   - The `archive` age boundary
   - `init` with and without root guidance
5. The same fixture suite passes under the Python runner and the TS runner. Tree, exit
   status and structured result all match, with no normalisation beyond absolute root
   paths.
6. The Python CLI's user-facing output (stdout, stderr and exit codes) for every existing
   test is unchanged by the structured-result, clock and version amendments.
7. Two concurrent TS processes creating tasks in the same project never produce a
   duplicate ID across at least 50 repetitions. A TS lock holder killed mid-allocation
   does not block the next allocation beyond the bounded wait. The unsupported mixed
   Python/TS case is documented in the pi package README and the setup guide.
8. A project initialised by the pi `init` passes the Python `check-layout` with zero
   findings, and a project initialised by the Python CLI passes the TS `check-layout` with
   zero findings.
9. Type checking of the pi package reports zero errors. Unit and parity tests pass.
10. No file under the pi package's generated skills contains a shell invocation of the
    `ai-team` binary (checked by an automated guard). Every call-form `ai_team` snippet in
    a rendered pi skill validates against the tool schema (checked by an automated test).
    The pi manifest ships no orchestrator skill.
11. Every variant of the tool's input union maps to a core handler, checked by an
    automated test.
12. A manual smoke test is recorded in the task's Work Log, with pi using a scratch
    `PI_CODING_AGENT_DIR`, the package loaded from a local path, and a scratch project.
    In that test, asking the agent to create a task via the new-task skill produces
    `T-001` through the `ai_team` tool without any shell call to `ai-team`.
13. The repo-level checks (`uv run pytest`, `uv run ruff format --check .`,
    `uv run ruff check .`) and the pi package's type and test checks all pass.

## Implementation Order

| Phase | What | Depends On |
|---|---|---|
| 0 | Framework guide and architecture doc updates. Architect records the ADRs for the pi header derivation and the per-implementation lock decision | Nothing |
| 1 | Python parity groundwork: structured result per command, injectable clock and version, fixture format and Python runner, fixtures seeded from the amended CLI | Phase 0 |
| 2 | Command map, sync `pi` target with marker rendering and derived pi headers, skill bodies converted to markers, scaffold golden comparison, pi package skeleton | Phase 0 (parallel with 1) |
| 3 | TS artifact core, TS lock, and TS fixture runner, reaching full parity with the fixture suite | Phases 1 and 2 |
| 4 | `ai_team` tool adapter, rendered-skill schema check, binary-invocation guard, manual smoke test, CI wiring | Phase 3 |

## Amendment Log

<!-- Optional. Use when an approved spec is amended after tasks are in flight.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| YYYY-MM-DD | Description of change | Reason for amendment | T-XXX, T-YYY |
-->
