# Full Skills Review — Claude + Codex Reconciliation

**Date:** 2026-06-04
**Inputs reconciled:** `claude_skills_review.md` (review of the Claude-format export) and
`codex_skills_review.md` (review of the Codex-format export).
**Purpose:** The two reviews independently examined the **two platform exports of the same
process**. This report merges their findings into one issue list, separates genuinely
platform-specific changes from shared-process changes, and — for each issue — points the fix at
the **source of truth** (`cli/` scaffolds or `ai-process/` docs) rather than at the export
copies, so a single fix lands on both platforms.

---

> **⚠️ Post-audit correction (2026-06-04).** This report was built by comparing the two
> hand-copied exports (`claude_skills/`, `codex_skills/`), which are **both stale relative to the
> real source** (`cli/src/ai_team/init/sources/` + rendered `scaffolds/`). A later source audit
> found several reported issues are **already fixed in source**, not open defects:
> **I13** (test discovery is already lenient/consistent in source `dev-loop`, `integrate`, `tdd`,
> and `workflow-overview` — prior bug B-007); **I9** (`change-request` already renders to *both*
> claude+codex scaffolds — prior bug B-006); **P1** (source `codex/planner.toml` already
> references `change-request` and `claude/planner.md` already lists it). Treat the **source**, not
> these export copies, as ground truth. The backlog generated from this report
> (`project/tasks`, `project/bugs`) reflects the corrected, source-verified scope: only **I6** and
> **I8** are genuine defects (bugs B-008, B-010); the rest are genuine improvements still missing
> from source (I2/I7/I12/I15/I1/I5/I4/I10); and the stale-copy symptoms are resolved simply by
> re-rendering the exports from source (task T-067).

## 0. How the two trees relate (read this first)

There is **one process**, rendered to two runtimes:

```
cli/src/ai_team/init/sources/skills/<name>/
        body.md         ← SHARED process text (renders to BOTH exports)
        metadata.toml    ← [claude] header + [codex] header (per-platform frontmatter)
cli/src/ai_team/init/sources/agents/
        claude/<role>.md     ← Claude role files (model: opus|sonnet, tools, skills)
        codex/<role>.toml    ← Codex role files (model = "gpt-5.5", reasoning_effort, sandbox)
cli/src/ai_team/templates/   ← task.md (EARS lives here), spec.md, bug.md, change-request.md, …
        → `python cli/scripts/sync_init_scaffolds.py` renders →
claude_skills/  (SKILL.md per skill, agents/*.md)
codex_skills/   (SKILL.md per skill, agents/*.toml)
```

**Consequence for fixes:** a *process* fix belongs in the shared `body.md` (one edit → both
platforms). A *frontmatter* fix belongs in the per-platform `metadata.toml` headers. A *role*
fix must be applied to **both** `agents/claude/*.md` **and** `agents/codex/*.toml`. A
*contract* change should update the owning `ai-process/` doc first (per `CLAUDE.md`).

> Both reviews edited only their export tree, and neither updated the source. The two exports
> have now **diverged from each other and from source**. The remediation (Section 5) is to
> consolidate both reviews' improvements into source, reconcile the divergences, and re-render.

---

## 1. Changes specific to Claude vs Codex (the platform layer)

Almost all of the *process* findings are platform-agnostic. The genuinely platform-specific
differences are:

| Aspect | Claude Code | Codex | Implication |
|---|---|---|---|
| **Role definition format** | `agents/<role>.md` — markdown body + frontmatter `name/description/tools/model/skills` | `agents/<role>.toml` — `developer_instructions = """…"""`, `model`, `model_reasoning_effort`, `sandbox_mode` | Role-level edits must be authored twice, in two formats. |
| **Model + runtime knobs** | `model: opus` (Architect/Planner), `model: sonnet` (Dev/Reviewer/Integrator) | `model = "gpt-5.5"`, `model_reasoning_effort = "high"`, `sandbox_mode = "workspace-write"` | Keep per platform; do not cross-copy model IDs. |
| **Skill frontmatter policy** | Uses `allowed-tools`, `argument-hint`, `effort`, `disable-model-invocation` meaningfully | Codex `skill-creator` guidance says skills "normally use only `name` and `description`" — yet the current Codex export **still carries** `allowed-tools`/`effort`/`disable-model-invocation` (see codex review "Remaining Considerations") | **Open policy question**: strip extra keys from `[codex]` headers, or keep for parity? Decide and document. |
| **Skill → skill invocation** | `Skill(<name>)` gating in `allowed-tools` (the Claude review wired `Skill(status-report)` this way for G2/I8) | Codex export also carries `allowed-tools` with `Skill(...)`, so the mechanism currently renders the same — but it is a Claude-native concept | If Codex doesn't honour `Skill()` gating, the status-report wiring (I8) needs a Codex-native equivalent. |
| **Authoring style of the dedup** | Claude review used a "FROZEN block + `(canonical: escalation-review)` pointer" convention | Codex review centralized the same rules in `git-conventions`/`escalation-review` without the pointer convention | Stylistic divergence to reconcile when consolidating to source (pick one convention for the shared `body.md`). |

