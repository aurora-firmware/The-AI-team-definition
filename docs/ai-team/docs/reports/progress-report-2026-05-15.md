---
title: "Progress Report — 2026-05-15"
date: 2026-05-15
generated_by: status-report skill (manual fallback)
---

# Progress Report — 2026-05-15

> **Note.** `ai-team report` could not generate this file automatically. It aborts on
> `project/bugs/resolved/B-001-...md` because that artifact's frontmatter lacks the
> required `created` field (`FrontmatterError`). The defect is tracked as **B-004**,
> filed today. This report was assembled manually per the `status-report` skill's
> fallback path. Once B-004 is fixed, future reports will be CLI-generated.

## Summary

- Active specs: 3 (all `approved`)
- Pending tasks: 0
- In progress: 0
- Completed: 43
- Blocked: 0
- Open bugs: 2 (0 critical/high)
- Bugs in progress: 0
- Resolved bugs: 2
- ADRs: 0
- Latest integration result: `chore(tasks): merge T-041 update-framework-documentation-for-cli-owned-scaffold-sources` on `dev-agent`

## Specifications

| ID / Filename | Title | Status | Created |
|---|---|---|---|
| `ai-team-cli-documentation.md` | ai-team CLI Documentation | approved | 2026-05-14 |
| `cli-owned-framework-scaffolds-and-remove-ai-process-init-export.md` | CLI-owned framework scaffolds and remove ai-process init export | approved | 2026-05-14 |
| `github-actions-ci-for-cli-tests-and-ruff-formatting-checks.md` | GitHub Actions CI for CLI tests and Ruff formatting checks | approved | 2026-05-14 |

All three specs are approved. Their tasks are tracked under the completed task IDs below.

## Completed Tasks

43 tasks have been completed and merged into `dev-agent`. Recent integrations (most recent last):

- T-034 — Add the GitHub Actions CI workflow for the ai-team CLI
- T-035 — Implement package-owned scaffold source generator
- T-036 — Migrate shared skill sources into the CLI package
- T-037 — Add package-owned Claude and Codex agent scaffolds
- T-038 — Remove ai-process export behavior from init
- T-039 — Update init tests for Codex scaffolds and removed ai-process export
- T-040 — Refresh CLI command documentation for init changes
- T-041 — Update framework documentation for CLI-owned scaffold sources
- T-042 — Regenerate Claude and Codex skill scaffold outputs
- T-043 — Regenerate Claude and Codex agent scaffold outputs

The full list lives under `project/tasks/completed/`.

## In Progress

None.

## Blocked

None.

## Open Bugs

| ID | Title | Severity | Notes |
|---|---|---|---|
| B-003 | ai-team `task new` does not substitute the body title placeholder | medium | Filed 2026-05-15. Tracks I-007. Same defect class as B-001 (which fixed `spec new` and `bug new`); `task new` in `cli/src/ai_team/commands/task.py` was missed. |
| B-004 | ai-team `report` aborts on resolved bug artifacts missing `created` frontmatter | medium | Filed 2026-05-15. Tracks I-008. Currently blocks `ai-team report` from running, hence this manual fallback report. |

No critical or high severity bugs are open.

## Resolved Bugs

| ID | Title | Resolved |
|---|---|---|
| B-001 | `ai-team spec new` CLI does not match `new-spec` skill contract; body title placeholder | 2026-05-14 |
| B-002 | `code-review` skill: Reviewer mis-scopes git operations | 2026-05-14 |

## Integration Evidence

Most recent integration on `dev-agent`:

```
02386e5 chore(bugs): file B-003 and B-004 for I-007 and I-008
14a6efc docs(framework): codify spec-authoring contract and CLI-sources ownership
75c3c92 chore(tasks): move T-041 to completed
437a359 chore(tasks): merge T-040 refresh-cli-command-documentation-for-init-changes
... (T-039, T-038, T-043 merges precede)
```

CLI test suite on `dev-agent`: **228 passed**, 0 failed (last run after the I-006 fix and scaffold regeneration on 2026-05-15).

## Recently Closed: I-006

I-006 ("specifications tend to embed implementation code") was closed today. The fix added
`guides/spec-authoring-guide.md` as a human-readable authoring playbook, embedded the
section-by-section recipes into `cli/src/ai_team/init/sources/skills/new-spec/body.md` so
the Planner has them in-flight when `/new-spec` fires, and reworked the spec template
(`cli/src/ai_team/templates/spec.md`) to carry an authoring hint on every section.
`CLAUDE.md` was updated to clarify that the CLI sources under
`cli/src/ai_team/init/sources/` are the product source-of-truth and that `.claude/` /
`.codex/` in this repo are local agent configuration only.

## Next Actions

1. **Fix B-003** — one-line fix in `cli/src/ai_team/commands/task.py` mirroring B-001's
   change to `spec.py` / `bug.py`. Add a regression test analogous to
   `test_spec_new_substitutes_body_h1_with_provided_title`.
2. **Fix B-004** — harden `cli/src/ai_team/commands/report.py` so resolved bug artifacts
   missing optional frontmatter fields do not abort report generation. Add a regression
   test using a resolved artifact whose frontmatter omits `created`.
3. **Once B-004 lands**, re-run `ai-team report` to verify the CLI-generated report
   produces a Gate-5-ready summary on its own.
4. **Optional cleanup** — the test
   `test_package_owned_agent_sources_cover_each_exported_role_for_both_tools` still
   asserts byte parity between `cli/src/ai_team/init/sources/agents/codex/` and the
   repo-root `.codex/agents/`. After the ownership-model update, `.codex/` is local
   config and not authoritative. Consider inverting or removing that assertion in a
   follow-up.

## Risks / Concerns

- **CLI-generated reports are currently blocked by B-004.** Until the bug is fixed,
  Gate 5 reports require this manual fallback. Severity is medium because the report
  is the only blocked surface; the rest of the CLI runs cleanly.
- **The completed-tasks queue is unusually large for one window (43).** Confirm the
  spec scopes are still distinct before merging `dev-agent` to `main` — Gate 5 is a
  sign-off, not a code review, but the human should still verify the bundle matches
  the three approved specs' intent.

## Gate 5 Readiness

- Approved specs: 3 ✓
- Completed tasks: 43, all merged into `dev-agent` ✓
- Open critical/high bugs: 0 ✓
- Blocked tasks: 0 ✓
- Latest integration test result: green (228/228 passing) ✓
- Outstanding medium bugs that should be tracked but do not block Gate 5: B-003, B-004.

The branch appears Gate-5-ready pending the human's spec-intent sign-off.
