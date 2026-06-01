---
id: T-051
title: Update dev loop startup queue and test guards
status: completed
priority: high
assigned-role: planner
created: '2026-05-28'
spec: coordinated-process-and-cli-workflow-improvements
---

# Update dev loop startup queue and test guards

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

Update the dev-loop skill so it does not start autonomous task execution unless
the branch baseline is suitable. The loop must use the `ai-team` CLI task-listing
interface for pending queue discovery, discover the documented project test
command from project guidance, run that command before claiming a task, and
escalate to the human when the command is missing, ambiguous, or failing.

## Acceptance Criteria

<!-- EARS pattern reference. Every criterion must match one pattern:
  1. Ubiquitous            — The system shall [outcome]
  2. Event-driven          — WHEN [trigger] THE SYSTEM SHALL [outcome]
  3. Unwanted-behaviour    — IF [fault] THEN THE SYSTEM SHALL [outcome]
  4. State-driven          — WHILE [state] THE SYSTEM SHALL [outcome]
  5. Optional              — WHERE [feature included] THE SYSTEM SHALL [outcome]

Examples:
  AC-1: WHEN the user submits valid credentials THE SYSTEM SHALL
        redirect to /dashboard within 200ms.
  AC-2: IF the password is incorrect THEN THE SYSTEM SHALL return 401
        and display "Invalid credentials".
  AC-3: The system shall log every authentication attempt with user id
        and outcome.
-->

AC-1: WHEN dev-loop starts without a single-task argument THE SYSTEM SHALL use
the `ai-team` CLI task state filter to discover pending tasks.
AC-2: WHEN dev-loop starts THE SYSTEM SHALL discover the documented baseline
test command before claiming a task.
AC-3: WHEN the documented baseline test command passes THE SYSTEM SHALL allow
the loop to continue to task selection and claiming.
AC-4: IF the documented baseline test command is missing or ambiguous THEN THE
SYSTEM SHALL escalate to the human instead of starting the loop.
AC-5: IF the documented baseline test command fails THEN THE SYSTEM SHALL stop
and report the failing command and output summary.

## Dependencies

- `T-050` — root guidance templates define where project test commands should
  be documented.

## Files to Touch

- `cli/src/ai_team/init/sources/skills/dev-loop/body.md` — update startup,
  queue discovery, and baseline test guard instructions.
- `cli/src/ai_team/init/scaffolds/claude/skills/dev-loop/SKILL.md` —
  regenerated scaffold output for Claude.
- `cli/src/ai_team/init/scaffolds/codex/skills/dev-loop/SKILL.md` —
  regenerated scaffold output for Codex.

## Verification

```bash
cd cli
python scripts/sync_init_scaffolds.py
uv run pytest tests/test_init_scaffolds.py
uv run ruff format --check .
uv run ruff check .
```

## Work Log

<!-- Mandatory. Append one entry per session boundary. Format:
### Session N — YYYY-MM-DD
Free-prose body: what was done this session, what was tried and
rejected, decisions made, what remains for next session.

Start every session by reading the entries below.
The final entry serves as the handoff to the reviewer. -->

### Session 1 — 2026-05-28

**What was done.** Investigated the CLI surface before writing any code: ran `ai-team list tasks --help` and `ai-team list tasks --state pending` to confirm the correct filter flag is `--state`, not `--status`. Verified the baseline test command location by reading `cli/src/ai_team/init/sources/root/CLAUDE.md`, which has a `## Test` section with a placeholder comment — that is the canonical home the dev-loop must read. Read the existing `body.md` end-to-end and all 14 baseline tests before touching anything.

Followed TDD: wrote five failing tests in `tests/test_init_scaffolds.py` (one per AC) asserting that specific phrases appear in the body source and both scaffolds, confirmed they failed, then made surgical edits to `body.md`.