**Everything else below is shared process and should be identical on both platforms.** The
fact that the two exports currently differ on these is the bug, not a platform requirement.

---

## 2. Cross-review coverage matrix

What each review caught, and what remains **open in the other export** (verified against the
current files).

| # | Issue | Claude review | Codex review | Residual gap (verified) |
|---|---|---|---|---|
| I1 | Centralize branch/commit/lifecycle/handoff rules in `git-conventions` | ✅ | ✅ | none — both converged |
| I2 | Bug evidence chain: `debug` diagnosis-only, fix contract, `tdd` consumes it, `code-review` validates | ◑ (boundary clarified) | ✅ (deeper: required fix contract + evidence-chain validation) | Claude tree weaker — adopt Codex's contract depth |
| I3 | Integration trust: require committed `PASS` verdict + committed handoffs before merge; protect lifecycle files | ◑ (relied on existing canonical-on-dev-agent) | ✅ (explicit `PASS`-before-merge check) | Claude `integrate` lacks the explicit committed-`PASS` gate |
| I4 | Planning handoff boundaries (brainstorm/new-spec/spec-breakdown/new-task/spec-breakdown-review) | ◑ (pointers, EARS, atomicity) | ✅ (explicit ownership per phase) | minor — merge both framings |
| I5 | Escalation = single cross-role impasse handler + artifact routing | ✅ | ✅ | none |
| **I6** | **`new-adr` caller contract**: callers pass stale `context`; skill expects `description` | ❌ **MISSED** | ✅ fixed | **🔴 LIVE BUG in `claude_skills`** (spec-breakdown-review:47, escalation-review:67 still pass `context`) |
| I7 | Gate 2 must check **spec coverage** before dependency/file-conflict checks | ❌ | ✅ | open in `claude_skills` |
| **I8** | `status-report` orphaned / not invoked by loops (Gate 5) | ✅ wired via `Skill(status-report)` | ◑ (made CLI-first, **not wired into loops**) | **open in `codex_skills`** (codex loops never call status-report) |
| **I9** | `change-request` skill missing from export | ✅ created + improved + added to planner | ❌ not addressed | **🔴 still MISSING in `codex_skills`** |
| I10 | EARS canonical home ambiguous | ✅ (→ task template) | ◑ (folded into dedup) | tidy both to point at `templates/task.md` |
| I11 | Gate 2 output-format conflict (spec-breakdown-review vs architect role) | ✅ | ❌ | open in `codex_skills` |
| I12 | Two-stage review checklist ownership (→ `code-review` canonical) | ✅ | ◑ | open/unclear in `codex_skills` |
| I13 | **Test-command discovery** unified to one source | ✅ (root `CLAUDE.md ## Test`) | ❌ | open in `codex_skills` **and** conflicts with `ai-process` (see I13 detail) |
| I14 | `new-bug` regression-evidence completeness | ◑ (description only) | ✅ (full evidence fields) | Claude `new-bug` body weaker |
| I15 | Remove routine forced branch deletion (`git branch -D`) | ❌ | ✅ | `claude_skills/integrate` still has the `-D` fallback |
| P1 | **Codex agent role files not reviewed** (`*.toml`; review searched for non-existent `openai.yaml`) | ✅ Claude `.md` updated | ❌ Codex `.toml` untouched | **🔴 Codex roles received none of the role-level edits** |
| P2 | Skill frontmatter policy for Codex (name+description vs full set) | n/a | flagged, unresolved | open decision |

Legend: ✅ done · ◑ partial · ❌ not addressed · 🔴 needs action now.

