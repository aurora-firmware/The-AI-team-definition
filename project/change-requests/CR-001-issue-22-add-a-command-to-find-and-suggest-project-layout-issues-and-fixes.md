---
id: CR-001
title: 'Issue 22: add a command to find and suggest project layout issues and fixes'
status: rejected
created: '2026-06-24'
---

# Issue 22: add a command to find and suggest project layout issues and fixes

## Desired Changes

Add an `ai-team check-layout` command that inspects the current repository for the project layout expected by the CLI and reports missing or misplaced files and directories together with suggested fixes. Include checks for framework-critical paths such as `project/`, lifecycle subdirectories, and agent/skill scaffold locations used by the tooling. Also add a clear CLI under development banner so users know the tool is still evolving and where to report issues.

Constraints:
- The command should diagnose layout problems without modifying files.
- Output should identify what is missing and how to fix it.
- The detailed validation contract is owned by S-003.

## Context

Very often the project layout does not match what the CLI expects, which causes commands to fail later with less actionable errors. Issue #22 requests a direct `ai-team check-layout` command so users can validate repository structure early and understand what is missing. The under-development banner is requested to set expectations and direct issue reporting.

Affected artifacts:
- GitHub issue #22: `add a command to find and suggest project layout issues and fixes`
- `project/specs/S-003-project-layout-diagnostics-and-cli-development-warning.md`
- CLI command and usage documentation under `cli/docs/`
- CLI implementation under `cli/src/ai_team/commands/` and any supporting validation or locator modules

## Potential Impact

- Adds a new user-facing CLI command and command-output surface.
- May require updates to specs, usage docs, and generated command documentation.
- May overlap with existing project-root or validation logic, so command scope boundaries must be defined clearly.
- Risk: if the layout rules are incomplete or too strict, the command could produce misleading guidance.
- Risk: banner placement may affect command output expectations or tests.
- Migration considerations: S-003 excludes changes to existing command failures;
  users invoke `check-layout` directly.

## Possible Spec Amendments

This request was promoted to the standalone specification
`project/specs/S-003-project-layout-diagnostics-and-cli-development-warning.md`
because the command, hierarchical validation contract, and process-wide banner
form an isolated capability large enough to require Gate 1 approval.

Open questions:
- Resolved in S-003: the first release has four ordered validation levels.
- Resolved in S-003: the one-line banner appears on every CLI invocation.
- Resolved: this change is promoted to a new specification.
