---
title: "Progress Report — 2026-10-20"
status: draft  # draft | final
created: 2026-10-20
---

# Progress Report — 2026-10-20

## Summary

Active specs: 8. Pending tasks: 0. In progress tasks: 0. Completed tasks: 125. Blocked tasks: 0. Open bugs: 3. Bugs in progress: 0. Resolved bugs: 26. ADRs: 2. Latest integration result: T-125 Session 1 (2026-10-20): I added a sentence to the Gate 5 status paragraph in `cli/docs/usage.md`. It says the integration result is read only from Work Log headings of the exact form `### Session N — YYYY-MM-DD`, with an em dash. It also says a completed task or resolved bug whose sessions use any other heading form reports `not found`. I wrote `cli/tests/test_cr003_usage_status_heading.py` first and saw 4 of its 5 tests fail. It pins the documented wording (AC-1, AC-2) and takes the heading from the doc code span, fills in a number and a date, and checks that `_SESSION_HEADING` matches it (AC-3). The existing `tests/test_usage_guide.py` still passes (AC-4); with `tests/test_status.py` that is 69 passed. The full suite (902 passed), ruff format and ruff check all pass. Committed as f9853209. I made no changes to `status.py`, to the help text or to `commands.md`. Nothing is left over. Reviewers may want to know that the doc-versus-regex check works by replacing `N` and `YYYY-MM-DD` in the documented heading text, so it assumes the doc keeps those placeholders..

## Specifications

| Spec | Status | Notes |
|---|---|---|
| S-002-coordinated-process-and-cli-workflow-improvements.md | approved | Current Gate 5 target |
| S-003-project-layout-diagnostics-and-cli-development-warning.md | approved | Current Gate 5 target |
| S-004-uninterrupted-change-request-and-spec-todo-readiness.md | approved | Current Gate 5 target |
| S-006-local-work-item-tracker.md | approved | Current Gate 5 target |
| S-007-system-overview-spec-s-000.md | approved | Current Gate 5 target |
| S-008-ai-team-cli-documentation.md | approved | Current Gate 5 target |
| S-009-cli-owned-framework-scaffolds.md | approved | Current Gate 5 target |
| S-010-github-actions-ci-for-cli-tests-and-ruff-formatting-checks.md | approved | Current Gate 5 target |

## Integration Evidence

