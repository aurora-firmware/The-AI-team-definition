---
id: B-001
title: ai-team spec new CLI does not match new-spec skill contract and leaves 
  body title placeholder
severity: medium
status: in-progress
---

# ai-team spec new CLI does not match new-spec skill contract and leaves body title placeholder

## Summary

The `ai-team` CLI (under development) has two defects in `spec new`. First, the
CLI interface does not match what the `new-spec` skill documents: the skill
calls `--title` and `--description` flags, but the CLI takes the title as a
positional argument and has no `--description` option at all — so following the
skill verbatim fails outright, and the required `description` input has nowhere
to go. Second, `spec new` populates the frontmatter `title` but leaves the
literal `# [Specification Title]` placeholder in the document body, so every new
spec needs a manual fix. The same flag mismatch also affects `ai-team bug new`,
which likewise takes a positional title and has no `--description` option
despite the `new-bug` skill documenting both flags.

## Reproduction Status

Status: confirmed

Both issues were observed directly while creating spec `S-001` on
`2026-05-14`. The `bug new` flag mismatch was confirmed via `--help` while
creating bug `B-001`.

## Evidence

- Logs / stack traces / failing assertions:
  - `ai-team spec new --json --title "..." --description "..."` →
    `Error: No such option: --title`
  - `ai-team spec new --help` shows `Usage: ai-team spec new [OPTIONS] TITLE`
    with options limited to `--author`, `--status`, `--json`, `--help` — no
    `--title`, no `--description`.
  - `ai-team bug new --help` shows `Usage: ai-team bug new [OPTIONS] TITLE`
    with options limited to `--severity`, `--task`, `--json`, `--help` — no
    `--title`, no `--description`.
- Screenshots or recordings: n/a
- Failing command or test:
  `ai-team spec new --json --title "X" --description "Y" --author planner --status draft`
- First diagnostic step if not yet reproduced: n/a (reproduced)

## Reproduction Steps

1. Run `ai-team spec new --json --title "Some Title" --description "Some description"`
   as documented by the `new-spec` skill.
2. Observe the command fails with `No such option: --title`.
3. Run `ai-team spec new --json "Some Title"` (positional title, the actual
   supported form). The command succeeds and returns `{"id": ..., "path": ...}`.
4. Open the created spec file and observe the body heading is still the literal
   `# [Specification Title]`, even though the frontmatter `title` is populated.

## Expected Behavior

- The `spec new` and `bug new` CLI interfaces should match their respective
  skill contracts (`new-spec`, `new-bug`) — either by accepting `--title` and
  `--description`, or by the skills being corrected to the positional form and
  to not require a description the CLI cannot consume. The CLI and skills must
  agree.
- `spec new` should substitute the body `# [Specification Title]` heading with
  the provided title, consistent with how it fills the frontmatter.

## Actual Behavior

- `ai-team spec new --title ...` fails with `No such option: --title`.
  `--description` does not exist; there is no CLI path to pass a description.
  The same flag mismatch applies to `ai-team bug new`.
- A spec created via the supported positional form has its frontmatter `title`
  populated but its body H1 left as `# [Specification Title]`.

## Environment

- OS / platform: Linux (6.12.86, Debian 13)
- Language / runtime version: ai-team CLI (version unknown; under development)
- Relevant dependencies: ai-team CLI, `.claude/skills/new-spec`,
  `.claude/skills/new-bug`
- Branch / commit: `pi-agent-design`

## Related

- Task: n/a
- Specification: `the-intern-agent-service-architecture.md` (`S-001`, the spec
  whose creation surfaced these issues)
- See also: `ai-process-cli-reported-issues.md` in the repo root.

## Suspected Area

`ai-team` CLI `spec new` / `bug new` command definitions, and their template
population step. The companion `.claude/skills/new-spec` and
`.claude/skills/new-bug` skill definitions are also part of the mismatch and
may be the side that needs correcting.

## Fix Verification

