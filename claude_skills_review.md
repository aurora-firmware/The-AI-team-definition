# claude_skills Process-Optimization Review

**Date:** 2026-06-04
**Scope:** All 17 skills + 5 agent role files in `claude_skills/`, reviewed as a working
system (the executable form of the ai-process workflow), not as isolated documents.
**Method:** One orchestrator did a holistic cross-skill analysis and froze a set of
canonical-ownership decisions, then four parallel agents each ran `skill-creator` over a
disjoint cluster of files and applied the edits. The orchestrator ran a final consistency
sweep. Goal: reduce redundancy, fix inconsistencies, and close process gaps while preserving
the workflow's intent.

> **Important — these are edits to the flattened export.** `claude_skills/` is the rendered
> Claude-format export. The source of truth is `cli/src/ai_team/init/sources/`
> (split `body.md` + `metadata.toml`) and the bundled `cli/src/ai_team/templates/`. To make
> these improvements permanent, the changes must be ported back into the source tree and
> re-rendered with `python cli/scripts/sync_init_scaffolds.py` (and `bash cli/scripts/gen_docs.sh`
> if command docs change). Nothing under `cli/` was modified by this review. See
> "Port-back checklist" at the end.

---

## 1. How the work was partitioned

Four clusters, each owning a disjoint set of files so the agents could run in parallel
without conflict. Cross-cutting concepts were resolved up front (Section 2) so that an agent
fixing one copy of a shared rule could not diverge from another agent fixing a different copy.

| Cluster | Theme | Files |
|---|---|---|
| 1 | Planning & Specs | brainstorm, new-spec, spec-breakdown, new-task, new-adr, spec-breakdown-review, **change-request (new)**, planner, architect |
| 2 | Implementation & Review | tdd, debug, code-review, new-bug, developer, reviewer |
| 3 | Orchestration & Integration | dev-loop, bug-loop, integrate, merge-conflicts, status-report, integrator |
| 4 | Shared contracts | git-conventions, escalation-review |

---

## 2. Canonical-ownership decisions (the redundancy fixes)

The biggest source of drift risk in the skill set was the same rule being restated in many
places. Each concept now has exactly one canonical home; everything else references it.

| Concept | Canonical home | Was duplicated in |
|---|---|---|
| Branch model + commit format + hard git rules | `git-conventions` | dev-loop, bug-loop, integrate, tdd, code-review commit tables |
| Four-field escalation request block | `escalation-review` (`## Escalation Request Block (FROZEN)`) | ~12 skills/agents — kept inline for locality, but field names frozen + `(canonical: escalation-review)` pointer added everywhere |
| Phase 2 Human Escalation Report template | `escalation-review` (`## Phase 2 Human Escalation Report`) | referenced by dev-loop, bug-loop, spec-breakdown-review |
| Atomicity / one-shottable thresholds (≤3–4 files, ≤5 ACs, ~20-line desc) | `new-task` (Task Quality Rules) | spec-breakdown, spec-breakdown-review (numbers removed, now reference) |
| EARS five patterns | the task template (`templates/task.md`) | new-task/spec-breakdown wording reconciled to point at the template |
| Content-boundary rule (no impl code in spec) | `new-spec` | brainstorm + planner trimmed to one-line pointers |
| Two-stage review checklist | **`code-review` skill** (ownership *reversed* — see §3, G4) | reviewer agent now references it |
| Baseline test command source | `dev-loop` (root `CLAUDE.md ## Test`) | tdd + integrate now use the same single fallback source |
| Gate 5 status summary | `status-report` | dev-loop/bug-loop now invoke it instead of hand-rolling (see §3, G2) |

**Why centralize but keep escalation blocks inline:** a skill that *emits* an escalation
should be usable without loading `escalation-review`, so the four-field block stays inline at
each emission point. What was unsafe was the wording silently drifting. The field
names/order are now frozen and shown in a copy-ready fenced block in `escalation-review`, and
every inline copy carries a `(canonical: escalation-review)` pointer — locality without drift.

---

## 3. Process gaps closed (structural changes)

These altered the process contract and were applied per your "fix everything in place" choice.
Each is called out here because it changes behavior, not just wording.

