# AI Process Fixes and CLI Improvements Change Request

## Purpose

Plan a focused round of fixes and improvements for the AI-team framework. The changes mix process steering, a new lightweight planning skill, and CLI scaffold behavior improvements.

## Requested Changes

### 1. Keep Project Documentation Updated During Task Planning

Agents currently miss documentation updates when breaking work into tasks. Add explicit steering so documentation changes are considered during task creation and task-plan review.

Potential implementation points:
- `cli/src/ai_team/init/sources/skills/new-task/body.md`
- `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md`
- `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md`
- Generated scaffold outputs under `cli/src/ai_team/init/scaffolds/` after regeneration

Expected behavior:
- Task authors must consider whether the change requires updates to README, guides, CLI docs, command docs, project docs, or other user-facing documentation.
- If documentation must change, the relevant files must appear in `Files to Touch` and acceptance criteria or verification must cover the documentation update.
- If no documentation update is needed, the task should state why in the task body or reviewer-visible context.
- Gate 2 preflight should flag task plans that implement user-facing, CLI, workflow, or contract changes without a corresponding documentation task or an explicit no-docs rationale.

### 2. Add `change-request` Skill

Create a new skill named `change-request` for smaller changes that do not need a full specification.

Intent:
- Follow a similar discovery pattern to `brainstorm`.
- Use a lighter process for bounded, single-task changes.
- Create exactly one task directly when the request is small enough.
- Refuse to force larger work into one task.

Expected behavior:
- The skill clarifies only material unknowns.
- The skill checks existing specs, decisions, tasks, and docs for conflicts.
- Before creating or assigning a development task, the skill must verify the
  relevant project test suite is already green using the documented project
  test command.
- Preexisting test failures are a blocking condition: if baseline tests fail
  before implementation starts, the change request must stop, record the
  failing command and failure summary, and require the failures to be resolved
  or explicitly reclassified before a dev session begins.
- If the change can fit in one atomic, one-shottable task, it invokes `new-task`.
- If the change cannot fit in one task, or if it alters the framework contract substantially, it tells the agent to suggest creating a full spec instead.
- The skill should include the same documentation-update expectation described above.

Potential implementation points:
- New source skill under `cli/src/ai_team/init/sources/skills/change-request/`
- Planner agent skill list updates for Claude and Codex source agents
- Component map and setup/customization docs if they list available skills
- Scaffold regeneration and tests for source/scaffold parity

### 3. Update `ai-team init` To Generate Root Agent Instructions

Update the CLI `init` command so initialized repositories receive the main agent instruction file in the repository root.

Expected behavior:
- For Claude initialization, generate `CLAUDE.md` in the target repository root.
- For Codex initialization, generate `AGENTS.md` in the target repository root.
- If both tools are selected, define whether both files are generated or whether one combined/default behavior applies. Prefer generating both to keep tool behavior explicit.
- Existing collision and `--force` behavior should apply to these root files.
- `--dry-run` should report these files.

Potential implementation points:
- Add source templates under `cli/src/ai_team/init/sources/`
- Add generated scaffold assets under `cli/src/ai_team/init/scaffolds/`
- Update `cli/src/ai_team/commands/init.py`
- Update init tests
- Regenerate `cli/docs/commands.md` if command output or documented behavior changes
- Update `guides/setup-guide.md` and `guides/customization-guide.md`

### 4. Update `ai-team init` To Generate Project-Folder Agent Instructions

Update the CLI `init` command so the created `project/` folder also contains agent instructions for working with tasks, specs, bugs, decisions, reports, and docs.

Expected behavior:
- For Claude initialization, generate `project/CLAUDE.md`.
- For Codex initialization, generate `project/AGENTS.md`.
- The file should explain the purpose of `project/tasks/`, `project/specs/`, `project/bugs/`, `project/decisions/`, and `project/docs/`.
- It should reinforce lifecycle constraints, including where agents may create or move artifacts.
- Existing collision and `--force` behavior should apply.
- `--dry-run` should report these files.

Potential implementation points:
- Add project-folder agent-guide templates to scaffold sources
- Update init copy planning
- Update tests for selected tools, collisions, force, and dry-run
- Update setup/customization documentation

## Suggested Breakdown

This change request likely should become a full spec rather than one task because it includes multiple independent outcomes across skill sources, agent source metadata, CLI behavior, tests, generated scaffolds, and documentation.

Suggested task groups:
- Add documentation-update steering to task creation, task breakdown, and Gate 2 review.
- Add the `change-request` skill and wire it into planner-facing tool definitions.
- Add a baseline test-green preflight to the `change-request` flow, treating
  preexisting test failures as blocking before any dev session starts.
- Add root-level `CLAUDE.md` and `AGENTS.md` scaffold generation in `ai-team init`.
- Add `project/CLAUDE.md` and `project/AGENTS.md` scaffold generation in `ai-team init`.
- Update tests, generated scaffolds, setup/customization docs, component map, and command docs.

## Acceptance Notes

- Source-of-truth changes should be made under `cli/src/ai_team/init/sources/` first.
- Generated scaffold output should be regenerated with `python scripts/sync_init_scaffolds.py` from `cli/`.
- CLI verification should include `uv run pytest`, `uv run ruff format --check .`, and `uv run ruff check .` from `cli/`.
- The resulting `change-request` process must require a passing baseline test
  run before a development session starts, and must block on any preexisting
  test errors unless they are first resolved or formally reclassified.
- Documentation impact must be explicitly covered in the resulting task plan.
