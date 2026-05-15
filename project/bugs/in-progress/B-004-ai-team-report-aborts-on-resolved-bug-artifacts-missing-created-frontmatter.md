---
id: B-004
title: ai-team report aborts on resolved bug artifacts missing 'created' frontmatter
severity: medium
status: in-progress
created: '2026-05-15'
---

# ai-team report aborts on resolved bug artifacts missing 'created' frontmatter

## Summary

`ai-team report` fails before writing any output when a resolved bug artifact does
not have a `created` field in its frontmatter. Because `parse_bug()` treats
`created` as required, a single legacy resolved artifact prevents every report
generation. Gate 5 full reporting is blocked even when the project is otherwise
clean. Originally reported as I-008 in `ai-process-cli-reported-issues.md`.

## Reproduction Status

Status: confirmed

Both the installed CLI and the repo-local CLI fail identically on the current
`dev-agent` state when at least one resolved bug under `project/bugs/resolved/`
lacks `created`. Observed 2026-05-15 during `/status-report`.

## Evidence

- Logs / stack traces / failing assertions:
  ```text
  FrontmatterError: Required frontmatter field 'created' is missing or null in
  project/bugs/resolved/B-001-ai-team-spec-new-cli-does-not-match-new-spec-skill-contract-and-leaves-body-title-placeholder.md
  ```
- Screenshots or recordings: n/a.
- Failing command or test: `uv --directory cli run ai-team report` (or the
  installed `ai-team report`) on a checkout where the named resolved bug exists.
- First diagnostic step if not yet reproduced: confirm the resolved artifact's
  frontmatter has only `id`, `title`, `severity`, and `status` (no `created`),
  then re-run `ai-team report`.

## Reproduction Steps

1. Check out a copy of the repo on `dev-agent`.
2. Confirm `project/bugs/resolved/B-001-...md` (or any resolved bug missing
   `created`) is present.
3. Run `uv --directory cli run ai-team report`.
4. Observe the command aborts with `FrontmatterError: Required frontmatter field
   'created' is missing or null in project/bugs/resolved/B-001-...md` before
   writing any output.

## Expected Behavior

`ai-team report` should be robust across pre-existing lifecycle artifacts. Any of
the following is acceptable:

- Validate all artifacts up front and emit a single actionable error that lists
  every malformed file, rather than aborting on the first one.
- Migrate / backfill legacy bug frontmatter so the required field is populated
  consistently.
- Render resolved bug rows with an unknown/missing `created` value when the field
  is not needed by the report table.

## Actual Behavior

The command halts on the first resolved bug without a `created` field, raising a
`FrontmatterError`, and never produces a report. The status-report skill had to
fall back to writing a manual report file at
`project/docs/reports/progress-report-2026-05-15.md` on 2026-05-15.

## Environment

- OS / platform: Linux (Debian 13).
- Language / runtime version: Python 3.14 (as configured in `cli/pyproject.toml`).
- Relevant dependencies: ai-team CLI as built from this repository; installed CLI
  shows the same failure.
- Branch / commit: observed on `dev-agent` after T-041 integration.

## Related

- Task: not applicable
- Specification: not applicable
- Prior bug: B-001 (the resolved artifact whose frontmatter shape triggers the
  failure).
- Prior issue note: I-008 in `ai-process-cli-reported-issues.md`.
- Affected workflow: Gate 5 (`/status-report`) — blocked from generating a full
  progress report through the CLI.

## Suspected Area

`cli/src/ai_team/commands/report.py` — bug listing path that calls `parse_bug()`
(in the frontmatter/parsing layer) on every artifact under `project/bugs/resolved/`.
`parse_bug()` requires `created`. The hardening should likely live either in
`report.py` (treat `created` as optional for resolved-bug rows) or in the bug
parser / migration helper used at report time.

## Fix Verification

```bash
# 1. Repro on current `dev-agent` (B-001 lacks `created`):
cd /home/daneel/projects/The-AI-team-definition
uv --directory cli run ai-team report
# expected before fix: FrontmatterError on B-001-...md and no report file written.

# 2. After fix:
uv --directory cli run ai-team report
# expected: command exits 0 and writes
#           project/docs/reports/progress-report-<date>.md, with B-001 listed in
#           the resolved-bugs section (created date shown as unknown / migrated /
#           backfilled, per the fix approach).

# 3. Regression test in cli/tests/ covering a resolved bug artifact whose
#    frontmatter has only id, title, severity, status (no `created`), asserting
#    `ai-team report` completes successfully.
uv --directory cli run pytest tests/test_report.py
```

## Diagnosis Log

<!-- Mandatory before implementation. Append one entry before changing production code. Format:
### Diagnosis N — YYYY-MM-DD
Reproduction status:
Evidence captured:
Isolated fault:
Root cause or fault hypothesis:
Planned verification:
-->

### Diagnosis 1 — 2026-05-15

**Reproduction status:** Confirmed — fully reproducible. Running `uv --directory cli run ai-team report` from the repo root exits with code 1 every time, before writing any output file.

