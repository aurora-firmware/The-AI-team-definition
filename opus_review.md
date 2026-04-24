# ai-process references in .claude/

## Summary

- Total files under `.claude/agents/` that reference `ai-process/`: **2**
- Total files under `.claude/skills/` that reference `ai-process/`: **5**
- Total distinct `ai-process/...` paths referenced: **4**
- Distinct paths referenced (all verified to exist on disk):
  - `ai-process/guidelines/coding-standards.md` — **EXISTS**
  - `ai-process/guidelines/git-conventions.md` — **EXISTS**
  - `ai-process/guidelines/review-checklist.md` — **EXISTS**
  - `ai-process/processes/escalation-procedure.md` — **EXISTS**

Notably, `ai-process/architecture/`, `ai-process/processes/quality-gates.md`, and `ai-process/processes/workflow-overview.md` are never cited by any `.claude/` file.

---

## References by file

### Agents

#### `.claude/agents/developer.md`

- `ai-process/processes/escalation-procedure.md` — line `55` — `After three failures, stop retrying and enter the escalation chain (see \`ai-process/processes/escalation-procedure.md\`).`
- `ai-process/guidelines/coding-standards.md` — line `85` — `Code follows the coding standards: \`ai-process/guidelines/coding-standards.md\` (general) and \`project/docs/coding_guidelines...`

#### `.claude/agents/reviewer.md`

- `ai-process/guidelines/review-checklist.md` — line `78` — `See \`ai-process/guidelines/review-checklist.md\` for the complete checklist used in each review.`

---

### Skills

#### `.claude/skills/bug-loop/SKILL.md`

- `ai-process/processes/escalation-procedure.md` — line `153` — `Follow the two-phase escalation procedure from \`ai-process/processes/escalation-procedure.md\`:`
- `ai-process/guidelines/git-conventions.md` — line `188` — `All orchestrator commits follow the project's git conventions from \`ai-process/guidelines/git-conventions.md\`:`

#### `.claude/skills/code-review/SKILL.md`

- `ai-process/guidelines/review-checklist.md` — line `15` — `- **Review checklist** — \`ai-process/guidelines/review-checklist.md\`.`
- `ai-process/guidelines/review-checklist.md` — line `42` — `Review the code against the checklist in \`ai-process/guidelines/review-checklist.md\`:`
- `ai-process/guidelines/git-conventions.md` — line `60` — `Commit the verdict on \`dev-agent\` according to \`ai-process/guidelines/git-conventions.md\`.`

#### `.claude/skills/dev-loop/SKILL.md`

- `ai-process/processes/escalation-procedure.md` — line `117` — `Follow the two-phase escalation procedure from \`ai-process/processes/escalation-procedure.md\`.`
- `ai-process/guidelines/git-conventions.md` — line `157` — `All orchestrator commits follow the project's git conventions from \`ai-process/guidelines/git-conventions.md\`:`

#### `.claude/skills/integrate/SKILL.md`

- `ai-process/guidelines/git-conventions.md` — line `180` — `All integrator commits follow \`ai-process/guidelines/git-conventions.md\`:`

#### `.claude/skills/tdd/SKILL.md`

- `ai-process/guidelines/coding-standards.md` — line `13` — `- **Coding standards** — \`ai-process/guidelines/coding-standards.md\` for framework standards, plus target-project guid...`

---

## Broken or suspicious references

None found. All 4 distinct `ai-process/` paths cited across 7 files resolve to files that exist on disk. No typos, wrong subfolders, or stale paths detected.
