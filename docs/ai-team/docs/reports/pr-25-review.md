# PR Review: aurora-firmware/The-AI-team-definition#25 — Fix/status report model invocation

## Summary
This PR adds an S-003 spec and related project artifacts, introduces a global development warning, adds the `ai-team check-layout` diagnostic command with layout validation levels, and updates CLI/user documentation plus tests. I reviewed the source and documentation scopes inline because parallel subagents were not available in this environment. No review findings were identified.

| Scope | Files | Lines changed | Tier | Findings |
|---|---:|---:|---|---:|
| Source | 17 | 1574 | full | 0 |
| Documentation | 10 | 1096 | full | 0 |

## Findings

No findings.

## Skipped files

None.

## Review notes

- Existing PR review comments fetched: 0.
- Noise filtering skipped no files; no security-flagged files were identified.
- Source review covered the changed CLI implementation and tests, with surrounding context read for the new layout core and command registration patterns.
- Documentation review covered the changed usage guide, generated command docs, S-003, change request, and completed task artifacts for consistency with the implementation.
- Verification run: `cd cli && uv run pytest -q` — 422 passed.
