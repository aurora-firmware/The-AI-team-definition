# ai-team CLI — Reported Issues

Running log of bugs, rough edges, and friction observed while using the `ai-team` CLI
(and the skills/loops that invoke it). The CLI is under active development; entries here
are observations to triage, not confirmed defects unless marked so.

## How to read this

- **Severity** — `high` (blocks work / wrong results), `medium` (workaround exists),
  `low` (cosmetic / ergonomic).
- **Status** — `open`, `confirmed`, `fixed`, `wontfix`, `not-a-cli-bug`.

---

## Issues

### I-001 — Reviewer verdict commit included implementation files (not a CLI bug)

- **Severity:** medium
- **Status:** fixed (via B-002, 2026-05-14)
- **Tracked by:** B-002
- **Observed during:** `/dev-loop`, T-027 integration.
- **What happened:** The Reviewer subagent, when committing its verdict to the canonical
  task file on `dev-agent`, ran a broad `git add` and swept in three implementation files
  (`cli/docs/commands.md`, `cli/scripts/gen_docs.sh`, `cli/tests/test_gen_docs.py`) that
  had been checked out for inspection. The lifecycle commit should contain only the task
  file.
- **Impact:** The orchestrator had to rewrite the (non-pushed) verdict commit to contain
  only the task file before integration, because the contaminated state would have made
  the `integrate` "expected changes" check misfire.
- **Not an ai-team CLI defect** — this is `code-review` skill / reviewer-agent behavior.
  Logged here because it affected a dev-loop run. Suggested fix: the `code-review` skill
  should instruct the Reviewer to stage exactly the canonical task file.

### I-002 — Reviewer reviewed file contents instead of the branch diff (not a CLI bug)

- **Severity:** high
- **Status:** fixed (via B-002, 2026-05-14)
- **Tracked by:** B-002
- **Observed during:** `/dev-loop`, T-031 review.
- **What happened:** The Reviewer evaluated the full current contents of `README.md` and
  `CLAUDE.md` rather than `git diff dev-agent...task/T-031-...`. It misattributed
  pre-existing repository content (README "Install the CLI" subsections, earlier CLAUDE.md
  edits) as additions made by the branch, and returned a factually incorrect `FAIL`.
  The real branch diff was 4 in-scope inserted lines.
- **Impact:** Spurious FAIL verdict; the loop could not proceed at the review gate.
- **Not an ai-team CLI defect** — `code-review` skill / reviewer-agent behavior. Suggested
  fix: the `code-review` skill must pin review scope to `git diff <dest>...<branch>` (the
  merge base), not working-tree contents.

### I-006 — Specifications tend to embed implementation code instead of descriptions and measurable criteria (not a CLI bug)

- **Severity:** medium
- **Status:** not-a-cli-bug (process/agent behavior)
- **Observed during:** `/brainstorm` for S-001 (`github-actions-ci-for-cli-tests-and-ruff-formatting-checks`), 2026-05-14.
- **Where:** `.claude/skills/brainstorm`, `.claude/skills/new-spec`, and the spec
  template (`## Configuration` / code-block sections).

**Observed:** When `/brainstorm` produced S-001, the resulting spec included concrete
implementation artifacts — a near-complete `ci.yml` and `pyproject.toml` snippet. The
spec template actively invites this: it ships a `## Configuration` section with a YAML
code block placeholder, so the spec author fills it with real code.

**Why this is a problem:** A specification should describe *what* must be true and how
success is *measured* — observable behaviour, acceptance criteria, constraints,
exclusions — not *how* it is built. Implementation code in a spec (a) pre-empts the
Planner's task decomposition, (b) pre-empts the Developer, who should write the code
against the project's coding guidelines, and (c) rots: the spec and the eventual code
drift apart, and reviewers cannot tell which is authoritative. Code belongs mostly in
**tasks**, as illustrative examples, and the real implementation is the Developer's
output.

**Expected:** The `brainstorm` / `new-spec` skills and the spec template should steer
authors toward prose descriptions plus measurable/observable criteria. Code or config
snippets in a spec should be the rare exception (e.g. a contract that genuinely *is*
the requirement), clearly marked as illustrative — not a drop-in implementation.
Concrete example snippets, where useful, belong in the tasks the `spec-breakdown`
skill produces; the Developer agent writes the actual code per the coding guidelines.

**Notes:**
- Self-observed: S-001 as written carries this smell (the `ci.yml` and `pyproject.toml`
  blocks). It can be left as-is for now or trimmed to "shape" descriptions when the
  spec is revised — logged here so the underlying template/skill nudge gets fixed.
