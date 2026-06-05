# Full Skills Review By Codex

This report merges the findings from `claude_skills_review.md` and `codex_skills_review.md`.
It separates shared ai-process issues from Claude Code vs Codex-specific differences and
recommends durable fixes in `cli/` or `ai-process/`, not in the flattened `claude_skills/`
or `codex_skills/` review copies.

## Executive Summary

Both reviews found the same core problem: the exported skills represent one workflow, but
several process contracts were duplicated across skills and agents. The same branch rules,
handoff rules, escalation shapes, test-command discovery rules, review criteria, and Gate 5
summary rules appeared in multiple places. That creates drift risk and makes it unclear which
skill owns a decision when agents disagree.

Most fixes should be made in:

- `cli/src/ai_team/init/sources/skills/*/body.md`
- `cli/src/ai_team/init/sources/skills/*/metadata.toml`
- `cli/src/ai_team/init/sources/agents/claude/*`
- `cli/src/ai_team/init/sources/agents/codex/*`
- `ai-process/processes/*`
- `ai-process/guidelines/*`
- `guides/agent_template.md`
- `guides/skill_template.md`

After source edits, run:

```bash
cd cli
python scripts/sync_init_scaffolds.py
uv run pytest
uv run ruff format --check .
uv run ruff check .
```

## Claude Code Vs Codex-Specific Differences

### Claude Code-Specific

- Claude exports include Markdown agent files in `claude_skills/agents/*.md`; the Claude review updated both skills and agents.
- Claude Code uses `.claude/agents`, `.claude/skills`, and root `CLAUDE.md` as the natural project guidance surface.
- Claude skill frontmatter commonly includes execution-control fields such as `allowed-tools`, `argument-hint`, `disable-model-invocation`, and role-facing `skills:` lists in agents.
- The Claude review found `change-request` missing from the flattened Claude review copy, although the source tree and generated scaffolds already contain `change-request` for both Claude and Codex.

### Codex-Specific

- Codex agent definitions are TOML files in `codex_skills/agents/*.toml` and `cli/src/ai_team/init/sources/agents/codex/*.toml`; the Codex review focused on skills and did not update Codex agent source files.
- Codex project guidance naturally uses root `AGENTS.md`, although this repository also scaffolds `CLAUDE.md`.
- System `skill-creator` guidance for Codex-triggered skills says only `name` and `description` are used for triggering. The copied Codex skills preserve Claude-style extra frontmatter fields. This may be intentional for this framework export, but the source should explicitly document the Codex schema choice.
- No `agents/openai.yaml` metadata exists under `codex_skills/skills`; that is not a bug if these are framework process skills rather than user-installed OpenAI skill packages, but it should be documented if intentional.

### Shared

The substantive workflow issues are shared across both tools. Branching, handoffs, review,
integration, escalation, planning gates, bug evidence, and status reporting should be fixed in
the shared source skill bodies, then rendered to both Claude and Codex outputs.

## Issues And Recommended Fixes

## 1. Shared Rules Are Duplicated Across Many Skills

Type: shared ai-process issue.

Where it appears:

- `codex_skills_review.md`: "Duplicated Ownership Rules" and "Redundancy Reductions".
- `claude_skills_review.md`: Section 2, "Canonical-ownership decisions".
- Source areas:
  - `cli/src/ai_team/init/sources/skills/git-conventions/body.md`
  - `cli/src/ai_team/init/sources/skills/dev-loop/body.md`
  - `cli/src/ai_team/init/sources/skills/bug-loop/body.md`
  - `cli/src/ai_team/init/sources/skills/integrate/body.md`
  - `cli/src/ai_team/init/sources/skills/tdd/body.md`
  - `cli/src/ai_team/init/sources/skills/code-review/body.md`
  - `ai-process/guidelines/git-conventions.md`

Why it matters:

When branch model, lifecycle ownership, commit rules, destructive-git restrictions, and
handoff evidence are restated in multiple skills, one skill can drift from another. That is
especially risky for integration because a loop may believe a lifecycle update is valid while
`integrate` treats it as unsafe.

