---
title: "Customization Guide"
status: approved
created: 2026-03-10
---

# Customization Guide

This guide explains what to adapt when adopting the AI team framework for your project.

## What ai-team init Exports As-Is

The `ai-team init` command exports these files from the CLI package scaffold sources. They are generic and work for any project without modification:

| Category | Destination in your project |
|---|---|
| **Agent definitions** | `.claude/agents/` — roles are universal |
| **Skill definitions** | `.claude/skills/` — procedures are language-agnostic |
| **All templates** | `TEMPLATE-*.md` files in `.claude/skills/*/assets/` |
| **Action skills** | Action skills in `.claude/skills/` (`disable-model-invocation: true` only for human-only actions that no other skill invokes) |
| **Codex agents** | `.codex/agents/*.toml` (only when `--tools codex` is passed) |

The `ai-process/` specification documents (process docs, guidelines, architecture docs) are **not** exported. They live in the AI team definition meta-repository and serve as the authoritative spec for the rules that agents and skills implement. Your project does not need them; the agent and skill files already embed the rules they need to execute.

## What to Customize

### Must Customize

**`CLAUDE.md`** — Your project's identity:
- Replace the project name and purpose description.
- Add your tech stack, repository layout, and the specific build/run/test/lint commands agents should use.
- Point agents to project-local conventions, including `ai-team/docs/coding_guidelines.md` if present.
- Keep the Repository Map, How to Work Here, and Conventions sections. Update paths to match your project layout.

**`README.md`** — Your project's README:
- Write a new README describing your actual project, not the framework.
- Reference the framework workflow in a "Development Process" section.

**Project-local coding guidance** — Stack-specific rules:
- Keep `ai-process/guidelines/coding-standards.md` as the framework's general, language-agnostic baseline unless you are intentionally forking the process.
- Put project-specific coding rules in `ai-team/docs/coding_guidelines.md` or another project-local document referenced by your `CLAUDE.md`.
- Include formatter, linter, test framework, dependency policy, naming conventions, file layout, and framework conventions there.
- Agents and skills should discover these details from the target project instead of relying on hardcoded defaults in the framework.

**Verification commands** — Project-specific commands:
- Define build, run, lint, test, and integration verification commands in `CLAUDE.md`, task files, README, or project-local docs.
- The integration procedure reads these commands from the project; it should stop and ask if it cannot determine the correct command.

### Root CLAUDE.md and AGENTS.md

`ai-team init` can scaffold two root-level guidance files from starter templates:

- **`CLAUDE.md`** (repo root) — read by Claude and the dev-loop. The `## Test`
  section is the primary place to document the build, test, lint, and run
  commands for your project. The dev-loop reads this file before starting any
  session so agents can run your tests without guessing.
- **`AGENTS.md`** (repo root) — read by non-Claude AI tooling (for example,
  Codex). Mirror your `## Test` section here if you use Codex agents so they
  also have the correct commands. Claude reads `CLAUDE.md`, not `AGENTS.md`.

#### What they're for

These files give AI tools the project-specific context they cannot infer from
source code alone: how to install dependencies, how to run the test suite, how
to lint, and what environment assumptions apply. Without them, agents fall back
to guessing — or stop and ask, slowing down the loop.

#### The `## Test` section convention

The dev-loop skill reads the `## Test` section of `CLAUDE.md` to determine the
verification command for a task. Structure it like this:

```markdown
## Test

\`\`\`bash
uv run pytest
uv run ruff format --check .
uv run ruff check .
\`\`\`
```

Keep this section accurate. If the test command changes (new linter added,
test runner changed), update `CLAUDE.md` in the same commit.

#### Workflow after `ai-team init` scaffolds them

1. Open the generated `CLAUDE.md` and `AGENTS.md` from the starter templates.
2. Replace the placeholder project name and description.
3. Fill in your actual build, test, lint, and run commands under `## Test`.
4. Add your tech stack, repo layout, and any agent-facing conventions.
5. Commit both files. They are yours to maintain — re-running `ai-team init`
   without `--force` will not overwrite them.

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

**Escalation thresholds** — In `ai-process/processes/escalation-procedure.md`:
- Default: architect consultation after failure, then human escalation.
- For faster iteration: skip architect, escalate directly to human.
- For more autonomy: allow two architect consultations before human escalation.

## Extending the Framework

### Adding New Agent Roles

Use `guides/agent_template.md` as a reference. Common additions:
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
4. Create `ai-team/docs/coding_guidelines.md` for stack-specific conventions if those rules are not already documented elsewhere.
5. Migrate existing issues/tasks by creating a task for each open item with `ai-team task new` (they land in the local tracker).
6. Write a specification for the current system state in `ai-team/specs/` — this becomes the baseline.
7. Create an ADR in `ai-team/decisions/` documenting the decision to adopt this framework.