- **G1 — `change-request` skill was missing from the export.** The skill already existed in
  the CLI source (`cli/src/ai_team/init/sources/skills/change-request/`) but had never been
  rendered into `claude_skills/`, leaving the workflow's documented "lighter intake path"
  (`ai-team change-request new`, CR-NNN) with no executable skill. Ported it in, improved it to
  new-spec/new-task quality (added Quality Criteria + Common Pitfalls), sharpened the
  description for triggering, and added it to the **planner** agent's `skills:` list (the
  Planner owns change-request intake per the workflow). *Net new file:
  `skills/change-request/SKILL.md`.*

- **G2 — `status-report` was orphaned.** The workflow says the loop produces the Gate 5
  summary, but dev-loop/bug-loop hand-rolled their own end-of-run summary and never invoked
  `status-report` (which had `disable-model-invocation: true` and was unreachable from the
  loops). Now both loops invoke `Skill(status-report)` at Step 8 (queue drained) and the skill
  was added to their `allowed-tools`. There is now one authoritative Gate 5 summary, not two
  competing ones. `disable-model-invocation` stays (prevents accidental description-triggering);
  explicit `Skill()` invocation from a loop is still allowed.

- **G3 — three different test-command-discovery rules** (dev-loop: root `CLAUDE.md ## Test`
  only; integrate: a four-source fallback chain; tdd: unspecified). Reconciled to a single
  rule: the work item's own `## Verification`/`## Fix Verification` command is authoritative
  for that item; the **fallback is the same root `CLAUDE.md ## Test` baseline** the dev-loop
  uses; otherwise `BLOCKED`. tdd and integrate were aligned to name that single source. The
  intentional precedence (item-specific command first) is preserved; only the divergent
  fallbacks were unified.

- **G4 — two-stage review checklist ownership was inverted.** The `code-review` skill
  deferred to "the Reviewer agent's quality bar," while the full checklist lived in the
  `reviewer` agent — so the skill was not self-contained and could not be reused without the
  agent in context. Reversed: the full Stage 1 / Stage 2 / Bug Fix Addendum / Verdict Mapping
  checklist now lives in the `code-review` skill (`## Two-Stage Review Checklist`); the
  `reviewer` agent keeps a short quality-bar summary and points to the skill.

- **G5 — EARS canonical home was ambiguous** (new-task said "the template," spec-breakdown
  said "the new-task skill," and the five patterns were never defined in any skill body). Fixed
  to a single chain: skills name the five pattern keywords and point to the task template
  (`templates/task.md`), which is where the definitions and examples actually live.

- **G6 — Gate 2 output-format conflict.** `spec-breakdown-review` defined one `Result:` block;
  the `architect` agent defined a different envelope, with no statement of which applies when
  the Architect runs the skill. Reconciled: the architect agent's
  `Result/Summary/Artifacts/Evidence/Obstacles/Next Owner/Next Action` envelope is the role
  wrapper; `spec-breakdown-review` keeps its domain-specific Findings block and now states that
  the agent wrapper applies (no field duplication, no ambiguity).

- **debug ↔ tdd fix overlap.** `debug` is diagnosis-first, but its Steps 6–7
  ("Fix with Minimal Change" / "Verify the Fix") silently duplicated tdd's red→green cycle.
  In the bug-loop the Developer diagnoses with `debug` then fixes with `tdd`. Added a
  `## Usage Context` section and labeled Steps 6–7 as the **standalone-use path only**; inside
  the loop, diagnosis stops at the handoff and `tdd` owns the fix.

---

## 4. Per-cluster change summary

### Cluster 1 — Planning & Specs
- **change-request/SKILL.md** (new): ported + improved (G1).
- **spec-breakdown**: EARS wording → task template (G5); atomicity numbers removed, now
  reference new-task; escalation pointer.
- **spec-breakdown-review**: EARS + atomicity dedup; Gate 2 output-format reconciliation (G6);
  escalation pointer.
- **new-adr**: sharpened description (records a decided decision, not exploration); added
  Quality Criteria + Common Pitfalls (was the only cluster skill lacking them).
- **brainstorm**: content-boundary restatement trimmed to a one-line pointer to new-spec.
- **planner**: content-boundary trimmed to a pointer; escalation forwarding-owner vs
  template-owner split clarified; `change-request` added to skills list (orchestrator).
- **architect**: escalation pointer.

### Cluster 2 — Implementation & Review
- **tdd**: test-command source aligned to the frozen three-level rule (G3); escalation pointer.
- **debug**: `## Usage Context` added; Steps 6–7 marked standalone-only; loop boundary made
  explicit; escalation pointer.