**Evidence captured:** stack trace shows `FrontmatterError: Required frontmatter field 'created' is missing or null in project/bugs/resolved/B-001-...md`. Call chain: `report.py:257 default → _render_report → _bug_rows → parse_bug(path)` (called on B-001) → `models.py:209 _require(data, "created", path)` → `_require` raises. The B-001 resolved artifact has frontmatter `id`, `title`, `severity`, `status` only; `created` is absent (it predates the field's introduction).

**Isolated fault:** `cli/src/ai_team/core/models.py`, inside `parse_bug` (lines 204–212): `created=str(_require(data, "created", path))`. `_require` treats absence of `created` as a fatal error for every bug artifact regardless of context. The `Bug` dataclass declares `created: str` (non-optional, no default), so there is no downstream way to represent a missing date gracefully. The consumer in `report.py` `_bug_rows` (lines 116–129) never reads `bug.created` — only `bug.id`, `bug.title`, and `bug.severity`. `created` is read exclusively by `dump_frontmatter` and by mutation callers (bug lifecycle commands), neither invoked by `report`.

**Root cause or fault hypothesis:** `created` was added as a hard-required field on the `Bug` dataclass after B-001 was already resolved and written. `parse_bug` enforces the requirement unconditionally with no tolerance for legacy artifacts. Because `_bug_rows` iterates over all bug folders including `resolved/`, a single legacy artifact causes `parse_bug` to abort before any report output is written. This is a design mismatch: strictness belongs to write paths (creating or mutating a bug file), not read paths that need a subset of fields for display. Recommended fix is option 3 from the bug file (make `Bug.created` optional). Option 2 (backfilling B-001) fixes the immediate data but leaves the code fragile against future legacy artifacts; option 1 (validate-all up front) still prevents reports from generating when legacy artifacts exist.

**Planned verification:**
1. Add a failing regression test in `cli/tests/test_report.py`: create a resolved bug fixture whose frontmatter has only `id`, `title`, `severity`, `status` (no `created`), invoke `ai-team report`, assert exit 0 and the output file is written.
2. Add a unit test in `cli/tests/test_models.py`: `parse_bug` on a file missing `created` returns a `Bug` with `created=None` instead of raising.
3. Apply the minimal fix: change `Bug.created` to `str | None = None` and read it with `data.get("created")` instead of `_require`.
4. Run the full test suite; all tests must pass.
5. Re-run `uv --directory cli run ai-team report` against the real repo (with B-001 present); command must exit 0 and write the dated report file with B-001 listed in the resolved-bugs section.

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-15

Read the bug file and Diagnosis Log (embedded in the task prompt), then confirmed the fault in `cli/src/ai_team/core/models.py`: `parse_bug` called `_require(data, "created", path)` unconditionally, and `Bug.created` was declared `str` (non-optional). Any resolved artifact written before `created` became a required field caused a `FrontmatterError` that aborted `ai-team report` before it could write any output.

Followed the TDD cycle as directed. Red phase: added `test_parse_bug_accepts_missing_created` to `cli/tests/test_models.py` (fixture with only `id`, `title`, `severity`, `status`; asserts `bug.created is None` and no `FrontmatterError`) and `test_report_succeeds_with_legacy_bug_missing_created` to `cli/tests/test_report.py` (sets up a resolved bug without `created`, invokes `ai-team report --out`, asserts exit code 0 and B-001 in output). Both tests failed against the unfixed code with the exact `FrontmatterError` described in the bug.

Green phase: changed `Bug.created` field type from `str` to `str | None = None` in the dataclass, and replaced `created=str(_require(data, "created", path))` with `raw_created = data.get("created")` followed by `created=str(raw_created) if raw_created is not None else None`. Both new tests passed. No changes made to `parse_task`, `parse_spec`, or `parse_adr` — all out of scope and still enforce `created` as required as specified in the diagnosis.

Full suite: 231 tests pass. Fix Verification: `uv --directory cli run ai-team report` exits 0, writes `project/docs/reports/progress-report-2026-05-15.md`, and B-001 appears in the resolved-bugs section. The generated report file was not committed on the bug branch — it is a runtime output artifact.

Nothing remains for this bug. Ready for review.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-05-15

PASS

Both stages passed.

**Stage 1 — Bug criteria**

- Diagnosis Log (Diagnosis 1) records reproduction status (confirmed, fully reproducible), evidence (stack trace with exact call chain and `FrontmatterError` message), isolated fault (`models.py parse_bug` calling `_require` on `created` unconditionally; `Bug.created` declared non-optional), and root cause (field added after B-001 was resolved; strictness misapplied to read paths that do not need `created`). All required elements are present.
- The fix is scoped to the isolated cause: `Bug.created` changed from `str` to `str | None = None`; `parse_bug` replaced `_require(data, "created", path)` with `data.get("created")` + conditional `str()` conversion. No unrelated behavior was added.
- `parse_spec`, `parse_adr`, and `parse_task` retain `_require` for `created` — correctly out of scope.
- `dump_frontmatter` already omits `None`-valued optional fields, so the changed field type does not introduce a write-path regression.
- `_bug_rows` in `report.py` does not read `bug.created` — confirmed in source, consistent with the diagnosis.
- Fix Verification steps were executed: `uv --directory cli run ai-team report` exits 0 and writes the dated report file with B-001 listed; recorded in Session 1.
- The fix branch diff contains exactly `cli/src/ai_team/core/models.py`, `cli/tests/test_models.py`, and `cli/tests/test_report.py`. `project/docs/reports/progress-report-2026-05-15.md` is not modified on the branch.

**Stage 2 — Code quality**

- Correctness: the conditional `str(raw_created) if raw_created is not None else None` correctly handles both the absent-field case (returns `None`) and the present-field case (coerces to `str`, matching prior behavior).
- Tests: `test_parse_bug_accepts_missing_created` (unit, `test_models.py`) and `test_report_succeeds_with_legacy_bug_missing_created` (integration, `test_report.py`) both cover the failure path (pre-fix) and the success path (post-fix). Tests are independent (use `tmp_path`/`monkeypatch`). Full suite: 231 tests pass per Session 1.
- Security: no credentials, no unvalidated input beyond what existed before.
- Readability: inline comment on the dataclass field explains the optionality; function logic is straightforward. No dead code or debug artifacts.
- Performance: no new loops or blocking paths.