- Not filed as a bug — needs triage to decide which of template vs. skills to change.

---

## ai-team CLI defects

### I-003 — `spec new` / `bug new` interface does not match the `new-spec` / `new-bug` skills

- **Severity:** high
- **Status:** fixed (via B-001, 2026-05-14)
- **Tracked by:** B-001
- **Resolution:** skill side corrected — `new-spec` / `new-bug` `## Input Requirements`
  now separate CLI-passable inputs from agent-consumed inputs; `description` is documented
  as agent-consumed (not a CLI flag) and the procedures explicitly say not to pass it to
  the CLI. The CLI positional-title interface was kept as-is.
- **Observed during:** reported by another agent on branch `pi-agent-design`, 2026-05-14.
- **Where:** `ai-team spec new` vs. `.claude/skills/new-spec/SKILL.md`; `ai-team bug new` vs. `.claude/skills/new-bug/SKILL.md`.

**Observed:** The `new-spec` skill documents the command as:

```
ai-team spec new --json --title "<title>" --description "<description>" [--author ...] [--status ...]
```

The actual CLI signature is:

```
ai-team spec new [OPTIONS] TITLE
Options: --author, --status, --json, --help
```

So:
- `--title` is not a valid option — the title is a positional argument. Following the skill
  verbatim fails with `No such option: --title`.
- `--description` does not exist at all. There is no CLI path to pass a description.

**Impact:** Any caller following the skill's documented procedure fails. The `description`
field — which the skill lists as a *required* input — is silently unused, because the CLI
offers nowhere to put it.

**Also affects `bug new`:** `ai-team bug new` has the same shape — positional `TITLE`,
options limited to `--severity`, `--task`, `--json`, `--help`. The `new-bug` skill likewise
documents `--title` and `--description`, neither of which the CLI accepts.

**Expected:** Either the CLI should accept `--title` and `--description` (matching the skill
contracts), or the `new-spec` / `new-bug` skills should be corrected to use the positional
title and to stop requiring a description the CLI cannot consume. The two must agree.

### I-004 — `spec new` does not substitute the body title placeholder

- **Severity:** medium
- **Status:** fixed (via B-001, 2026-05-14)
- **Tracked by:** B-001
- **Resolution:** `new_spec()` (and `new_bug()`, which had the same `# [Bug Title]`
  defect) now substitute the body H1 placeholder with the provided title before writing
  the artifact; regression tests added in `cli/tests/test_spec_new.py` and
  `cli/tests/test_bug_new.py`.
- **Observed during:** reported by another agent on branch `pi-agent-design`, 2026-05-14.
- **Where:** `ai-team spec new` (template population).

**Observed:** After creating spec `S-001`, the frontmatter `title` was populated correctly,
but the body still contained the literal placeholder heading:

```
# [Specification Title]
```

**Impact:** Every newly created spec has a placeholder H1 that must be fixed by hand. Easy
to miss.

**Expected:** The CLI should substitute the body `# [Specification Title]` heading with the
provided title, consistent with how it fills the frontmatter.

**Notes:**
- `ai-team spec new --json` output format worked as expected: `{"id": "S-001", "path": "..."}`.
- Reproduced on branch `pi-agent-design`, 2026-05-14.

### I-005 — CLI test suite has a stale failing test: task template comparison points at a deleted path

- **Severity:** medium
- **Status:** fixed (2026-05-14) <!-- fixed directly in commit 77af8a8 on dev-agent (no bug filed) -->
- **Observed during:** `/bug-loop`, B-001 implementation/verification, 2026-05-14.
- **Where:** `cli/tests/test_templates.py::test_load_template_task_matches_bundled_source`.

**Observed:** Running the CLI test suite (`uv run pytest` in `cli/`) produces one
failing test: `test_load_template_task_matches_bundled_source`. It fails because the
bundled source it compares against, `.claude/skills/new-task/assets/TEMPLATE-task.md`,
does not exist in the repo.

**Impact:** The CLI test suite is not green on `dev-agent` — 210 pass, 1 fail. This
is not a regression, but it means `integrate`'s regression check starts from a
non-clean baseline and any future genuine regression in `test_templates.py` is
harder to spot.