Suggested fix:

- Promote `git-conventions` to the canonical source for branch model, commit format,
  lifecycle ownership, shared handoff contract, destructive-git restrictions, and integration
  evidence.
- Trim other skills to short role-specific instructions plus references to `git-conventions`.
- Update `ai-process/guidelines/git-conventions.md` to match the skill's canonical sections.
- Add or update tests in `cli/tests/test_init_scaffolds.py` or a new content validation test to
  assert the rendered Claude and Codex skill copies both contain the canonical headings.

## 2. Escalation Block And Human Escalation Template Can Drift

Type: shared ai-process issue.

Where it appears:

- `claude_skills_review.md`: Section 2, frozen four-field escalation block and Phase 2 report.
- `codex_skills_review.md`: "Escalation Was Not Clearly A Single Process".
- Source areas:
  - `cli/src/ai_team/init/sources/skills/escalation-review/body.md`
  - `cli/src/ai_team/init/sources/skills/dev-loop/body.md`
  - `cli/src/ai_team/init/sources/skills/bug-loop/body.md`
  - `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md`
  - `cli/src/ai_team/init/sources/agents/claude/*`
  - `cli/src/ai_team/init/sources/agents/codex/*`
  - `ai-process/processes/escalation-procedure.md`

Why it matters:

Every skill that can return `ESCALATE` needs to emit the same fields so the Architect can
consume the request without interpretation. If field names or order drift, an active loop may
drop required context or trigger repeated Architect consultations.

Suggested fix:

- Add a stable `## Escalation Request Block` section to `escalation-review`.
- Use exactly `Problem`, `Attempted`, `Failed because`, and `Question` everywhere.
- Add a stable Phase 2 Human Escalation Report section to `escalation-review`.
- Update agent templates and both Claude/Codex agents to reference the canonical escalation
  skill rather than redefining thresholds.
- Update `ai-process/processes/escalation-procedure.md` so the documented workflow matches the
  skill contract.

## 3. Bug Fix Evidence Chain Is Too Weak

Type: shared ai-process issue.

Where it appears:

- `codex_skills_review.md`: "Weak Evidence Chain For Bug Fixes".
- `claude_skills_review.md`: debug to tdd overlap and implementation/review cluster.
- Source areas:
  - `cli/src/ai_team/init/sources/skills/debug/body.md`
  - `cli/src/ai_team/init/sources/skills/tdd/body.md`
  - `cli/src/ai_team/init/sources/skills/code-review/body.md`
  - `cli/src/ai_team/init/sources/skills/bug-loop/body.md`
  - `cli/src/ai_team/init/sources/agents/claude/developer.md`
  - `cli/src/ai_team/init/sources/agents/codex/developer.toml`
  - `ai-process/processes/workflow-overview.md`
  - `ai-process/guidelines/review-checklist.md`

Why it matters:

Without a required diagnosis handoff, bug fixes can become symptom patches. Reviewers then
have to reconstruct intent from the diff, which increases false passes and review churn.

Suggested fix:

- Make looped use of `debug` diagnosis-only.
- Require Diagnosis Log fields: reproduction status, evidence captured, isolated fault, root
  cause or fault hypothesis, fix contract, and planned verification.
- Make `tdd` require a complete Diagnosis Log before bug implementation.
- Make `code-review` validate the diagnosis-to-fix chain and fail missing evidence.
- Update Developer agents for both Claude and Codex so their Quality Bar includes the fix
  contract, not only root cause.

## 4. `debug` And `tdd` Overlap On Fix Ownership

Type: shared issue with a Claude review nuance.

Where it appears:

- `claude_skills_review.md`: Section 3, "debug to tdd fix overlap".
- `codex_skills_review.md`: `debug` was made diagnosis-only.
- Source areas:
  - `cli/src/ai_team/init/sources/skills/debug/body.md`
  - `cli/src/ai_team/init/sources/skills/tdd/body.md`
  - `cli/src/ai_team/init/sources/skills/bug-loop/body.md`