- Latest integration-test result: T-125 Session 1 (2026-10-20): I added a sentence to the Gate 5 status paragraph in `cli/docs/usage.md`. It says the integration result is read only from Work Log headings of the exact form `### Session N — YYYY-MM-DD`, with an em dash. It also says a completed task or resolved bug whose sessions use any other heading form reports `not found`. I wrote `cli/tests/test_cr003_usage_status_heading.py` first and saw 4 of its 5 tests fail. It pins the documented wording (AC-1, AC-2) and takes the heading from the doc code span, fills in a number and a date, and checks that `_SESSION_HEADING` matches it (AC-3). The existing `tests/test_usage_guide.py` still passes (AC-4); with `tests/test_status.py` that is 69 passed. The full suite (902 passed), ruff format and ruff check all pass. Committed as f9853209. I made no changes to `status.py`, to the help text or to `commands.md`. Nothing is left over. Reviewers may want to know that the doc-versus-regex check works by replacing `N` and `YYYY-MM-DD` in the documented heading text, so it assumes the doc keeps those placeholders.
- Source: latest Work Log session of completed tasks and resolved bugs
- Date: 2026-10-20

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
| T-078 | Document the S-000 content contract in the spec authoring guide | developer |
| T-079 | Add the S-000 system-overview template and register it | developer |
| T-080 | Add `ai-team spec new --overview` to create S-000 with duplicate protection | developer |
| T-081 | Refuse `ai-team task new --spec S-000` | developer |
| T-082 | Report tasks that name S-000 as their source spec in `ai-team validate` | developer |
| T-083 | Add the missing-S-000 hint helper and wire it into `validate` and `report` | developer |
| T-084 | Wire the missing-S-000 hint into `spec new`, `adr new` and `status` | developer |
| T-085 | Wire the missing-S-000 hint into `task new`, `bug new` and `change-request new` | developer |
| T-086 | Add the `new-system-overview` skill with greenfield and brownfield paths | developer |
| T-087 | Make spec-breakdown refuse S-000 | developer |
| T-088 | Suggest the system overview from `using-ai-team` and `brainstorm` | developer |
| T-089 | Give the Planner the S-000 session-start rule and skill | developer |
| T-090 | Add S-000 checks to the consistency review and quality gates | developer |
| T-091 | Move system-wide architecture out of the feature spec template | developer |
| T-092 | Update the workflow overview and component map for S-000 | developer |
| T-093 | Regenerate scaffolds and CLI docs and document the new behaviour | developer |
| T-094 | Give the Architect the S-000 session-start rule | developer |
| T-095 | Add a version mismatch warning to every ai-team command | developer |
| T-096 | Read task dependencies from the task body in dev-loop | developer |
| T-097 | Print tool-specific skill invocations in init next steps | developer |
| T-098 | Export Codex skills to .agents/skills through a shared tool path table | developer |
| T-099 | Remove legacy .codex/skills framework copies on init --force | developer |
| T-100 | Report legacy .codex/skills framework folders in check-layout | developer |
| T-101 | Document the .agents/skills export path in usage.md | developer |
| T-102 | Update the guides and README for the .agents/skills export path | developer |
| T-103 | Update repo guidance and ignore rules for the .agents folder | developer |
| T-104 | Add Bash to the Claude Architect agent tools | developer |
| T-105 | Update the evidence rule for roles that all have a shell | developer |
| T-106 | Define design-review Verification and its run context in new-task | developer |
| T-107 | Add the verification run context and design-review option to the task and bug templates | developer |
| T-108 | Add a design-review tasks section to the tdd skill | developer |
| T-109 | Add the per-task verification mode rule to spec-breakdown | developer |
| T-110 | Add the regeneration planning rules to spec-breakdown | developer |
| T-111 | Accept a named design review as Gate 2 verification in spec-breakdown-review | developer |
| T-112 | Tighten the code-review severity rubric for CI and Description findings | developer |
| T-113 | Add the design-review record check to code-review | developer |
| T-114 | Route a deferred Minor that proves a real failure to On FAIL in dev-loop | developer |
| T-115 | Route a deferred Minor that proves a real failure to On FAIL in bug-loop | developer |
| T-116 | Add the verification run context and design-review lookup to integrate | developer |
| T-117 | Show a trailer-capable merge command in integrate | developer |
| T-118 | Describe design-review verification in the quality gates and review checklist | developer |
| T-119 | Describe design-review tasks in the workflow overview and component map | developer |
| T-120 | Copy skill supporting folders into both scaffold exports | developer |
| T-121 | Copy non-UTF-8 scaffold files byte for byte in init | developer |
| T-122 | Document skill supporting-folder export and placeholder rules in the skill template guide | developer |
| T-123 | Remove sandbox_mode from the Codex agent files | developer |
| T-124 | State the parent-session sandbox rule for Codex agents in the guides | developer |
| T-125 | Document the Work Log heading that ai-team status reads | developer |

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
| B-028 | ai-team init --force crashes on a symlinked framework skill folder in .codex/skills | low | open | n/a |
| B-029 | Several tests pass without exercising the behaviour they name | low | open | n/a |
| B-030 | gen_docs.sh --output option is not documented in usage.md | low | open | n/a |
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
| B-018 | ai-team init ignores --create-root-guidance in interactive mode and does not report overwritten files | medium | resolved | complete |
| B-019 | ai-team status reports an arbitrary commit subject as the latest integration result | medium | resolved | complete |
| B-020 | CLI docs tests regenerate the tracked commands.md in place and never detect stale docs | medium | resolved | complete |
| B-021 | ai-team init --dry-run reports root guidance and tracker changes the real run does not make | medium | resolved | complete |
| B-022 | Planner role-file test pins the exact order of the skills frontmatter line | low | resolved | complete |
| B-023 | ai-team init next steps names the non-existent /write-plan skill | low | resolved | complete |
| B-024 | ai-team writes long frontmatter titles wrapped across lines with trailing whitespace | low | resolved | complete |
| B-025 | Test suite does not detect stale Codex skill and project-guidance scaffolds | medium | resolved | complete |
| B-026 | sync_init_scaffolds.py ignores its arguments, so --help and --dry-run rewrite the scaffolds | low | resolved | complete |
| B-027 | usage.md says the scaffold sync copies the repo-local .claude folders instead of the package sources | low | resolved | complete |

## Decisions

| ADR | Title | Status |
|---|---|---|
| ADR-001 | Codex skill frontmatter retains full parity with Claude | accepted |
| ADR-002 | Reconcile approved specs against completed work before Gate 5 | accepted |

## Next Actions

1. No immediate actions.

## Risks and Concerns

- No immediate risks identified.
