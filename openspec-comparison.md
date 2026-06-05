# OpenSpec Comparison

## What OpenSpec Does

OpenSpec is an AI-native spec-driven development framework. It adds an `openspec/` planning layer to a project, where `specs/` describe current system behavior and `changes/` hold proposed modifications until they are applied, synced, and archived. It emphasizes lightweight, iterative planning for brownfield projects and exposes AI-assistant slash commands such as `/opsx:propose`, `/opsx:apply`, and `/opsx:archive`.

## CLI Usage

OpenSpec CLI examples:

```bash
openspec init
openspec update
openspec list
openspec show <item>
openspec validate --all
openspec archive <change>
openspec status
openspec config profile
openspec workspace setup
openspec schema init <name>
```

AI Team Definition CLI examples:

```bash
ai-team init . --tools codex --no-interactive
ai-team task new "Add onboarding" --priority high --assigned-role developer
ai-team task start T-001
ai-team task complete T-001
ai-team bug new "Login crashes" --severity high
ai-team spec new "Billing reconciliation"
ai-team adr new "Use PostgreSQL"
ai-team validate --all
ai-team status
ai-team report
ai-team archive --dry-run
```

## Similarities

- Both CLIs scaffold AI-agent workflow files into target repositories.
- Both support multiple AI tools, including Claude and Codex.
- Both maintain project-local planning artifacts in predictable folders.
- Both include lifecycle commands for listing, showing, validating, status reporting, and archiving.
- Both expose JSON output for agent/script usage on several read/validation commands.
- Both separate framework/package source from generated project scaffolds.
- Both rely on assistant-facing commands or skills for daily AI workflow execution, while the terminal CLI manages files and state.

## Differences

- OpenSpec is a Node/TypeScript npm package named `@fission-ai/openspec`; AI Team CLI is a Python/Typer package named `ai-team`.
- OpenSpec centers on `openspec/specs/` and `openspec/changes/`; AI Team centers on `project/specs/`, `project/tasks/`, `project/bugs/`, `project/decisions/`, and reports.
- OpenSpec's primary workflow is change/spec driven: propose, explore, apply, sync, archive. AI Team's workflow is role/process driven: spec approval, task breakdown, dev loop, review, integration, bug loop, Gate 5 report.
- OpenSpec provides many slash commands directly under `/opsx:*`; AI Team provides skills such as `/new-task`, `/dev-loop`, `/bug-loop`, and `/status-report` that delegate to `ai-team`.
- OpenSpec has interactive dashboard and configuration commands: `view`, `config`, `completion`, `feedback`.
- AI Team has first-class task, bug, spec, and ADR creation/lifecycle commands.
- OpenSpec includes schema customization commands: `schema init`, `schema fork`, `schema validate`, `schema which`.
- AI Team includes explicit Gate 5 reporting via `ai-team status` and `ai-team report`.
- OpenSpec has beta workspace support for coordinating multiple repos/folders. AI Team does not expose an equivalent workspace abstraction.
- OpenSpec supports a larger list of AI tools; AI Team currently documents Claude Code and Codex as exported platform targets.
- OpenSpec initializes with `openspec init [path] --tools ...`; AI Team initializes with `ai-team init [PATH] --tools ... --no-interactive`.
- OpenSpec has `update` to regenerate assistant instruction files after package/profile changes. AI Team's docs emphasize rebuilding bundled scaffolds before packaging, not an equivalent target-project update command.

## Notes And Implications

- OpenSpec is broader as a general-purpose spec/change workflow layer for many AI tools.
- AI Team Definition is stricter and more operational: it defines roles, quality gates, artifact states, and autonomous loops.
- OpenSpec may be a useful reference for CLI ergonomics: `update`, `config profile`, `completion`, `view`, workspace commands, and schema extensibility.
- AI Team's stronger artifact lifecycle may be better for controlled multi-agent development where task state, review, integration, bugs, ADRs, and final sign-off need explicit tracking.