Why it matters:

If `debug` both diagnoses and fixes while `bug-loop` separately invokes `tdd`, the workflow has
two owners for the same implementation step. That can duplicate tests, skip the red/green
evidence, or blur where the Work Log belongs.

Suggested fix:

- Define two modes in `debug`:
  - Loop mode: stop after diagnosis handoff.
  - Standalone mode: may apply a minimal fix only when no loop will invoke `tdd`.
- Prefer the stricter Codex change for bug-loop: inside bug-loop, `debug` always stops after
  diagnosis and `tdd` owns implementation.
- Document the mode distinction in `ai-process/processes/workflow-overview.md`.

## 5. Code Review Checklist Ownership Is Split Between Skill And Agent

Type: shared issue; more visible in Claude because Claude agents were reviewed.

Where it appears:

- `claude_skills_review.md`: G4, checklist ownership was inverted.
- `codex_skills_review.md`: `code-review` strengthened evidence checks, but Codex agents were
  not updated.
- Source areas:
  - `cli/src/ai_team/init/sources/skills/code-review/body.md`
  - `cli/src/ai_team/init/sources/agents/claude/reviewer.md`
  - `cli/src/ai_team/init/sources/agents/codex/reviewer.toml`
  - `ai-process/guidelines/review-checklist.md`
  - `guides/agent_template.md`

Why it matters:

A skill should be reusable without depending on the full Reviewer agent being in context. If
the complete checklist lives only in the agent, a direct `code-review` invocation is weaker.

Suggested fix:

- Move the full two-stage review checklist and Bug Fix Addendum into `code-review`.
- Keep Reviewer agents as short role wrappers that point to the skill's checklist.
- Update `ai-process/guidelines/review-checklist.md` to match the skill or explicitly state
  that `code-review` is the executable checklist.
- Apply the same wrapper treatment to both Claude and Codex Reviewer agents.

## 6. Test Command Discovery Is Inconsistent

Type: shared issue with tool-specific guidance-file names.

Where it appears:

- `claude_skills_review.md`: G3, three different test-command-discovery rules.
- `codex_skills_review.md`: integration and loops need stronger evidence, but did not fully
  address command-source parity.
- Source areas:
  - `cli/src/ai_team/init/sources/skills/dev-loop/body.md`
  - `cli/src/ai_team/init/sources/skills/tdd/body.md`
  - `cli/src/ai_team/init/sources/skills/integrate/body.md`
  - `cli/src/ai_team/init/sources/root/CLAUDE.md`
  - `cli/src/ai_team/init/sources/root/AGENTS.md`
  - `guides/setup-guide.md`
  - `guides/customization-guide.md`
  - `ai-process/architecture/component-map.md`

Why it matters:

The loop, TDD, and integration should not infer different verification commands. If they do,
work can pass locally and fail at integration, or integration can block because it looks in a
different place from the Developer.

Suggested fix:

- Define a single precedence order:
  1. Work item `## Verification` or `## Fix Verification`.
  2. Root guidance for the active platform: `CLAUDE.md` for Claude Code, `AGENTS.md` for Codex,
     or both when both are scaffolded and equivalent.
  3. Explicit human instruction.
  4. Otherwise `BLOCKED`.
- Update `dev-loop`, `tdd`, and `integrate` to use that exact order.
- Resolve the current documentation inconsistency: some docs say root `CLAUDE.md` only, while
  others say `CLAUDE.md` and `AGENTS.md`.
- Add a scaffold test that checks root `CLAUDE.md` and `AGENTS.md` contain equivalent baseline
  test guidance.

## 7. Integration Can Proceed Without Enough Committed Review Evidence

Type: shared ai-process issue.

Where it appears:

- `codex_skills_review.md`: "Review And Integration Could Trust Chat Too Much".
- `claude_skills_review.md`: shared handoff contracts and integration cluster.
- Source areas:
  - `cli/src/ai_team/init/sources/skills/dev-loop/body.md`
  - `cli/src/ai_team/init/sources/skills/bug-loop/body.md`
  - `cli/src/ai_team/init/sources/skills/integrate/body.md`
  - `cli/src/ai_team/init/sources/skills/git-conventions/body.md`
  - `ai-process/processes/workflow-overview.md`
  - `ai-process/processes/quality-gates.md`

Why it matters:

Integration is Gate 4 and must consume Gate 3 evidence. If a branch is merged from a chat
summary instead of a committed `PASS` verdict in the canonical task or bug file, later agents
cannot audit what was approved.

Suggested fix:

- Require the active loop to pass source branch, destination branch, canonical lifecycle file,
  and latest committed `PASS` verdict heading/date to `integrate`.
- Require `integrate` to independently verify the latest canonical verdict is `PASS`.
- Stop integration if the source branch modifies task or bug lifecycle files.
- Add integration evidence output requirements to `git-conventions`.

## 8. Status Report Is Orphaned From The Loops

Type: shared issue; found explicitly by Claude review.

Where it appears:

- `claude_skills_review.md`: G2, `status-report` was orphaned.
- `codex_skills_review.md`: `status-report` was made CLI-first but loops were not fully wired
  to call it in the Codex pass.
- Source areas:
  - `cli/src/ai_team/init/sources/skills/status-report/body.md`
  - `cli/src/ai_team/init/sources/skills/status-report/metadata.toml`
  - `cli/src/ai_team/init/sources/skills/dev-loop/body.md`
  - `cli/src/ai_team/init/sources/skills/dev-loop/metadata.toml`
  - `cli/src/ai_team/init/sources/skills/bug-loop/body.md`
  - `cli/src/ai_team/init/sources/skills/bug-loop/metadata.toml`
  - `ai-process/processes/quality-gates.md`

Why it matters:

Gate 5 should have one status summary contract. If loops hand-roll summaries while
`status-report` also exists, the human can receive different evidence depending on which path
ran.

Suggested fix:

- Make `status-report` the canonical Gate 5 summary skill.
- Add `Skill(status-report)` to dev-loop and bug-loop allowed tools for both Claude and Codex
  metadata.
- Invoke `status-report` when each loop drains its queue or stops at a Gate 5-relevant summary
  point.
- Keep `disable-model-invocation` if the skill should not trigger from natural language, but
  ensure explicit loop invocation remains documented.

## 9. Planning Skill Boundaries Are Blurry

Type: shared ai-process issue.

Where it appears:

- `codex_skills_review.md`: "Planning Handoffs Were Blurry".
- `claude_skills_review.md`: planning cluster ownership decisions.
- Source areas:
  - `cli/src/ai_team/init/sources/skills/brainstorm/body.md`
  - `cli/src/ai_team/init/sources/skills/new-spec/body.md`
  - `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md`
  - `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md`
  - `cli/src/ai_team/init/sources/skills/new-task/body.md`
  - `ai-process/processes/workflow-overview.md`
  - `guides/spec-authoring-guide.md`

Why it matters:

If planning skills overlap, a Planner can put unresolved product decisions into task
descriptions or let Gate 2 become a second product approval. That weakens Gate 1 and makes
tasks less atomic.

Suggested fix:

- Define skill ownership:
  - `brainstorm`: direction and alternatives.
  - `new-spec`: Gate 1-ready spec drafting.
  - `spec-breakdown`: plan coverage, task boundaries, dependencies, file ordering.
  - `new-task`: one task's shape.
  - `spec-breakdown-review`: Gate 2 technical readiness.
- Make `spec-breakdown` stop when scope-affecting `[TODO]` items remain.
- Make `spec-breakdown-review` check spec coverage before dependency and file-conflict checks.
- Update `guides/spec-authoring-guide.md` if this changes what Gate 1 approval means.

## 10. EARS And Atomicity Rules Need One Canonical Home

Type: shared issue.

Where it appears:

- `claude_skills_review.md`: G5, EARS canonical home ambiguous.
- `codex_skills_review.md`: per-task quality owned by `new-task`; plan-wide correctness by
  `spec-breakdown` and `spec-breakdown-review`.
- Source areas:
  - `cli/src/ai_team/templates/task.md`
  - `cli/src/ai_team/init/sources/skills/new-task/body.md`
  - `cli/src/ai_team/init/sources/skills/spec-breakdown/body.md`
  - `cli/src/ai_team/init/sources/skills/spec-breakdown-review/body.md`
  - `guides/skill_template.md`

Why it matters:

If EARS pattern definitions and atomicity thresholds are spread across skills, tasks can be
accepted by one skill and rejected by another.

Suggested fix:

- Keep EARS definitions in `cli/src/ai_team/templates/task.md` or move a compact canonical
  definition into `new-task`; do not split definitions between both.
- Make `new-task` own per-task atomicity and one-shottable thresholds.
- Make `spec-breakdown` and `spec-breakdown-review` reference `new-task` for per-task rules
  while owning plan-wide coverage and dependency correctness.
- Add content validation to prevent numeric threshold leakage outside `new-task`.

## 11. Change Request Skill/Export Parity

Type: Claude export-specific symptom; shared source/rendering concern.

Where it appears:

- `claude_skills_review.md`: G1, `change-request` missing from the flattened Claude export.
- Source check: `cli/src/ai_team/init/sources/skills/change-request/` and generated
  `cli/src/ai_team/init/scaffolds/{claude,codex}/skills/change-request/SKILL.md` already
  exist.
- Source areas:
  - `cli/src/ai_team/init/sources/skills/change-request/body.md`
  - `cli/src/ai_team/init/sources/skills/change-request/metadata.toml`
  - `cli/src/ai_team/init/sources/agents/claude/planner.md`
  - `cli/src/ai_team/init/sources/agents/codex/planner.toml`
  - `cli/scripts/sync_init_scaffolds.py`
  - `ai-process/architecture/component-map.md`

Why it matters:

The workflow documents a lighter change-request intake path. If one export lacks the skill,
the Planner can create change requests in one tool but not another.

Suggested fix:

- Treat the missing flattened `claude_skills` copy as a stale export unless the package output
  also omits it.
- Improve the source `change-request` body and metadata with the Claude review's Quality
  Criteria and triggering improvements.
- Ensure both Claude and Codex Planner agent sources list `change-request`.
- Add a test that every source skill renders into both Claude and Codex scaffolds, with
  `change-request` explicitly asserted.

## 12. Agent Parity Between Claude And Codex

Type: tool-specific representation issue.

Where it appears:

- `claude_skills_review.md`: reviewed and changed 5 Claude agent role files.
- `codex_skills_review.md`: did not update Codex agent TOML files.
- Source areas:
  - `cli/src/ai_team/init/sources/agents/claude/*.md`
  - `cli/src/ai_team/init/sources/agents/codex/*.toml`
  - `guides/agent_template.md`

Why it matters:

The same role should enforce the same process contract whether invoked through Claude Code or
Codex. Different file formats are fine; different role behavior is not.

Suggested fix:

- Port any Claude agent changes to the corresponding Codex agent TOML developer instructions.
- Keep tool-specific phrasing only where the platform surface differs, such as file format,
  command invocation, or root guidance filename.
- Add a parity test or maintainer checklist that compares declared skills and key role
  sections across Claude and Codex agent sources.

## 13. Codex Skill Metadata Schema Is Ambiguous

Type: Codex-specific packaging/documentation issue.

Where it appears:

- `codex_skills_review.md`: remaining consideration about extra frontmatter fields.
- Source areas:
  - `cli/src/ai_team/init/sources/skills/*/metadata.toml`
  - `cli/scripts/sync_init_scaffolds.py`
  - `guides/skill_template.md`

Why it matters:

Codex skill triggering generally depends on `name` and `description`. The Codex-rendered
skills currently preserve Claude-style fields such as `allowed-tools`, `argument-hint`,
`effort`, and `disable-model-invocation`. If Codex ignores them, they are harmless but noisy;
if the framework expects them to be meaningful, that contract should be explicit.

Suggested fix:

- Decide whether Codex exports should preserve framework frontmatter fields for process
  parity or emit a Codex-native minimal header.
- Document that decision in `guides/skill_template.md`.
- If minimal Codex headers are desired, update `metadata.toml` codex headers and scaffold tests.
- If parity headers are desired, add a short note explaining that extra fields are
  framework-owned metadata and may be ignored by generic Codex skill loading.

## 14. Codex Skill UI Metadata Is Absent

Type: Codex-specific packaging issue, probably non-blocking.

Where it appears:

- `codex_skills_review.md`: no `agents/openai.yaml` files exist under `codex_skills/skills`.
- Source areas:
  - `guides/skill_template.md`
  - `cli/src/ai_team/init/sources/skills/*`

Why it matters:

System `skill-creator` recommends `agents/openai.yaml` for skill-list UI metadata. These
framework skills may not be installed as ordinary user skills, so absence may be acceptable.
The risk is ambiguity for maintainers.

Suggested fix:

- If these skills are intended for generic Codex skill installation, add generated
  `agents/openai.yaml` support in the source tree or a generation step.
- If not, explicitly document in `guides/skill_template.md` that AI-team framework skill
  exports do not include `agents/openai.yaml` because role/tool metadata is represented by the
  framework agent files and skill frontmatter.

## 15. Source-Of-Truth Porting Is Required

Type: shared repository maintenance issue.

Where it appears:

- Both reports note that changes were made to flattened review copies, not durable source.
- Source areas:
  - `cli/src/ai_team/init/sources/skills/*`
  - `cli/src/ai_team/init/sources/agents/*`
  - `cli/src/ai_team/init/scaffolds/*`
  - `cli/scripts/sync_init_scaffolds.py`

Why it matters:

Edits in `claude_skills/` and `codex_skills/` are review artifacts. They will not affect the
package unless ported to `cli/src/ai_team/init/sources/` and regenerated.

Suggested fix:

- Port shared skill edits to `cli/src/ai_team/init/sources/skills`.
- Port role-specific edits to both `agents/claude` and `agents/codex`.
- Run `python cli/scripts/sync_init_scaffolds.py`.
- Run repo checks.
- If command output or release guidance changes, run `bash cli/scripts/gen_docs.sh`.

## Suggested Implementation Order

1. Update `git-conventions` and `escalation-review` first because other skills should point to
   those canonical contracts.
2. Update `debug`, `tdd`, `code-review`, `bug-loop`, and `new-bug` as one bug-flow contract.
3. Update `dev-loop`, `bug-loop`, `integrate`, `merge-conflicts`, and `status-report` as one
   integration/Gate 5 contract.
4. Update `brainstorm`, `new-spec`, `spec-breakdown`, `spec-breakdown-review`, `new-task`, and
   `new-adr` as one planning/Gate 2 contract.
5. Port agent wrapper changes for both Claude and Codex.
6. Update `ai-process/` and `guides/` to match the executable skill contracts.
7. Regenerate scaffolds and run tests.

## Verification To Add Or Run

Recommended checks after implementation:

```bash
cd cli
python scripts/sync_init_scaffolds.py
uv run pytest
uv run ruff format --check .
uv run ruff check .
```

Recommended new or strengthened tests:

- Assert every source skill renders into both Claude and Codex scaffold directories.
- Assert `change-request` appears in both Claude and Codex scaffold skills and Planner agent
  skill lists.
- Assert `dev-loop` and `bug-loop` invoke `status-report` and declare it in allowed tools.
- Assert escalation field names are consistent where skills can emit `ESCALATE`.
- Assert atomicity thresholds appear only in `new-task` if that remains the canonical home.
- Assert Claude and Codex agent sources have matching declared skill sets for equivalent roles,
  allowing only platform-specific format differences.