**Not a regression — confirmed three ways:** (1) the CLI suite was run on `dev-agent`
*before* the B-001 merge and already showed this failure; (2) the B-001 developer
confirmed it via a `git stash` round-trip; (3) `.claude/skills/new-task/assets/TEMPLATE-task.md`
was deleted by commit `6987d7f` ("chore(skills): migrate new-task to ai-team cli"),
which is an ancestor of the bug-loop session baseline `b1ce7e2` — the deletion
predates all bug-loop work.

**Root cause — the test is stale, not the code.** `6987d7f` migrated the task
template into the CLI's bundled templates (`cli/src/ai_team/templates/`) and
intentionally removed the old skill-asset copy at
`.claude/skills/new-task/assets/TEMPLATE-task.md`. The migration updated the code
but left `test_load_template_task_matches_bundled_source` asserting against the
deleted path. The sibling parametrized test
`test_load_template_returns_non_empty_frontmatter_for_each_kind` (task/bug/spec/adr)
passes, so `load_template("task")` itself works — only the stale path comparison fails.

**Fix applied (test side):** the test now repoints at the CLI's bundled template
source `cli/src/ai_team/templates/task.md` instead of the deleted skill-asset path.
No CLI behaviour change was needed. Full CLI suite is now green: 211 passed.

**Notes:**
- Discovered while fixing B-001; out of scope for B-001, logged here for triage.
- Fixed directly (no bug filed) in commit `77af8a8` on `dev-agent`:
  `test(cli): repoint task template comparison at bundled CLI source`.

### I-007 — `task new` does not substitute the body title placeholder

- **Severity:** medium
- **Status:** confirmed
- **Observed during:** `/write-plan` for S-001, creating tasks T-032/T-033/T-034, 2026-05-14.
- **Where:** `ai-team task new` (template population) — `cli/src/ai_team/commands/task.py`.

**Observed:** `ai-team task new "<title>"` populates the frontmatter `title` correctly,
but the document body still contains the literal placeholder heading `# [Task Title]`.
All three tasks created during the S-001 write-plan run had to have their H1 fixed by
hand.

**Impact:** Every newly created task has a placeholder H1 that must be fixed manually —
the same defect class as I-004, easy to miss.

**Root cause (same as I-004/B-001):** B-001 fixed the body-placeholder substitution for
`spec new` (`# [Specification Title]`) and `bug new` (`# [Bug Title]`) in `spec.py` and
`bug.py`, but `task new` in `task.py` was not covered — `new_task()` passes the template
body straight to `write_artifact()` without replacing `# [Task Title]`.

**Expected:** `task new` should substitute the body `# [Task Title]` heading with the
provided title, consistent with `spec new` / `bug new` after the B-001 fix. A regression
test analogous to `test_spec_new_substitutes_body_h1_with_provided_title` should be added
in `cli/tests/test_task_new.py`.

**Notes:**
- Not yet filed as a bug — straightforward one-line fix mirroring the B-001 change; file
  a bug if it should go through the bug-loop.

### I-008 — `report` aborts when older resolved bug artifacts lack `created` frontmatter

- **Severity:** medium
- **Status:** confirmed
- **Observed during:** `/status-report`, 2026-05-15.
- **Where:** `ai-team report` / `cli/src/ai_team/commands/report.py` bug listing.

**Observed:** `ai-team status` successfully produced the inline project summary, but
`ai-team report` failed before writing `project/docs/reports/progress-report-2026-05-15.md`.
Both the installed CLI and the repo-local CLI failed with:

```text
FrontmatterError: Required frontmatter field 'created' is missing or null in
project/bugs/resolved/B-001-ai-team-spec-new-cli-does-not-match-new-spec-skill-contract-and-leaves-body-title-placeholder.md
```

The offending resolved bug artifact has `id`, `title`, `severity`, and `status`
frontmatter, but no `created` field. The report command parses resolved bugs through
`parse_bug()`, which requires `created`, so a historical/resolved artifact with older
frontmatter shape prevents all report generation.

**Impact:** Gate 5 full report generation is blocked even though the project can be
summarized and there are no open bugs. The status-report skill had to fall back to a
manual report file.

**Expected:** `ai-team report` should be robust across existing lifecycle artifacts. Good
options include validating and reporting all malformed artifacts with an actionable error,
backfilling/migrating older bug frontmatter, or allowing resolved bug rows to render with
an unknown/missing created date when that field is not needed by the report table.

**Notes:**
- Manual fallback report was written to
  `project/docs/reports/progress-report-2026-05-15.md`.
- Not yet filed as a bug — likely worth a bug-loop item because it blocks the CLI report
  command on current repository data.
