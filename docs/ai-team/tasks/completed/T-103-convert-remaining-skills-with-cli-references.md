---
id: T-103
title: Convert remaining skills with CLI references
status: completed
priority: high
assigned-role: developer
created: '2026-09-30'
spec: S-005
---

# Convert remaining skills with CLI references

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

Part of **S-005** (`docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md`), Implementation Order **Phase 2**. Binding ADRs: ADR-001 to ADR-004 in `docs/ai-team/decisions/`. Planned as P26 in the Gate-2-approved plan (plan IDs are mapped to task IDs below).

- as T-101 for status-report, dev-loop and bug-loop; orchestrators converted even though not shipped. Out of scope: manifest.

## Acceptance Criteria

AC-1: no ai-team token outside a marker in any skill source.
AC-2: V-GOLD (SC-2).
AC-3: no lowercase ai-team under pi/resources/skills (SC-10).
AC-4: every bare mention of the CLI, including inside non-command fences, uses a noun marker (pi output has no `\bCLI\b` token). Added per Architect escalation ruling 2026-10-01 (T-102).

## Dependencies

- `T-097` — Move raw-body/raw-header test assertions to rendered output
- `T-099` — Pi target in the sync; generate pi/resources/

## Files to Touch

- sources/skills/{status-report,dev-loop,bug-loop}/{body.md,metadata.toml} and generated pi output (grep confirms exactly these three) [G2 N6]

## Verification

```bash
# V-SYNC; V-GOLD; grep -rn ai-team pi/resources/skills (none); V-PY.
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
Converted the three remaining skills with CLI references, following the T-101/T-102 patterns.
- **Command markers.** The status-report fences (`ai-team status`, `ai-team report`) became sole `{{ai-team ...}}` lines, which pi renders as "Call the `ai_team` tool with ...". The inline `ai-team status` and `ai-team list tasks --state pending` mentions in dev-loop, bug-loop and status-report now use command markers.
- **Noun markers.** The bare "CLI" nouns use `{{ai-team-cli|CLI|tool}}`. dev-loop line 12 uses `{{ai-team-cli|`ai-team` CLI|`ai_team` tool}}`. No fence mixes markers with other content.
- **Tests.** New `cli/tests/test_render_loop_report_skills.py` covers:
  - AC-1 and AC-4 on the source (no stray `ai-team` or `\bCLI\b`, command fences hold only marker lines);
  - claude/codex exact reproduction of each converted site;
  - pi render and the generated pi `SKILL.md` having no `ai-team` and no `CLI` token.
- **Tried and rejected.** I considered rewording status-report line 7 to avoid the awkward pi text ("the `ai_team` tool call `{"command": "status"}` and ... are available"), but that would change claude/codex output and break V-GOLD.
- **Remaining.** Nothing for this task. Pi resources are regenerated and committed. B-018 was not depended on.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-10-01
PASS

Reviewed the triple-dot diff of `task/T-103-convert-remaining-skills-with-cli-references` (12711ec) against `feat/pi-extension`.

**Stage 1 (acceptance criteria)**
- AC-1: met. After stripping `{{...}}` markers, the full bodies and metadata.toml of status-report, dev-loop and bug-loop contain no `ai-team`, `ai_team` or bare `\bCLI\b` token.
- AC-2 (V-GOLD): met. `git diff --exit-code $(git merge-base HEAD main) -- scaffolds/claude scaffolds/codex` is clean.
- AC-3: met. No `ai-team` under `pi/resources/skills`.
- AC-4: met. Every bare CLI mention, including the inline mentions and the former bash fences, uses a command or noun marker. The pi output for the three skills has no `\bCLI\b` token.
- Scope: only the three skill sources, their pi output, and one new test file changed. No unexpected files.

**Stage 2 (quality)**
- The sync re-run produces no diff, so pi/resources is consistent with the sources.
- `uv run pytest`: 1022 passed. `ruff format --check` and `ruff check` are clean. `npm run typecheck` is clean and `npm test` passes (12 tests).
- The new `cli/tests/test_render_loop_report_skills.py` covers the source-level checks, claude/codex reproduction and pi render. The tests are independent.

**Non-blocking observations**
- The pi status-report line 7 reads "the `ai_team` tool call `{"command": "status"}` and the `ai_team` tool call `{"command": "report"}` are available". It is awkward but accurate, and the instructions stay correct. Rewording would break V-GOLD, so deferring is right.
- The pi "Run the tool status command ... Call the `ai_team` tool with ..." wording is slightly redundant but correct.
- `skill-calls/dev-loop.json` lists `list tasks` / `pending` twice, once per call site. This is consistent with the other skills' behavior.

Next owner: Development Loop.
