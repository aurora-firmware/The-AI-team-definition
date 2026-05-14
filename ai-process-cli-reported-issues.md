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
- **Status:** not-a-cli-bug (process/agent behavior)
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
- **Status:** confirmed
- **Tracked by:** B-001
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
- **Status:** confirmed
- **Tracked by:** B-001
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
