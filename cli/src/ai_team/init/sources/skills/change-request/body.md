# Change Request

Create a new change-request artifact using `ai-team change-request new --json`, then fill the body with the proposed scope change.

## Input Requirements

Provide these values directly when possible:
- `title` — required
- `description` — required; summarize the requested change, why it is needed, affected specs or tasks, and any known risk

When invoked directly and required fields are missing, ask only for the missing fields before proceeding.

## Procedure

1. Resolve inputs:
   - Use the caller-provided `title` and `description` when present.
   - Use `$ARGUMENTS` as the title when it is the only provided input.
   - If the title or description is still missing, ask for the missing value.

2. Create the artifact:
   - Run `ai-team change-request new "<title>" --json`.
   - Parse the JSON response to capture `id` and `path`.

3. Open the created file and replace template placeholders with the supplied description.
   - Keep the frontmatter produced by the CLI.
   - Preserve the template structure unless the human explicitly requested a different format.
   - Mark unknown details as `[TODO]` instead of inventing them.

4. Confirm the created file exists and return the CLI response values.

5. When the change-request proposes a spec amendment or otherwise touches an existing spec or ADR, hand it to the Architect for an Architecture Consistency Review (Next Owner: Architect) so the proposed change is checked against every approved spec and accepted ADR before it is applied. The Architect returns findings for the Planner to resolve.

## Quality Criteria

- The artifact id and path come from the CLI response.
- The title is reflected in the file heading.
- The body states the requested change, reason, affected artifacts, and unresolved questions.
- Unknown or unconfirmed details remain marked `[TODO]`.

## Common Pitfalls

- **Raising a change-request when a new spec is warranted** — if the proposed change adds a significant new capability, a new workflow, or a new system component, open a spec instead. A change-request is for scope amendments to an existing, approved spec, not a vehicle for speccing new work.
- **Vague change description** — "update the spec" or "fix the task" is not a change description. Name the specific section, requirement, or acceptance criterion that must change and state why the current wording is wrong or incomplete.
- **Missing affected-artifact list** — every change-request must name the specs, tasks, or other artifacts it touches. Omitting this forces reviewers to guess the blast radius and risks silent conflicts with in-flight tasks.
- **Missing risk notes** — if the change could break a dependency, invalidate work already in progress, or require re-review of a gate, say so. Silently omitting known risks is the most common reason change-requests are rejected or returned for revision.
- **Inventing details instead of marking `[TODO]`** — when the full impact of a change is not yet known, mark the gap `[TODO]` rather than filling it with plausible-sounding but unconfirmed content. Invented details mislead reviewers and produce incorrect downstream tasks.

## Output Format

Always return:

```text
Result: PASS | FAIL | BLOCKED

Summary:
- <brief statement of the change request created>

Artifacts:
- <change-request file created>

Evidence:
- <CLI command result or reason not run>

Obstacles Encountered:
- <missing input, unresolved scope issue, or "none">

Next Owner:
- <Human | Planner | Architect | none>

Next Action:
- <specific follow-up required, or "none">
```