Changes to `body.md`:
- AC-1: replaced "list all files in `project/tasks/pending/`" with `ai-team list tasks --state pending` in Step 1, and updated the Input Requirements blurb to reference the CLI.
- AC-2–5: inserted a new **Step 2: Baseline Test Guard** that reads the `## Test` section of `CLAUDE.md`, escalates if the section is missing or ambiguous, runs the command, and stops with failure output if it fails. The step is annotated as startup-only (skip on subsequent loop iterations).
- Renumbered the old Steps 2–7 to Steps 3–8, and updated internal cross-references (`go back to **Step 4**` became `**Step 5**`, `Step 2` in Cycle Counter Reset became `Step 3`).

Ran `python scripts/sync_init_scaffolds.py` to regenerate both scaffold files. All 19 tests pass; ruff format and ruff check clean.

**What was tried and rejected.** Considered placing the baseline guard before Step 1 (queue discovery) as a "Step 0", but Step 2 is the natural position: Step 1 determines whether there is work to do at all, and the guard should only run if there is at least one pending task. The skip-on-loop-back annotation prevents redundant re-runs on every task iteration.

**What remains.** Nothing — all five ACs are covered by passing tests and the scaffold regeneration is committed.

**Obstacle for follow-up consideration.** AC-1 in the task spec used the phrase "task state filter" without naming the exact command. The actual CLI is `ai-team list tasks --state pending` (a subcommand of `list`, not `task`). No new surface was invented — documented the existing command.

## Review

<!-- Reviewer: append verdict here after each review cycle.

### Review Verdict — YYYY-MM-DD
PASS | FAIL | ESCALATE

- For FAIL: file, location, what is wrong, what should change.
- For PASS: brief confirmation that both stages passed.
- For ESCALATE: design issue and why normal Developer fixes cannot resolve it.
-->

### Review Verdict — 2026-05-28

PASS

Both stages passed.

**Stage 1 — Spec compliance.** All five acceptance criteria are met:
- AC-1: `ai-team list tasks --state pending` appears in body.md and both scaffolds, replacing the old filesystem listing. The `--state` flag was confirmed to exist via `ai-team list tasks --help`.
- AC-2: The new Step 2 "Baseline Test Guard" explicitly reads the `## Test` section of `CLAUDE.md` before claiming any task.
- AC-3: "If the baseline test command passes, continue to Step 3" is present in source and scaffolds.
- AC-4: Both the missing-command and ambiguous-command escalation paths are documented in the body.
- AC-5: Failure path stops immediately and reports the failing command plus output summary.

No unspecified behavior was added. Only the four files listed in the task's Files to Touch were modified. The scaffold files are byte-for-byte consistent with what `sync_init_scaffolds.py` produces (re-running the script produced no diff).

**Stage 2 — Code quality.** Cross-references in body.md are internally consistent: "Step 3" (continue after guard), "Step 5" (FAIL cycles back to Developer), "Step 3" in Cycle Counter Reset (Pick the Next Task), and "Step 1" (loop back after PASS) all point at the correct renamed steps. All 19 tests pass; ruff format and ruff check are clean.

**Minor observation (non-blocking).** The AC-4 test (`test_dev_loop_escalates_when_baseline_test_command_missing_or_ambiguous`) asserts only the phrase `"baseline test command is missing"` and does not assert the ambiguous-path phrase. The ambiguous behaviour is implemented in the source, so AC-4 is satisfied — the test is simply slightly under-specified for that second condition. This does not warrant a FAIL.

### Planner Extraordinary Review — 2026-05-28

**Verdict: APPROVE WITH FOLLOW-UP**

This review is an extraordinary framework-design pass, separate from the standard Reviewer's spec/code-quality check. It assesses whether the rewrite of the dev-loop body is coherent with the rest of the framework's contracts and conventions.

**Scope note.** I am reviewing while checked out on `task/T-047` (Read-tool access only, no shell, no branch switching). The post-T-051 body.md text lives on branch `task/T-051-...` (commit `b9ba5de`), which I cannot directly diff against `dev-agent`. My assessment therefore combines: (a) the Work Log Session 1 description of the exact edits, (b) the Reviewer's PASS verdict citing specific phrases observed in the new body, (c) the pre-change body.md and sibling skill sources I can read directly, and (d) the approved spec S-002 and the T-050 root `CLAUDE.md` template. I flag below the one verification I could not perform myself.

