---
id: T-102
title: Convert new-adr and change-request to markers
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Convert new-adr and change-request to markers

<!--
Task Quality Rules (see the new-task skill for full details):
  - Atomic — one clear outcome.
  - One-shottable — ≤ 3–4 files touched, ≤ 5 ACs, Description ≈ 20 lines.
  - Verifiable — concrete Verification command or explicit manual steps.
  - Self-contained — Description is enough to start without follow-up questions.
  - EARS — every AC matches one of the five EARS patterns below.
  - Dependency-honest — list every prior task this one reads from or modifies.
-->

## Description

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P25 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- as T-101; plus the Phase 2 render assertion for the new-adr --supersedes site (bare `supersedes` inside backticks for pi, unchanged for claude/codex).
- Per Architect escalation ruling 2026-10-01: noun/flag markers are allowed in fences without command markers; a fence containing any command marker must hold only command markers. A fence is a command fence iff it contains a `{{ai-team ` command marker. `skill_markers.py` `render_fence` returns non-command fences unchanged so the inline pass renders their noun/flag markers. AC-1 stays as written, including fenced text.

## Acceptance Criteria

AC-1: every reference uses a marker.
AC-2: V-GOLD (SC-2).
AC-3: supersedes as bare field, no nested span (Inline context).
AC-4: shortened adr new --json intros render as mention form.
AC-5: no lowercase ai-team in pi output (SC-10).

## Dependencies

- `T-097` — Move raw-body/raw-header test assertions to rendered output
- `T-099` — Pi target in the sync; generate pi/resources/

## Files to Touch

- sources/skills/{new-adr,change-request}/{body.md,metadata.toml}
- generated pi output
- new cli/tests/test_render_adr_cr_skills.py [G2 N6]
- cli/scripts/skill_markers.py and cli/tests/test_skill_markers_pi.py (added per Architect ruling 2026-10-01: command-fence detection)

## Verification

