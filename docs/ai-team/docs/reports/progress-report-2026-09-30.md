---
title: "Progress Report — 2026-09-30"
status: draft  # draft | final
created: 2026-09-30
---

# Progress Report — 2026-09-30

## Summary

Active specs: 4. Pending tasks: 35. In progress tasks: 0. Completed tasks: 90. Blocked tasks: 0. Open bugs: 1. Bugs in progress: 0. Resolved bugs: 16. ADRs: 4. Latest integration result: chore(tasks): merge T-090 seed fixtures for lifecycle transitions.

## Specifications

| Spec | Status | Notes |
|---|---|---|
| S-002-coordinated-process-and-cli-workflow-improvements.md | approved | Current Gate 5 target |
| S-003-project-layout-diagnostics-and-cli-development-warning.md | approved | Current Gate 5 target |
| S-004-uninterrupted-change-request-and-spec-todo-readiness.md | approved | Current Gate 5 target |
| S-005-pi-extension-package-skeleton-and-artifact-core.md | approved | Current Gate 5 target |

## Integration Evidence

- Latest integration-test result: chore(tasks): merge T-090 seed fixtures for lifecycle transitions
- Source: git log --all --grep=merge|integration|verification|test -n 1
- Date: 2026-09-30

## Completed

| Task ID | Title | Agent Role |
|---|---|---|
| T-001 | Bootstrap cli/ uv project with Typer scaffold and command auto-discovery | developer |
| T-002 | Implement project root locator | developer |
| T-003 | Implement frontmatter parser and artifact data models | developer |
| T-004 | Implement filesystem layer for artifact reads, writes, and atomic moves | developer |
| T-005 | Implement ai-team list command | developer |
| T-006 | Implement ai-team show command | developer |
| T-007 | Implement ai-team status command | developer |
| T-008 | Implement artifact ID allocator | developer |
| T-009 | Bundle artifact markdown templates and implement template loader | developer |
| T-010 | Implement ai-team task new command | developer |
| T-011 | Implement ai-team bug new command | developer |
| T-012 | Implement ai-team spec new command | developer |
| T-013 | Implement ai-team adr new command | developer |
| T-014 | Implement task lifecycle commands (start, complete, block, unblock) | developer |
| T-015 | Implement bug lifecycle commands (start, resolve) | developer |
| T-016 | Implement ai-team archive command | developer |
| T-017 | Implement ai-team validate command | developer |
| T-018 | Implement ai-team report command and bundle progress-report template | developer |
| T-019 | Migrate status-report skill to invoke ai-team CLI | developer |
| T-020 | Migrate new-task skill to invoke ai-team CLI | developer |
| T-021 | Migrate new-bug skill to invoke ai-team CLI | developer |
| T-022 | Migrate new-spec skill to invoke ai-team CLI | developer |
| T-023 | Migrate new-adr skill to invoke ai-team CLI | developer |
| T-024 | Bundle init scaffold assets and add sync helper | developer |
| T-025 | Implement ai-team init command | developer |
| T-026 | Document install in setup-guide and verify end-to-end packaging | developer |
| T-027 | Add typer-cli dependency, gen_docs script, and generate commands.md | unassigned |
| T-028 | Write cli/docs/usage.md hand-written CLI guide | unassigned |
| T-029 | Add CLI-to-skills mapping to component-map.md | unassigned |
| T-030 | Archive the ai-team-python-cli development spec | unassigned |
| T-031 | Link README/setup-guide to cli/docs and add regeneration Contributing rule | unassigned |
| T-032 | Add Ruff tooling configuration to the ai-team CLI | developer |
| T-033 | Apply the one-time Ruff format and lint-fix pass over the CLI | developer |
| T-034 | Add the GitHub Actions CI workflow for the ai-team CLI | developer |
| T-035 | Implement package-owned scaffold source generator | developer |
| T-036 | Migrate shared skill sources into the CLI package | developer |
| T-037 | Add package-owned Claude and Codex agent scaffolds | developer |
| T-038 | Remove ai-process export behavior from init | developer |
| T-039 | Update init tests for Codex scaffolds and removed ai-process export | developer |
| T-040 | Refresh CLI command documentation for init changes | developer |
| T-041 | Update framework documentation for CLI-owned scaffold sources | developer |
| T-042 | Regenerate Claude and Codex skill scaffold outputs | developer |
| T-043 | Regenerate Claude and Codex agent scaffold outputs | developer |
| T-044 | Update spec breakdown docs and test planning | planner |
| T-045 | Narrow Gate 2 review to technical criteria | architect |
| T-046 | Add change request core artifact support | developer |
| T-047 | Implement change request CLI creation | developer |
| T-048 | Add change request listing and validation | developer |
| T-049 | Add project guidance templates to init scaffolds | developer |
| T-050 | Prompt for root guidance files during init | developer |
| T-051 | Update dev loop startup queue and test guards | planner |
| T-052 | Refresh framework docs for workflow improvements | planner |
| T-053 | Regenerate scaffolds and CLI command documentation | developer |
| T-054 | Add change request storage and template loading | developer |
| T-055 | Generate project guidance files in init scaffolds | developer |
| T-056 | Prefix new spec filenames with S-NNN- identifier | developer |
| T-057 | Update Codex generated agent model defaults | developer |
| T-058 | Reconcile test-discovery, Gate 5 producer, and bug-evidence wording in workflow-overview | unassigned |
| T-059 | Add Gate 2 coverage and committed-evidence checks to quality-gates | unassigned |
| T-060 | Add no-routine-forced-branch-deletion rule to git-conventions guideline | unassigned |
| T-061 | Strengthen the bug evidence chain across debug, tdd, and code-review skills | unassigned |
| T-062 | Clarify planning-skill boundaries, EARS pointer, and Gate 2 output format | unassigned |
| T-063 | Add committed-PASS gate, lifecycle protection, and safe branch deletion to integration | unassigned |
| T-064 | Consolidate canonical git-conventions and escalation-review skill bodies to source | unassigned |
| T-065 | Update Claude agent role files to the reviewed state in source | unassigned |
| T-066 | Record the Codex skill-frontmatter parity decision | unassigned |
| T-067 | Re-render init scaffolds and verify both skill exports | unassigned |
| T-068 | Add a Common Pitfalls section to the change-request skill body | unassigned |
| T-069 | Add the global CLI development warning | developer |
| T-070 | Implement layout structure and version checks | developer |
| T-071 | Add artifact and guidance layout checks | developer |
| T-072 | Add the check-layout command and report | developer |
| T-073 | Document layout diagnostics and development warning | developer |
| T-074 | Add uninterrupted change-request continuation to source skills | developer |
| T-075 | Update process docs for TODO-ready specs and change requests | developer |
| T-076 | Add spec TODO readiness to source spec-authoring skills | developer |
| T-077 | Regenerate S-004 skill scaffolds | developer |
| T-078 | Update the skill guide for the pi target and the marker contract | developer |
| T-079 | Update the component map and system overview | developer |
| T-080 | CLAUDE.md pi checks and setup-guide pi install steps | developer |
| T-081 | Injectable "today" and framework version in the Python CLI | developer |
| T-082 | Structured-result type; apply to spec new, adr new, change-request new | developer |
| T-083 | Structured results for task and bug commands | developer |
| T-084 | Structured results for list, show, status, report | developer |
| T-085 | Structured results for validate, archive, check-layout | developer |
| T-086 | Structured result for init with internal empty-tools mode | developer |
| T-087 | TS lock entry in skeleton .gitignore; update B-017 tests and usage guide | developer |
| T-088 | Parity fixture format and Python fixture runner | developer |
| T-089 | Seed fixtures for artifact-creation commands | developer |
| T-090 | Seed fixtures for lifecycle transitions | developer |