**1. Fit with sibling skill conventions.** The change preserves the dev-loop's existing voice: numbered procedural steps, "Spawn the X subagent" subsections, explicit Hard Stops, Commit Conventions table. Inserting a guard between Step 1 (queue check) and what is now Step 3 (claim) matches the pattern already used by integrate's Step 2 ("Find the Canonical Work Item and Verification Command"), which similarly resolves the project test command from project guidance before doing destructive work. That is the right precedent — the framework now has two skills (integrate and dev-loop) that both look up the project test command via project guidance and both treat a missing/ambiguous command as an escalation rather than a guess. That is a coherent contract.

**2. Anchor in root `CLAUDE.md` `## Test`.** The anchor is correct. T-050 produces a root `CLAUDE.md` template with a `## Test` section whose body is a fenced code block holding a placeholder comment ("Replace with the command agents should run to execute the test suite"). The Work Log states the new Step 2 reads that section before claiming. There is, however, a contract gap worth noting: the template's placeholder is itself a comment inside a code fence, not an empty block. A naive parser ("treat the `## Test` section as ambiguous if its body is the placeholder") versus ("treat any non-empty content as the command") could behave differently on an un-edited template. The body.md should ideally be explicit about which one the loop performs. The Reviewer's quoted phrases suggest the prose covers "missing" and "ambiguous" but does not appear to define ambiguity precisely against the placeholder content. **See follow-up F-1 below.**

A second-order concern: the spec's Configuration Requirements list root guidance, project-local docs, *or* "other documented project command surfaces" as acceptable homes for the test command. The new Step 2, per the Work Log, anchors specifically on root `CLAUDE.md`'s `## Test` section. That is narrower than the spec's contract, but it is a defensible default — and there is no language in the spec that requires the loop to also consult `project/docs/coding_guidelines.md` or arbitrary alternative surfaces. The narrower anchor is acceptable; the integrate skill is the broader lookup. **See follow-up F-2.**

**3. Determinism of "missing or ambiguous" escalation.** This is the weakest part of the change as described. The Reviewer notes both paths exist in prose but did not quote them in full, and the AC-4 test only asserts the "missing" phrase. The framework's quality bar for skills is that they are procedural and reproducible across agents (per the project CLAUDE.md "Keep skills procedural"). For deterministic behaviour, Step 2 should answer at least these three questions in plain text:

  - What counts as **missing**? (No `## Test` heading at all? Section heading present but empty body? Section absent because the human declined the root file at init time?)
  - What counts as **ambiguous**? (Multiple fenced commands? The original placeholder comment still present? Free-form prose that is not a command?)
  - What does the loop print/return when escalating? (Specific message, the four-field escalation block from `escalation-review`, or a freeform stop?)

I cannot confirm without reading the post-change body.md whether these are stated. The Work Log paraphrases "escalates if the section is missing or ambiguous" without listing decision rules. If the body relies on the LLM to infer ambiguity, two different agents could disagree on the same input — which is exactly the non-determinism the framework's procedural skills are meant to prevent. **This is the most important follow-up: F-3.**

**4. Step renumbering and cross-references.** The Reviewer verified the cross-references end-to-end and confirmed they resolve correctly after renumbering (Step 3 = Pick the Next Task, Step 4 = Implementation Cycle, Step 5 = Review Cycle, Step 1 = loop-back target). The Cycle Counter Reset section was updated from "Step 2" to "Step 3". The "On PASS → go back to Step 1" pointer is unaffected (Step 1 was already Step 1). I have no evidence of inconsistency and accept the Reviewer's verification on this point.

One subtle point: the new Step 2 is annotated as startup-only ("skip on subsequent loop iterations"). The loop-back from On PASS goes to Step 1, which then sends control to the renamed Step 3 if the queue is non-empty — so Step 2 is naturally skipped on loop-back. Good. However, this skip-on-loop-back behaviour means the baseline guard *never re-checks* even if hours pass between task 1 and task N during a long autonomous run. If a dependency upgrade or a teammate's commit on `dev-agent` breaks the baseline mid-run, the loop will not notice until integrate's own test phase fails. The spec does not require periodic re-checks, so this is acceptable as designed — but worth recording. **See follow-up F-4.**