---

## 3. Consolidated issue list (what / why / where / fix)

Each issue states the **source-of-truth fix** so both exports are corrected together.

### 🔴 I6 — `new-adr` caller/callee contract mismatch (live bug in Claude tree)
- **What:** `new-adr` declares inputs `title`, `description`, `status`, `supersedes`. But its
  callers — `spec-breakdown-review` and `escalation-review` — instruct the agent to pass
  `title` + **`context`** (a field `new-adr` does not consume).
- **Why it matters:** the Architect would hand `new-adr` a payload that doesn't match its
  documented inputs → ADR body filled wrong or `status` omitted. Codex already fixed this
  (its `escalation-review` now passes a rich `description`); Claude did not.
- **Where:** `claude_skills/skills/spec-breakdown-review/SKILL.md:47`,
  `claude_skills/skills/escalation-review/SKILL.md:67`. (Codex export already correct.)
- **Fix (cli/):** in the **shared** `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md`
  and `…/escalation-review/body.md`, change the `new-adr` invocation input list from `context:`
  to `description:` (include the same content: spec path, affected tasks, ADRs, durability
  rationale). Re-render → fixes both exports.

### 🔴 I9 — `change-request` skill missing from Codex export
- **What:** the workflow's "lighter intake path" (`ai-team change-request new`, CR-NNN) has a
  source skill, but it is absent from `codex_skills/` (and was missing from `claude_skills/`
  until the Claude review recreated it).
- **Why:** stale exports. The skill exists at
  `cli/src/ai_team/init/sources/skills/change-request/` and its `metadata.toml` already has a
  `[codex]` header — so a re-render *should* produce it for both.
- **Where:** missing dir `codex_skills/skills/change-request/`.
- **Fix (cli/):** port the Claude review's *improved* body (added Quality Criteria + Common
  Pitfalls) into `…/skills/change-request/body.md`, then re-run
  `sync_init_scaffolds.py`. Add `change-request` to the planner role in **both**
  `agents/claude/planner.md` and `agents/codex/planner.toml`.
- **Fix (ai-process/):** none needed — `workflow-overview.md` already documents the
  change-request path; this is alignment *toward* the contract.

### 🔴 P1 — Codex agent role files (`*.toml`) never reviewed
- **What:** the Codex review concluded "no `agents/openai.yaml` files exist" and edited no
  roles. The Codex roles actually live at `codex_skills/agents/*.toml` (and
  `cli/.../agents/codex/*.toml`). They carry skills lists, escalation blocks, and handoff
  rules — none of which got the role-level edits the Claude `.md` roles received.
- **Why:** the five Codex role files are now stale relative to both the Claude roles and the
  reviewed skills (e.g., planner lacks `change-request`; reviewer still inlines the checklist).
- **Where:** `codex_skills/agents/{architect,developer,integrator,planner,reviewer}.toml`;
  source `cli/src/ai_team/init/sources/agents/codex/*.toml`.
- **Fix (cli/):** apply the same role-level edits made to `agents/claude/*.md` to
  `agents/codex/*.toml` (escalation wording, reviewer → `code-review` checklist pointer (I12),
  planner `change-request` (I9), any Gate-2-format wording (I11)). Mind the format: Codex roles
  use `developer_instructions = """…"""`, not markdown sections.

### I8 — `status-report` not wired into Codex loops
- **What:** Claude wired `Skill(status-report)` into dev-loop/bug-loop Step 8 so the Gate 5
  summary is produced by the canonical skill. Codex made `status-report` CLI-first but never
  wired it into its loops.
- **Where:** `codex_skills/skills/{dev-loop,bug-loop}/SKILL.md` (no status-report reference);
  Codex `dev-loop` `allowed-tools` lacks `Skill(status-report)`.
- **Fix (cli/):** in the shared `dev-loop/body.md` and `bug-loop/body.md`, add the Step-8
  invocation of `status-report`. Add `Skill(status-report)` to **both** platform headers in
  `dev-loop/metadata.toml` and `bug-loop/metadata.toml`. (Platform note: if Codex does not
  honour `Skill()` gating, replace with the Codex-native invocation; the body instruction
  "produce the Gate 5 summary via status-report" is platform-agnostic.)