## In Progress

| Task ID | Title | Agent Role | Notes |
|---|---|---|---|
| none | n/a | n/a | no in-progress tasks |

## Blocked

| Task ID | Title | Blocked By | Action Needed |
|---|---|---|---|
| none | n/a | n/a | no action needed |

## Bugs

| Bug ID | Title | Severity | Status | Diagnosis Status |
|---|---|---|---|---|
| B-018 | task block inserts Work Log entry above a newly created Work Log heading | low | open | n/a |
| B-001 | ai-team spec new CLI does not match new-spec skill contract and leaves body title placeholder | medium | resolved | complete |
| B-002 | code-review skill reviewer mis-scopes git — stages implementation files into the verdict commit and reviews working-tree contents instead of the branch diff | high | resolved | complete |
| B-003 | ai-team task new does not substitute the body title placeholder | medium | resolved | complete |
| B-004 | ai-team report aborts on resolved bug artifacts missing 'created' frontmatter | medium | resolved | complete |
| B-005 | ai-team spec new duplicate-ID allocation ignores existing spec IDs | medium | resolved | complete |
| B-006 | Change-request init scaffolding is incomplete | high | resolved | complete |
| B-007 | Dev-loop baseline test discovery is too rigid | medium | resolved | complete |
| B-008 | new-adr callers pass unsupported 'context' field instead of 'description' | high | resolved | complete |
| B-010 | Loops never invoke status-report, leaving the Gate 5 summary orphaned | medium | resolved | complete |
| B-011 | Accepted ADR changes can leave approved specs stale without validation findings | medium | resolved | complete |
| B-012 | Integrate task completion can leave the in-progress path tracked | medium | resolved | complete |
| B-013 | ai-team validate reports task-spec-missing for spec references the CLI itself creates | high | resolved | complete |
| B-014 | Concurrent ai-team task new calls allocate duplicate IDs | high | resolved | complete |
| B-015 | integrate post-merge regression check reuses the task-scoped verification command | medium | resolved | complete |
| B-016 | Developer role has no enforced boundary against committing lifecycle files on task branches | medium | resolved | complete |
| B-017 | ai-team task/bug/spec new leaves an untracked .ai-team.lock sentinel with no gitignore guidance | low | resolved | complete |

## Decisions

| ADR | Title | Status |
|---|---|---|
| ADR-001 | Codex skill frontmatter retains full parity with Claude | accepted |
| ADR-002 | Pi skill headers are derived from the Claude header | accepted |
| ADR-003 | Each implementation owns its ID-allocation lock; mixed concurrent allocation is unsupported | accepted |
| ADR-004 | Two implementations held to a shared parity-fixture contract | accepted |

## Next Actions

1. No immediate actions.

## Risks and Concerns

- No immediate risks identified.
