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
- **Status:** not-a-cli-bug (process/agent behavior)
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
- **Status:** not-a-cli-bug (process/agent behavior)
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

_No confirmed `ai-team` CLI defects observed yet during this dev-loop run. The T-027–T-031
tasks were documentation-focused and exercised the CLI only indirectly (`gen_docs.sh`
wrapping `typer ... utils docs`). New entries go here as they are found._