```bash
# V-SYNC; V-GOLD; grep guard; V-PY.
# V-SYNC: the sync command documented in CLAUDE.md's Build section (currently: cd cli && python scripts/sync_init_scaffolds.py)
# V-GOLD: git diff --exit-code "$(git merge-base HEAD main)" -- cli/src/ai_team/init/scaffolds/claude cli/src/ai_team/init/scaffolds/codex
# V-PY: cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .   # set UV_CACHE_DIR under /tmp if uv cannot write its cache
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-10-01
Converted the new-adr and change-request skills to markers, following the T-101 pattern.
- **Tests first.** I wrote `cli/tests/test_render_adr_cr_skills.py` and watched 13 tests fail. It covers the five ACs:
  - no unmarked CLI reference in the bodies;
  - noun-marker headers that render the original description for claude and codex;
  - exact claude/codex text for each converted site;
  - pi renders: the supersedes site as `` `supersedes "<supersedes>"` ``, the adr new and change-request new mention forms, and the call forms;
  - no lowercase `ai-team` in the pi SKILL.md files.
- **Source edits.** In new-adr I used command markers for the intro and the Base command, a flag marker for `--supersedes`, and noun markers for "CLI command" and "CLI response values". In change-request I used command markers for the intro and the Run line, plus noun markers for "produced by the CLI", "return the CLI response values", and "from the CLI response". Both headers use the `{{ai-team-cli|the ai-team CLI|the ai_team tool}}` description marker.
- **Tried and rejected.** I first put a noun marker on the `<CLI command result or reason not run>` line in change-request's Output Format fence. The sync fails on a fence that mixes markers with other lines, so I reverted it. The line stays literal, and the AC-1 test strips fenced blocks before checking.
- **Rest of the session.** I ran the sync and committed the regenerated pi resources (`7aaa880`). The full Python suite, ruff, the pi typecheck and pi tests all pass, and the claude/codex scaffold diff against the merge-base is empty.
- **Remaining.** Nothing for this task. If the unmarked fence line is judged an AC-1 gap, fixing it needs either a sync change that allows non-marker fences to carry noun markers, or an ADR or spec decision. It is outside this task's files.

### Session 2 — 2026-10-01
Resolved the Reviewer's AC-1 escalation by applying the Architect's ruling of 2026-10-01: noun and flag markers are allowed in fences that contain no command marker. A fence is a command fence if and only if it contains a `{{ai-team ` command marker. `{{ai-team-cli|` and `{{ai-team-flag ` do not match that test.
- **Sync change.** In `cli/scripts/skill_markers.py`, `render_fence` now returns the fence unchanged when its body has no `{{ai-team ` command marker. The inline pass then renders any noun or flag markers inside it. Command fences behave as before: only command-marker lines are allowed, they are rendered as prose, and anything else fails.
- **Tests.** I added two tests in `test_skill_markers_pi.py`: a `text` fence with a noun marker keeps its fence and renders "ai_team tool", and a flag marker in a non-command fence renders. Both failed before the change. The existing mixed-fence failure tests (command plus noun marker, markers plus shell lines) still pass.
- **Source.** The change-request Evidence line is now `- <{{ai-team-cli|CLI|ai_team tool}} command result or reason not run>`, using pi text without backticks.
- **AC-1 test.** I removed the fence stripping from the AC-1 test and added a check that the pi `SKILL.md` files for new-adr and change-request contain no `\bCLI\b` token. The frontmatter descriptions are already governed by the header noun marker, so they pass.
- **Verification.** Sync succeeded and the regenerated pi resources are committed (46ed07d). V-GOLD is empty, so claude and codex bytes are unchanged. The Python suite (1002 passed), ruff, the pi typecheck and the pi tests all pass.
- **Remaining.** Nothing. Later Phase 2 conversions can use the same non-command-fence rule.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-10-01
ESCALATE

Stage 1 (acceptance criteria), reviewed on the triple-dot diff of `task/T-102-convert-new-adr-and-change-request-to-markers` (7aaa880) against `feat/pi-extension`:
- AC-2 (V-GOLD): met. `git diff --exit-code $(git merge-base HEAD main) -- scaffolds/claude scaffolds/codex` is empty, and the sync re-run produces no diff (pi/resources is consistent).
- AC-3: met. The pi render is `supersedes "<supersedes>"` inside the existing backticks, with no nested span.
- AC-4: met. The shortened `adr new --json` and `change-request new --json` intros render in mention form.
- AC-5: met. No lowercase `ai-team` in either pi SKILL.md.
- AC-1 ("every reference uses a marker"): NOT met as written. `change-request/body.md` line 76, `- <CLI command result or reason not run>` inside the Output Format `text` fence, is a bare CLI mention. It renders unchanged into `pi/resources/skills/change-request/SKILL.md` line 81, so pi output still says "CLI".

Why this is ESCALATE and not FAIL: S-005's marker contract (Skill marker contract section) has no exemption for fenced non-command content. It requires a noun marker for "every bare mention of the CLI", and it also says the sync fails when a fence mixes markers with other lines. Both rules apply to this line, so no source edit inside the task's file list satisfies both. Rewording the line would change the claude/codex bytes and break AC-2. The Developer's choice to leave the line literal and strip fences in the AC-1 test is a reasonable stopgap, but it quietly narrows AC-1 and the spec's "Prose mentions" rule without authority. The task's and spec's wording is the issue, not the implementation. The same fence pattern (Output Format blocks with CLI placeholders) will likely recur in later Phase 2 conversions, so the decision should be made once.

Verification run in a temporary worktree (since removed): sync re-run gave no diff; `uv run pytest` gave 998 passed; `ruff format --check` and `ruff check` were clean; pi `npm run typecheck` and `npm test` passed (12 tests). Stage 2 was not scored, because Stage 1 is unresolved. Apart from the point above, the code and tests looked sound.

```text
Problem: AC-1 ("every reference uses a marker") cannot be satisfied for the `<CLI command result or reason not run>` line in change-request's Output Format text fence. The spec requires a noun marker for every bare CLI mention, but forbids markers mixed with other text in a fence, and the fence is not exempted from the former.
Attempted: Developer put a noun marker on the line, and the sync rejected it as a mixed fence. They reverted it, left the line literal, and made the AC-1 test skip fenced blocks. Rewording the source would change the claude/codex output and break V-GOLD.
Failed because: The two spec rules conflict for non-command text inside fences. Resolving this needs a spec or sync decision, which is outside this task's files (the sync's fence handling lives in cli/scripts/skill_markers.py).
Question: Should S-005's marker contract (a) explicitly exempt non-command fenced text (so AC-1 and the AC-1 test exclude fences, and the literal "CLI" in this pi output is accepted), or (b) allow noun markers inside non-command fences and have the sync support it? Either way, please state the ruling so T-102 and the later conversions apply it consistently.
```

### Review Verdict — 2026-10-01 (review cycle 2)
PASS

Reviewed the triple-dot diff of `task/T-102-convert-new-adr-and-change-request-to-markers` (7aaa880 plus 46ed07d) against `feat/pi-extension`, after the Architect ruling of 2026-10-01.

Stage 1 (acceptance criteria):
- AC-1: met. The test no longer strips fences. Neither pi `SKILL.md` for new-adr or change-request matches `\bCLI\b`. The Evidence line in change-request is now `<{{ai-team-cli|CLI|ai_team tool}} command result or reason not run>`, and it renders as "ai_team tool" in pi.
- AC-2: met. The V-GOLD diff against the merge-base with main is empty. The sync re-run produced no diff, so pi/resources is consistent.
- AC-3, AC-4, AC-5: met, and covered by `test_render_adr_cr_skills.py`.
- Ruling conformance: `render_fence` returns a fence unchanged when it has no `{{ai-team ` command marker, so the inline pass renders its noun and flag markers. Command fences are untouched: the existing mixed command/noun and marker/shell-line failure tests still pass. Two new tests cover noun and flag markers in non-command fences.
- Scope: files touched are the amended Files to Touch only (skill_markers.py, test_skill_markers_pi.py, the new-adr and change-request sources, the new test file, the generated pi output).

Stage 2 (code quality): the change is minimal and readable, with a comment that explains the rule. The tests are independent and cover both success and failure paths. No security or performance concerns.

Verification, run in a temporary worktree (removed afterwards): the sync gave no diff; `uv run pytest` gave 1002 passed; `ruff format --check` and `ruff check` were clean; pi `npm run typecheck` and `npm test` passed (12 tests).

Non-blocking: later Phase 2 conversions can reuse the non-command-fence rule as is.
