---
id: "T-029"
title: "Add CLI-to-skills mapping to component-map.md"
status: pending
priority: medium
assigned-role: "unassigned"
created: 2026-05-14
---

# Add CLI-to-skills mapping to component-map.md

## Description

Per spec `project/specs/ai-team-cli-documentation.md` (Phase 3, Component 4), the architecture layer must record where the `ai-team` CLI is used together with the skills. `ai-process/architecture/component-map.md` currently does not mention the CLI at all.

Add a section (or table) to `ai-process/architecture/component-map.md` mapping each action skill to the `ai-team` command(s) it invokes:
- `new-spec` → `ai-team spec new`
- `new-task` → `ai-team task new`
- `new-bug` → `ai-team bug new`
- `new-adr` → `ai-team adr new`
- `status-report` → `ai-team status` + `ai-team report`

Confirm the exact skill→command pairs against the current `.claude/skills/*/SKILL.md` files before writing — the mapping must reflect what the skills actually invoke. This task changes only the architecture document; no skill files are modified.

## Acceptance Criteria

AC-1: The system shall add a section to `ai-process/architecture/component-map.md` mapping action skills to the `ai-team` commands they invoke.
AC-2: The system shall include the mappings for `new-spec`, `new-task`, `new-bug`, `new-adr`, and `status-report`, each matching the command(s) named in that skill's `SKILL.md`.
AC-3: IF a skill's `SKILL.md` invokes a CLI command not listed above THEN THE SYSTEM SHALL include that mapping as well.
AC-4: The system shall not modify any file under `.claude/skills/`.

## Dependencies

- None

## Files to Touch

- `ai-process/architecture/component-map.md` — add CLI-to-skills mapping section

## Verification

```bash
grep -q "ai-team" ai-process/architecture/component-map.md
grep -q "status-report" ai-process/architecture/component-map.md
git diff --name-only | grep -qv "^.claude/skills/" && echo "no skill files changed"
```

## Work Log

### Session 1 — 2026-05-14

Read the task file and confirmed the Work Log was empty (first session). Read all five action skill SKILL.md files (`new-spec`, `new-task`, `new-bug`, `new-adr`, `status-report`) to confirm the exact CLI commands each invokes before writing anything. The mappings matched what the task anticipated: `new-spec` → `ai-team spec new`, `new-task` → `ai-team task new`, `new-bug` → `ai-team bug new`, `new-adr` → `ai-team adr new`, `status-report` → `ai-team status` + `ai-team report`.

Ran the three task verification commands before the edit to establish the red state: `ai-team` was not present in `component-map.md` (the key failing check). Added a `## CLI Command Mapping` section immediately before the `## Interaction Diagram` section — chosen because it follows the existing `## Documents and Directories` section thematically, and the interaction diagram is the natural closing element of the document. No alternative placements were considered seriously; this position groups architectural metadata together.

All three verification commands pass. No skill files were modified. Committed as `docs(architecture): add CLI command mapping section to component-map` on `task/T-029-map-cli-to-skills-in-component-map`.

Nothing remains for this task.

## Review