- **Fix (ai-process/):** `workflow-overview.md` §"Final Merge" already says the loop produces
  the Gate 5 summary — confirm it names `status-report` as the producer.

### 🔴 I13 — Test-command discovery: skills disagree, and disagree with `ai-process`
- **What:** Three rules existed (dev-loop strict: root `CLAUDE.md ## Test` only; integrate:
  multi-source fallback; tdd: unspecified). Claude unified them to the single source; Codex did
  not. **Separately**, `ai-process/processes/workflow-overview.md` itself still describes the
  **loose** rule ("starts with `CLAUDE.md`/`AGENTS.md`, then follows references to
  `project/docs/…`, README, build configuration…").
- **Why:** the implementation (dev-loop) and the owning process doc contradict each other — a
  genuine spec/impl conflict, not just export drift.
- **Where:** `ai-process/processes/workflow-overview.md` (§"What the development loop does",
  ~line 128); `codex_skills/skills/{dev-loop,integrate,tdd}/SKILL.md`.
- **Fix (ai-process/ FIRST):** decide the intended rule. Recommended: adopt the deterministic
  single-source rule (root `CLAUDE.md ## Test`, exactly one fenced block; else BLOCKED) and
  update `workflow-overview.md` to match. Then **fix (cli/):** align `dev-loop`, `integrate`,
  `tdd` `body.md` to that rule (Claude already did this in its export — port that wording to
  source).

### I2 — Bug evidence chain (adopt Codex's depth)
- **What:** make `debug` diagnosis-only with a required **fix contract** in the Diagnosis Log;
  `tdd` implements that contract; `code-review` fails when the diagnosis→fix evidence chain is
  missing instead of reconstructing intent from the diff.
- **Why:** reduces speculative fixes and review churn; both reviews moved here, Codex further.
- **Where:** `debug/body.md`, `tdd/body.md`, `code-review/body.md`.
- **Fix (cli/):** consolidate Codex's fix-contract requirement + Claude's standalone-vs-loop
  usage-context boundary into the shared bodies.
- **Fix (ai-process/):** reflect the "diagnosis-first, fix contract before implementation" rule
  in `workflow-overview.md` §"Bug-Fix Flow" and `quality-gates.md` (Gate 3 bug addendum).

### I3 — Integration requires committed PASS + lifecycle protection
- **What:** `integrate` must verify the latest **committed** canonical `PASS` verdict on
  `dev-agent` before merging, require committed Developer handoffs, and reject lifecycle-file
  edits arriving on implementation branches.
- **Where:** `integrate/body.md`, `dev-loop/body.md`, `bug-loop/body.md`.
- **Fix (cli/):** adopt Codex's explicit committed-`PASS`-before-merge step into the shared
  `integrate/body.md`.
- **Fix (ai-process/):** `quality-gates.md` Gate 4 + `workflow-overview.md` §"Work-item state
  model" should state the committed-evidence precondition.

### I7 — Gate 2 spec-coverage check
- **What:** `spec-breakdown-review` should confirm the task plan covers the spec **before**
  dependency/file-conflict checks. Codex added it; Claude did not.
- **Where:** `spec-breakdown-review/body.md`.
- **Fix (cli/):** add the coverage step. **Fix (ai-process/):** ensure `quality-gates.md`
  Gate 2 lists coverage as a check.

### I15 — Remove routine forced branch deletion
- **What:** Codex removed the `git branch -D` fallback (report safe-delete failure instead);
  Claude `integrate` still force-deletes when `-d` refuses.
- **Where:** `claude_skills/skills/integrate/SKILL.md` (Step 7 `-D` fallback).
- **Fix (cli/):** in `integrate/body.md`, replace the `-D` fallback with a stop-and-report.
- **Fix (ai-process/):** add "no routine forced deletion" to
  `ai-process/guidelines/git-conventions.md` Hard Rules.

### I14 — `new-bug` regression evidence
- **What:** ensure `new-bug` requires evidence, `source_branch`, expected/actual, and
  fix-verification for integration-filed regressions. Codex enriched the skill; Claude only
  sharpened the description (its `integrate` already passes the fields).
- **Where:** `new-bug/body.md`.
- **Fix (cli/):** adopt Codex's evidence fields into the shared body.
- **Fix (ai-process/):** already covered by `workflow-overview.md` §"Bug intake" — align skill
  to it.

### I1 / I4 / I5 / I10 / I11 / I12 — converged or single-side, low-risk
- **I1** (git-rule centralization), **I5** (escalation single-owner): both reviews agree; just
  pick one authoring convention when consolidating to source (see P2/§1 style note).
- **I4** (planning boundaries), **I10** (EARS → `templates/task.md`), **I11** (Gate 2 output
  format), **I12** (review-checklist → `code-review` canonical): Claude (and partly Codex)
  handled these; port the Claude wording to the shared bodies and mirror role pointers into the
  Codex `.toml` roles.

### P2 — Codex skill frontmatter policy (decision needed)
- **What:** decide whether Codex `SKILL.md` should keep `allowed-tools`/`argument-hint`/
  `effort`/`disable-model-invocation` (current state) or reduce to `name`+`description` per
  Codex `skill-creator` guidance.
- **Where:** `[codex]` headers in every `…/skills/*/metadata.toml`.
- **Fix (cli/):** once decided, set the `[codex]` headers accordingly and re-render. Note that
  I8's status-report wiring depends on this (if Codex drops `allowed-tools`, the loop must
  invoke status-report by instruction, not by `Skill()` gating).

