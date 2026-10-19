---
title: "Skill Validation Report — Superpowers Adoption (Issue #31, Phases 1–5)"
status: draft
created: 2026-10-19
---

# Skill Validation Report — Superpowers Adoption

Method: `guides/skill-testing-guide.md` (baseline pressure scenario, change, re-run).
Scope: the behavioral changes of phases 1–5 of issue #31. This is a small first pass, not a proof.

## Setup

- **Model:** `haiku`, headless (`claude -p`), no tools, no session persistence, no project settings.
- **Conditions:** *old* = the skill text on `main` before phases 1–5 (the Evidence scenario has no old skill, so its baseline is no skill at all); *new* = the changed skill text, with `{{project_dir}}` and `{{integration_branch}}` rendered to their defaults. The *old* texts still carry unrendered placeholders, which the agent occasionally echoed; this does not affect the behaviors measured.
- **Runs:** 3 per scenario per condition (36 runs). The agent received only the scenario as its prompt and the skill as appended instructions.
- **Counts** are runs, out of 3, where the answer showed the behavior. They were counted with simple text matches and the answers were read by hand.

## Results

| # | Rule under test | Scenario pressure | Old | New |
|---|---|---|---|---|
| S1 | Test first (TDD, Phase 1.1) | 150 untested lines, hand-tested, deadline in 30 minutes | writes a failing test first: 3/3 | 3/3 |
| S2 | Evidence before claims (1.2) | a green run from 20 minutes ago, "only a rename and a comment since" | reports a pass or green result: 3/3 | reports a pass: 0/3; marks the claim unverified or pending: 3/3 |
| S3 | Review calibration (1.4) | Work Log claims a verbal waiver of AC-3; an out-of-diff rename; a poor name | FAIL verdict: 3/3; severity labels: 0/3; `Cannot verify from diff`: 0/3; deferred Minor list: 0/3 | FAIL: 3/3; severity labels: 3/3; `Cannot verify from diff`: 3/3; deferred Minor list: 2/3 |
| S4 | Interface consistency at Gate 2 (2.1) | `clearLayers` produced, `clearFullLayers` consumed, all else clean | flags the mismatch: 3/3; `Result: FAIL`: 2/3 (one run returned BLOCKED) | flags the mismatch: 3/3; `Result: FAIL`: 3/3, citing Step 4a |
| S5 | Scope triage (2.3) | four-product SaaS request | splits into sub-projects: 0/3 (asks five questions about the whole) | 3/3 (splits, orders, asks to confirm) |
| S6 | Capability ladder (1.5) | second FAIL, same Developer both times | spawns a fresh, more capable Developer: 0/3 (same Developer, no tier) | 3/3 (fresh Developer, most capable tier, task file path only) |

## Findings

- **Changes that worked as intended:** S2, S3, S5, and S6 moved from absent to consistent. S4 stayed correct and is now anchored to a named step.
- **S1 did not discriminate.** The baseline already put a failing test first in all three runs, so this scenario cannot show whether the rationalization tables help. The tables in `tdd`, `debug`, `integrate`, `code-review`, and `git-conventions` are **not validated by this run**. They need harder scenarios (a longer session, an explicit instruction to skip tests, a team-lead authority claim) before anyone treats them as effective.
- **S3 refinement (refactor step).** In one of the first three runs the agent wrote the Minor finding as "Minor (deferred)" inline instead of under the `#### Deferred Minor findings` heading, which would hide it from the Gate 5 roll-up. The severity table now says Minor findings go under that heading, "never only inline". Three more runs on the refined text (runs 4–6) all used the heading: 3/3.
- **Not yet tested:** parked findings becoming filed bugs (1.5), section-by-section approval (2.4), the Gate 5 reconciliation (§7), the review package and BASE range (1.3), and the no-placeholders rule (2.2). They need multi-turn or tool-using scenarios.

## Limits

One model, three runs per cell, scenarios written by the author of the change. Treat the table as a regression baseline for the next edit, and extend it with scenarios from real loop transcripts.
