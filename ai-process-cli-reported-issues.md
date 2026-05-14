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

### I-005 — CLI test suite has a failing test: bundled task template source missing

- **Severity:** medium
- **Status:** confirmed
- **Observed during:** `/bug-loop`, B-001 implementation/verification, 2026-05-14.
- **Where:** `cli/tests/test_templates.py::test_load_template_task_matches_bundled_source`.

**Observed:** Running the CLI test suite (`uv run pytest` in `cli/`) produces one
failing test: `test_load_template_task_matches_bundled_source`. It fails because the
bundled source it compares against, `.claude/skills/new-task/assets/TEMPLATE-task.md`,
does not exist in the repo.

**Impact:** The CLI test suite is not green on `dev-agent` — 210 pass, 1 fail. This
is not a regression (confirmed pre-existing via a `git stash` round-trip while
working B-001), but it means `integrate`'s regression check starts from a non-clean
baseline and any future genuine regression in `test_templates.py` is harder to spot.

**Expected:** Either the bundled task template source file should exist at the path
the test expects, or the test should point at the correct source location. The CLI
test suite should be green.

**Notes:**
- Discovered while fixing B-001; out of scope for B-001, logged here for triage.
- Not yet filed as a bug — needs triage to decide CLI-side vs. skill-asset-side fix.