---

## 4. Answer: which changes are platform-specific?

- **Platform-specific (must be authored per platform):** role files (`.md` vs `.toml`), model
  IDs/runtime knobs (`opus|sonnet` vs `gpt-5.5`+`reasoning_effort`+`sandbox_mode`), and the
  Codex frontmatter-key policy (P2). The `Skill()` invocation mechanism is Claude-native and
  *may* need a Codex equivalent for I8.
- **NOT platform-specific (shared `body.md`; fix once):** every process issue — I1–I7, I10,
  I13–I15, the bug evidence chain, integration evidence, escalation routing, planning
  boundaries, EARS, Gate-2 checks. The current export divergence on these is drift to be
  removed, not a platform requirement.

---

## 5. Recommended remediation (single source, both platforms)

1. **Update `ai-process/` first** for the contract-level items (per `CLAUDE.md`):
   - `workflow-overview.md`: reconcile test-command discovery (I13), name `status-report` as
     the Gate 5 producer (I8), reflect bug fix-contract (I2) and committed-evidence precondition
     (I3).
   - `quality-gates.md`: Gate 2 coverage (I7), Gate 3 bug evidence addendum (I2), Gate 4
     committed-`PASS` (I3).
   - `guidelines/git-conventions.md`: "no routine forced deletion" (I15).
   - `escalation-procedure.md`: confirm single-owner + artifact routing (I5).
2. **Consolidate into the shared source `body.md`** files under
   `cli/src/ai_team/init/sources/skills/<name>/`, taking the stronger of the two reviews per
   issue (Codex for I2/I3/I6/I7/I14/I15; Claude for I8/I9/I10/I11/I12/I13). Apply I6 now (live
   bug). Pick one authoring convention (§1 style note).
3. **Update both role formats**: `agents/claude/*.md` and `agents/codex/*.toml` (P1) — planner
   `change-request`, reviewer checklist pointer, escalation wording, Gate-2 format.
4. **Decide P2** and set the `[codex]` `metadata.toml` headers.
5. **Re-render and verify:** `python cli/scripts/sync_init_scaffolds.py`;
   `cd cli && uv run pytest && uv run ruff format --check . && uv run ruff check .`
   (Codex review already confirmed 292 tests pass — re-confirm after source edits.)
   If command output/docs changed: `bash cli/scripts/gen_docs.sh`.
6. **Delete the now-stale hand-edited exports' divergence** by re-rendering from source so
   `claude_skills/` and `codex_skills/` are byte-consistent with the scaffolds again.

---

## 6. Notes & provenance

- The Claude review covered 17 skills + 5 `.md` roles and created `change-request` (18 skills).
  The Codex review covered the same 17 skills but **no roles** and did **not** create
  `change-request`.
- Verified directly in-tree for this report: `new-adr` `context` mismatch persists in
  `claude_skills` (I6); `change-request` absent from `codex_skills` (I9); Codex roles are
  `*.toml` and untouched (P1); Codex loops do not reference `status-report` (I8); both exports
  still carry Claude-style skill frontmatter (P2).
- Neither review modified `cli/` or `ai-process/`; both edited export copies only. This report's
  fixes deliberately target source so the two platforms re-converge.