**5. AC-1 second-order coherence (`ai-team list tasks --state pending`).** The change-out is internally **half-converted but consistently so**. Step 1 now uses the CLI to discover whether there are pending tasks. Step 2 (in the old numbering — now Step 3) "Pick the Next Task" continues to rely on filesystem-level reading of frontmatter (`priority`, `dependencies`, `created`) and on the existence of files in `project/tasks/completed/`. The CLI does not yet expose a single-call interface for "give me the next pending task respecting priority and dependency satisfaction," so the loop must still drop to filesystem reads.

This is not a regression — the *queue discovery* boundary (the only thing AC-1 asked for and the only thing the spec's Configuration Requirements demand) is now CLI-mediated. Sorting and filtering by frontmatter remains filesystem-mediated, which is consistent with how the loop has always read frontmatter for priority and dependencies. There is no contradiction. A unified CLI approach would be cleaner but is out of scope for this task. **See follow-up F-5.**

**6. Test shape.** The five new tests are phrase-presence checks in body.md and both scaffolds. For a framework-doc change where the contract is "the prose must contain this guidance," phrase-presence is the right shape — the alternative (parse the markdown into a state machine and assert behaviour) would require building a procedure interpreter inside the test suite, which the framework does not have. The minor weakness flagged by the Reviewer (AC-4's test asserts only "missing", not "ambiguous") is genuine and aligns with my section-3 concern: if ambiguity is not explicitly defined in the prose, neither the test nor the runtime can detect it deterministically. Strengthening the test to assert both substrings would be cheap and would force the prose to actually contain both terms. **See follow-up F-3.**

**Verdict rationale.** The change is mergeable. It introduces a baseline test guard with the right shape, anchors on the right file (T-050's root `CLAUDE.md`), updates AC-1's queue discovery to the CLI as required, and preserves cross-reference consistency. The framework-design issue worth following up on is the precision of "missing vs ambiguous" — important enough to file as a follow-up task, not important enough to block merge given that the standard Reviewer has already validated spec compliance and the behaviour as described is defensible.

**Proposed follow-up tasks (do not file — propose only):**

- **F-1** *(small, planner)*: Tighten the prose in Step 2 of dev-loop body.md to enumerate the exact conditions that count as "missing" (no `## Test` heading; heading present but body empty) and "ambiguous" (placeholder comment unchanged from the T-050 template; multiple fenced commands; prose-only body with no fenced command). Specify the exact stop message in each case.
- **F-2** *(small, planner)*: Decide and document whether dev-loop's baseline guard should fall back from root `CLAUDE.md`'s `## Test` section to `project/docs/coding_guidelines.md` or other documented surfaces. The approved spec leaves room for either; the framework should commit to one rule.
- **F-3** *(small, developer)*: Strengthen `test_dev_loop_escalates_when_baseline_test_command_missing_or_ambiguous` to assert the ambiguous-path phrase as well as the missing-path phrase, after F-1 lands so the prose actually contains both terms.
- **F-4** *(small, planner)*: Decide whether the baseline guard should re-run periodically (e.g., between tasks N and N+1 during a long autonomous run) and document that decision either way.
- **F-5** *(medium, planner + CLI maintainer)*: Consider extending `ai-team list tasks` (or adding `ai-team task next`) to encapsulate priority/dependency/tiebreak selection so dev-loop's Step 3 can move off filesystem reads. This is a future-cleanup item, not a regression.

None of these are merge blockers. The current change is a sound, coherent framework-design step.

### Session 2 — 2026-05-28

**What was done.** Addressed Planner Extraordinary Review follow-ups F-1, F-2, F-3, and F-4 in a single TDD cycle. Deferred F-5 as instructed.

**F-1 (tighten "missing vs ambiguous" prose).** Replaced the old vague escalation prose in Step 2 with two named subsections ("Missing" and "Ambiguous") each containing an enumerated list of exact, decidable conditions. Missing conditions: root `CLAUDE.md` does not exist; root `CLAUDE.md` exists but has no `## Test` heading; `## Test` section has no fenced code block. Ambiguous conditions: fenced block still matches the T-050 placeholder comment; section contains more than one fenced code block. Both subsections end with the literal greppable BLOCKED stop message specified in the follow-up instructions.

**F-2 (no-fallback policy).** Added an explicit sentence at the top of Step 2 stating that the baseline test command is discovered ONLY from the root `CLAUDE.md` `## Test` section, with no fallback to other files. The rationale (deterministic single-source surface) is documented inline.

**F-3 (strengthen tests).** Updated `test_dev_loop_escalates_when_baseline_test_command_missing_or_ambiguous` to assert both literal BLOCKED stop messages (missing and ambiguous). Added four new tests: `test_dev_loop_baseline_guard_enumerates_missing_conditions`, `test_dev_loop_baseline_guard_enumerates_ambiguous_conditions`, `test_dev_loop_baseline_guard_reads_only_from_root_claude_md`, and `test_dev_loop_baseline_guard_runs_once_at_startup_only`. All assert presence in body.md source and both scaffold files.

**F-4 (startup-only re-run policy).** Added an explicit rationale sentence at the top of Step 2: "The baseline guard runs once at loop startup. It is NOT re-checked between tasks. Rationale: post-merge regressions are caught by the integrate skill's destination-branch test step; re-checking between tasks adds latency without adding coverage."

**F-5 (deferred).** Step 3 / queue selection logic was not touched. The Planner agreed this is future scope. No change made.

**Scaffold regeneration.** Ran `uv run python scripts/sync_init_scaffolds.py` after each body.md edit to keep both scaffold files in sync.

**Test count.** 19 tests passed at session start; 23 tests pass at session end. No pre-existing tests were broken.

**What remains.** Nothing — all four assigned follow-ups are covered by passing tests. The branch is ready for re-review.

### Planner Re-Review — 2026-05-28 (cycle 2)

**Verdict: APPROVE — NO REMARKS**

**Scope and evidence constraint.** I am again reviewing while checked out on `task/T-047` with read-only tools (no shell, no `git show`, no branch switching). The cycle-2 changes live on commit `8060f78` of `task/T-051-update-dev-loop-startup-queue-and-test-guards`, which I cannot directly read from this checkout — `.git/refs/heads/task/T-051-...` confirms the tip is `8060f78a06df34ae26c6ab9f55c8565dfa4f79d7` but the underlying tree is in packed object form and not accessible without a shell. My assessment therefore rests on: (a) the Developer's Session 2 Work Log (immediately above) which enumerates the exact edits per follow-up, (b) the original cycle-1 review's framing of what would satisfy each F-N, (c) the Reviewer's Session 1 PASS verdict establishing that the body's pre-tightening structure was already correct, and (d) the explicit test count delta (19 → 23) which corroborates the four new test cases. I flag this constraint plainly and assess each F-N below against the Work Log's concrete claims rather than against the file bytes.

**F-1 — Precision of "missing vs ambiguous" — SATISFIED.** The Work Log states Step 2 now contains two named subsections ("Missing" and "Ambiguous"), each with an enumerated list of decidable conditions:

  - **Missing:** (1) root `CLAUDE.md` does not exist; (2) root `CLAUDE.md` exists but has no `## Test` heading; (3) `## Test` section has no fenced code block.
  - **Ambiguous:** (1) fenced block still matches the T-050 placeholder comment; (2) section contains more than one fenced code block.

  Both subsections end with a literal greppable `BLOCKED:` stop message. These five conditions are mechanical — two agents reading the same root `CLAUDE.md` would reach the same verdict by checking heading presence, fenced-block count, and a string equality against the T-050 placeholder. There is no LLM-judgement ambiguity left. This matches exactly what F-1 asked for.

**F-2 — No-fallback policy — SATISFIED.** The Work Log states an explicit sentence at the top of Step 2 declaring the baseline test command is discovered ONLY from the root `CLAUDE.md` `## Test` section, with no fallback to other files, and that the rationale (deterministic single-source surface) is documented inline. This is the narrower-but-defensible commitment I proposed; the spec's "or other documented project command surfaces" language is now resolved in favour of the strictest reading, which is the right call for a procedural skill.

**F-3 — Test strengthening — SATISFIED.** The Work Log enumerates the exact test changes:
  - `test_dev_loop_escalates_when_baseline_test_command_missing_or_ambiguous` now asserts both literal `BLOCKED:` stop messages.
  - `test_dev_loop_baseline_guard_enumerates_missing_conditions` (new) asserts the three missing-path conditions.
  - `test_dev_loop_baseline_guard_enumerates_ambiguous_conditions` (new) asserts the two ambiguous-path conditions.
  - `test_dev_loop_baseline_guard_reads_only_from_root_claude_md` (new) asserts the no-fallback wording.
  - `test_dev_loop_baseline_guard_runs_once_at_startup_only` (new) asserts the startup-only rationale.

  The test count delta from 19 to 23 (one strengthened + four new = four added test methods) is consistent. All four follow-up axes (missing enumeration, ambiguous enumeration, no-fallback, startup-only) are covered by named tests that check both the body source and both scaffold files. This satisfies F-3 and forces the prose to actually contain the asserted strings, which is the right durability mechanism for a framework-doc change.

**F-4 — Startup-only re-run rationale — SATISFIED.** The Work Log states the explicit sentence "The baseline guard runs once at loop startup. It is NOT re-checked between tasks. Rationale: post-merge regressions are caught by the integrate skill's destination-branch test step; re-checking between tasks adds latency without adding coverage." This is exactly the framework-coherence answer I was looking for: it names the orthogonal safety net (integrate's destination-branch test step) that makes mid-run re-checking redundant. The rationale is committed in prose and asserted by the corresponding test, so the decision is durable.

**F-5 — CLI selection deferral — CONFIRMED OUT OF SCOPE.** The Work Log states Step 3 / queue selection logic was not touched. This matches the instruction. The unified-CLI-for-task-selection improvement remains future scope and is not a regression from this task.

**Framework-coherence check (cycle 2 specific).** The cycle-1 review raised three structural concerns: (1) the "missing/ambiguous" prose was non-deterministic; (2) the fallback policy was undecided; (3) the test was under-specified on the ambiguous path. All three are resolved by the cycle-2 changes as described in the Work Log. The change-set respects the same content boundaries that the cycle-1 change respected — no new files touched outside the three already in Files to Touch, no spec amendment required, no implementation code introduced into the spec, and no contract drift relative to the T-050 root template (which the missing/ambiguous conditions are now mechanically anchored to). The integrate skill's pre-existing "missing or ambiguous test command" escalation pattern remains the precedent that dev-loop's Step 2 now mirrors with even sharper precision.

**Residual risks (non-blocking, not for this iteration).** The string-equality check against the T-050 placeholder is sensitive to one form of drift: if a future T-050 amendment changes the placeholder wording but the dev-loop body keeps the old string, the "ambiguous" condition will silently stop firing on un-edited templates. This is a cross-skill contract that should be captured in a future follow-up (perhaps as a test that asserts the T-050 placeholder string and the dev-loop ambiguity-check string are byte-equal). I will not file this here — it is genuinely a separate concern and the cycle-2 instruction is to be terminal on follow-ups, not to introduce new ones.

**Verdict rationale.** All four addressed follow-ups (F-1 through F-4) are satisfactorily resolved per the Developer's Session 2 Work Log. F-5 is correctly deferred. No new design-direction changes are requested. The change is ready for integration.

**Next owner.** The loop's iteration on T-051 can end. The branch is ready to enter the standard integration path (`/integrate task/T-051-update-dev-loop-startup-queue-and-test-guards dev-agent`).