- **code-review**: became the self-contained canonical checklist home (G4) — Input
  Requirements, Step 3, and a new `## Two-Stage Review Checklist` section; escalation pointer.
- **new-bug**: description sharpened to name caller roles and discovery scenarios.
- **developer**: escalation block aligned to frozen four-field form + pointer.
- **reviewer**: full checklist replaced with a short summary + pointer to the code-review
  skill; escalation pointer.

### Cluster 3 — Orchestration & Integration
- **dev-loop / bug-loop**: status-report wired into Step 8 + added to allowed-tools (G2);
  test-command fallback aligned (G3, dev-loop); commit tables trimmed to role-specific rows
  that reference git-conventions (removed restated branch model/hard rules); escalation
  pointers; kept structurally parallel.
- **integrate**: Step 2 fallback rewritten to name the single canonical source (G3);
  escalation pointer.
- **merge-conflicts**: escalation pointer.
- **status-report**: description strengthened to name its canonical Gate 5 role and disclaim
  competing summaries.
- **integrator**: escalation pointer + more specific hint text.

### Cluster 4 — Shared contracts
- **git-conventions**: promoted to explicit canonical source with stable, citable headings
  (`## Branch Model`, `## Commit Message Format`, `## When Each Role Commits`, `## Hard Rules`);
  removed the Quality Criteria section that merely restated the Hard Rules; added an
  absolute-rules framing line; sharpened description.
- **escalation-review**: added a dedicated `## Escalation Request Block (FROZEN)` section
  with verbatim field names in a copy-ready fence; promoted the Escalation Verdict block and
  the Phase 2 Human Escalation Report to top-level sections for stable cross-referencing;
  added a canonical-source notice; sharpened description; added an "amending a pushed commit"
  pitfall.

---

## 5. Consistency verification (post-edit sweep)

All checks passed:
- 18 skills present (17 + new change-request), all with valid `name`/`description` frontmatter.
- All fenced code blocks balanced across every skill and agent file.
- Atomicity thresholds appear **only** in new-task — no numeric leaks elsewhere.
- `git-conventions` exposes the four stable headings that loops/skills now cite by concept.
- `escalation-review` exposes the FROZEN request block, verdict block, and Phase 2 report
  headings that all `(canonical: escalation-review)` pointers resolve to.
- `(canonical: escalation-review)` pointer present in all 11 expected skill/agent files.
- `Skill(status-report)` in both loops' allowed-tools **and** invoked at Step 8.
- tdd, dev-loop, and integrate now all name root `CLAUDE.md ## Test` as the single fallback.
- reviewer agent points to the code-review skill's Two-Stage Review Checklist section.

---

## 6. Open items & follow-ups

1. **Port-back checklist (required to make changes durable):**
   - Re-apply each edit to the matching `cli/src/ai_team/init/sources/skills/<name>/body.md`
     (and `metadata.toml` headers where descriptions/allowed-tools changed).
   - Create `cli/src/ai_team/init/sources/skills/change-request/` already exists — only the
     improved body/Quality-Criteria/Pitfalls need porting; confirm it renders into the export.
   - Mirror agent edits in `cli/src/ai_team/init/sources/agents/claude/` **and**
     `.../agents/codex/` (the codex variants were *not* part of this review — see item 2).
   - Run `python cli/scripts/sync_init_scaffolds.py`, then `uv run pytest` and the ruff checks.
2. **Codex variants not reviewed.** This pass covered the Claude-format export only. The
   `codex_skills/` tree and `sources/agents/codex/` carry parallel copies; the same fixes
   should be applied there for parity (the framework ships both).
3. **EARS definitions live only in the task template.** The skills now point to it correctly,
   but a reader who only has a skill in context cannot see the five pattern examples. If full
   skill self-containment is a goal, consider inlining a compact EARS reference in new-task.
   Left as a pointer per the frozen decision (template is the single source).
4. **code-review Step 3 vs the checklist section** intentionally restate the Stage 2 items
   (procedural context vs reference list). If that feels redundant, Step 3 could be reduced to
   category names + a "see checklist below" pointer — a judgment call left open.
5. **Contract note.** Per `CLAUDE.md`, changes that alter the framework contract should update
   the owning spec/guide first. G1–G6 touch process behavior; before porting to source,
   confirm the owning docs in `ai-process/` and `guides/` agree (e.g., the workflow-overview
   already describes the change-request path and the loop-produced Gate 5 summary, so G1/G2 are
   alignments *toward* the documented contract, not departures from it).
