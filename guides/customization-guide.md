---
title: "Customization Guide"
status: approved
created: 2026-03-10
---

# Customization Guide

This guide explains what to adapt when adopting the AI team framework for your project.

## What to Copy As-Is

These files are generic and work for any project without modification:

| Category | Files |
|---|---|
| **Agent definitions** | All files in `.claude/agents/` — roles are universal |
| **Skill definitions** | All files in `.claude/skills/` — procedures are language-agnostic |
| **Process docs** | `ai-process/processes/workflow-overview.md`, `quality-gates.md`, `escalation-procedure.md` |
| **Review checklist** | `ai-process/guidelines/review-checklist.md` |
| **Markdown conventions** | `ai-process/guidelines/markdown-conventions.md` |
| **Architecture docs** | `ai-process/architecture/system-overview.md`, `component-map.md` |
| **All templates** | `TEMPLATE-*.md` files in `.claude/skills/*/assets/` and `ai-process/templates/` |
| **Action skills** | Action skills in `.claude/skills/` (with `disable-model-invocation: true`) |

## What to Customize

### Must Customize

**`CLAUDE.md`** — Your project's identity:
- Replace the project name and purpose description.
- Add your tech stack, repository layout, and the specific build/run/test/lint commands agents should use.
- Point agents to project-local conventions, including `project/docs/coding_guidelines.md` if present.
- Keep the Repository Map, How to Work Here, and Conventions sections. Update paths to match your project layout.

**`README.md`** — Your project's README:
- Write a new README describing your actual project, not the framework.
- Reference the framework workflow in a "Development Process" section.

**Project-local coding guidance** — Stack-specific rules:
- Keep `ai-process/guidelines/coding-standards.md` as the framework's general, language-agnostic baseline unless you are intentionally forking the process.
- Put project-specific coding rules in `project/docs/coding_guidelines.md` or another project-local document referenced by your `CLAUDE.md`.
- Include formatter, linter, test framework, dependency policy, naming conventions, file layout, and framework conventions there.
- Agents and skills should discover these details from the target project instead of relying on hardcoded defaults in the framework.

**Verification commands** — Project-specific commands:
- Define build, run, lint, test, and integration verification commands in `CLAUDE.md`, task files, README, or project-local docs.
- The integration procedure reads these commands from the project; it should stop and ask if it cannot determine the correct command.

### Optional Customization

**Agent subset** — Not every project needs all 5 agents:

| Team Size | Recommended Agents |
|---|---|
| Solo (1 agent) | Developer (combines all roles) |
| Small (2-3 agents) | Planner + Developer + Reviewer |
| Standard (4 agents) | Planner + Developer + Reviewer + Integrator |
| Full (5 agents) | All agents including Architect |

To reduce the team: keep only the agent files you need. The workflow still works — agents whose roles are absent have their responsibilities absorbed by adjacent agents (e.g., without an integrator, the developer handles merges).

**Quality gate criteria** — Adjust `ai-process/processes/quality-gates.md`:
- Gate 1 is human specification approval.
- Gate 2 is Architect task-plan preflight.
- Gate 3 is code review.
- Gate 4 is integration verification.
- Gate 5 is human final merge sign-off.
- If your project needs a different gate model, update `ai-process/processes/quality-gates.md`, `ai-process/processes/workflow-overview.md`, and the affected skills together.

**Temperature guidance** — In agent definitions:
- The defaults (creative 0.7, structured 0.2, execution 0.3, review 0.4) work well for most cases.
- Lower temperatures for safety-critical code.
- Higher temperatures for creative or design-heavy work.

**Escalation thresholds** — In `ai-process/processes/escalation-procedure.md`:
- Default: architect consultation after failure, then human escalation.
- For faster iteration: skip architect, escalate directly to human.
- For more autonomy: allow two architect consultations before human escalation.

## Extending the Framework

### Adding New Agent Roles

Use `.claude/agents/TEMPLATE-agent.md`. Common additions:
- **DevOps agent** — manages CI/CD, deployment, infrastructure.
- **Documentation agent** — writes user-facing docs, API references.
- **Security agent** — dedicated security review, dependency auditing.

### Adding New Skills

Create a new directory under `.claude/skills/<name>/` with a `SKILL.md` file. Common additions:
- **Database migration** — schema changes with rollback procedures.
- **API design** — REST/GraphQL endpoint design following project conventions.
- **Performance profiling** — identify and fix performance bottlenecks.

### Adding New Action Skills

Create a new directory under `.claude/skills/<name>/` with a `SKILL.md` file. Add the `disable-model-invocation: true` frontmatter field if the skill should be user-invocable only (not triggered by the model). Reference existing skills as examples.

## Retrofitting Into an Existing Project

If you have an existing codebase:

1. Follow the setup guide to create the directory structure alongside your existing code.
2. Your existing source code stays where it is — the framework directories are additive.
3. Write or update `CLAUDE.md` so agents can find project commands, coding guidance, and repository layout.
4. Create `project/docs/coding_guidelines.md` for stack-specific conventions if those rules are not already documented elsewhere.
5. Migrate existing issues/tasks by creating task files in `project/tasks/pending/` for each open item.
6. Write a specification for the current system state in `project/specs/` — this becomes the baseline.
7. Create an ADR in `project/decisions/` documenting the decision to adopt this framework.