```bash
# 1. CLI interface matches the skill contract (or skills are corrected to match).
ai-team spec new --help
ai-team bug new --help

# 2. A newly created spec has no leftover body placeholder.
ai-team spec new --json "Verification Spec"
grep -L "# \[Specification Title\]" project/specs/verification-spec.md
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

### Diagnosis 1 — 2026-05-14

**Reproduction status:** Both defects confirmed.

**Evidence captured:**

Defect 1 — Interface mismatch:
`ai-team spec new --json --title "Test Spec" --description "A description"` →
exit 2, `No such option: --title`. `ai-team spec new --help` shows
`Usage: ai-team spec new [OPTIONS] TITLE`, options `--author`, `--status`,
`--json`, `--help` — no `--title`, no `--description`. `ai-team bug new --help`
shows `Usage: ai-team bug new [OPTIONS] TITLE`, options `--severity`, `--task`,
`--json`, `--help` — no `--title`, no `--description`.

Git history: at commit `cdaef70` both `new-spec` and `new-bug` skills documented
`--title` and `--description` as CLI flags. At commit `34cb0a5` the skill
procedure steps were updated to the positional title form, but the `## Input
Requirements` sections were not — they still list `description` as a required
input.

Defect 2 — Placeholder not substituted:
`ai-team spec new --json "Diagnosis Throwaway Spec"` succeeded; the created file
had `title:` populated in frontmatter but the body heading remained the literal
`# [Specification Title]`. Throwaway spec deleted after confirmation.

**Isolated fault:**

- *Defect 1a (`--title`)* — already resolved at current HEAD. The skill
  procedure steps in both `new-spec/SKILL.md` and `new-bug/SKILL.md` already use
  the positional title form. No `--title` mismatch remains in the procedures.
- *Defect 1b (`--description`)* — still unresolved. `new-spec/SKILL.md` line 16
  and `new-bug/SKILL.md` line 16 still list `description` as a required input,
  but neither CLI command accepts a `--description` flag
  (`cli/src/ai_team/commands/spec.py` lines 50–54; `cli/src/ai_team/commands/bug.py`
  lines 110–114). The contract cannot be fulfilled as written.
- *Defect 2* — `cli/src/ai_team/commands/spec.py` lines 62–76: `_template_parts()`
  returns the template body containing `# [Specification Title]`
  (`cli/src/ai_team/templates/spec.md` line 9); `new_spec()` passes that `body`
  straight to `write_artifact()` (line 76) without substituting the `title`
  parameter into the body heading.

**Root cause or fault hypothesis:**

- *Defect 1b:* the `description` required-input is a remnant of the pre-CLI
  design (commit `cdaef70`). When the CLI was implemented, `description` was
  intentionally handled as an agent post-processing step (skill step 4: open the
  file and fill body sections) rather than a CLI flag, but the skills'
  `## Input Requirements` sections were never updated. **Recommended resolution:
  fix the skill side, not the CLI.** Rationale: (a) spec/bug `description` is
  free-form prose used to populate rich, section-specific body content that a
  single CLI string cannot meaningfully carry; (b) the skill procedures already
  handle it correctly via the body-fill step; (c) the CLI is under development
  and adding `--description` would be unplanned new scope. Fix: in both skills,
  demote `description` from a CLI-implying required input to an input the agent
  uses when filling the body after file creation.
- *Defect 2:* the body-placeholder substitution step is simply missing from
  `new_spec()`. Fix: replace `# [Specification Title]` with `# <title>` in the
  `body` before calling `write_artifact()`.

**Planned verification:**

- Defect 1: after editing the skills, `new-spec` / `new-bug` `## Input
  Requirements` no longer present `description` as a CLI-passable required input;
  the positional-title procedures remain intact.
- Defect 2: add a regression test asserting that `spec new` with title
  `"My Test Spec"` produces a body starting with `# My Test Spec` and containing
  no `# [Specification Title]`. Then:
  `ai-team spec new --json "Verification Spec"` and
  `grep -L "# \[Specification Title\]" project/specs/verification-spec.md`
  (the filename should be listed, i.e. placeholder absent).

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that diagnosis, fix, verification, and code quality passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->
