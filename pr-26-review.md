# PR Review: aurora-firmware/The-AI-team-definition#26 - change request automatic cycle and interactive TODO solving

## Summary

This PR updates the S-004 process contract, source skill bodies, generated skill scaffolds, tests, and project lifecycle artifacts for TODO-ready specs and uninterrupted change-request continuation. The skill changes and focused tests are internally consistent, and the PR head matches the local `dev-agent` branch. I found one warning: the packaged Planner agent sources still describe the old handoff timing, so initialized agents can continue to route work before the new TODO-free approval boundary.

| Scope | Files | Lines changed | Tier | Findings |
|---|---:|---:|---|---:|
| Documentation | 21 | 1188 | full | 1 |
| Source | 2 | 206 | full | 0 |
| Security | 0 | 0 | none | 0 |

## Findings

### Documentation

#### [warning] Planner agent sources still advertise the old handoff boundary - `ai-process/processes/quality-gates.md:43`

The new process contract says a change-request reaches Architecture Consistency Review only after it is TODO-free and human-approved, and that draft/amended specs must resolve human-answerable TODOs before review. However, the packaged Planner agent sources were not updated: `cli/src/ai_team/init/sources/agents/{claude,codex}/planner.*` and their generated scaffolds still say the Planner hands off a change-request "before its amendments are applied" and a spec "before Gate 1", with no TODO-free or approval condition. Those files are part of the exported framework instructions, so projects initialized from this PR can still get a Planner role prompt that contradicts the new gate and skill behavior. Update the Planner source agent instructions and regenerate the agent scaffolds so the role-level handoff contract matches the changed process and skills.

## Skipped Files

None. Generated scaffold files were reviewed for source/scaffold consistency rather than as independent prose.

## Review Notes

- Fetched PR metadata, files, full diff, and existing review comments with `gh`; existing review comments were empty.
- Local `dev-agent` is PR head `82e6c8c87b80466e562eb389e7bb6d3acc9a611d`; `origin/main` is base `28d2b0e7247cb06e60d718c6ea0a626adbf40b0e`.
- Reviewed changed process docs, S-004 spec, source skill bodies, generated skill scaffolds, and focused tests. Also checked related Planner agent source/scaffold instructions because the changed contract alters role handoff timing.
- Verification run: `UV_CACHE_DIR=/tmp/uv-cache-pr26 uv run pytest tests/test_t074_change_request_continuation.py tests/test_t076_spec_todo_readiness.py` from `cli/` passed with `10 passed`.
- `python cli/scripts/sync_init_scaffolds.py` completed and left the worktree clean.

## Developer Response

- Fixed the warning. Updated the Claude and Codex Planner source agent instructions so specs are handed to Architecture Consistency Review only after human-answerable `[TODO]` markers are resolved, and change-requests only after they are TODO-free and human-approved. Regenerated the corresponding Planner scaffolds and added a regression test covering the handoff language.
- Verification: `UV_CACHE_DIR=/tmp/uv-cache-pr26-dev uv run pytest tests/test_init_scaffolds.py::test_planner_agents_document_todo_ready_architecture_review_handoff tests/test_init_scaffolds.py::test_package_owned_agent_sources_cover_each_exported_role_for_both_tools tests/test_t074_change_request_continuation.py tests/test_t076_spec_todo_readiness.py` from `cli/` passed with `12 passed`; `UV_CACHE_DIR=/tmp/uv-cache-pr26-dev uv run ruff check tests/test_init_scaffolds.py` passed; `UV_CACHE_DIR=/tmp/uv-cache-pr26-dev uv run ruff format --check tests/test_init_scaffolds.py` passed.

## Re-review

Result: resolved locally.

The response patch updates both Planner source agent definitions and both generated Planner scaffold files so the handoff language now requires human-answerable `[TODO]` resolution before spec Architecture Consistency Review and TODO-free human approval before change-request Architecture Consistency Review. The new regression test checks all four source/scaffold files for the required replacement wording and rejects the old abbreviated handoff phrases.

Verification rerun from `cli/`:

- `UV_CACHE_DIR=/tmp/uv-cache-pr26-rereview uv run pytest tests/test_init_scaffolds.py::test_planner_agents_document_todo_ready_architecture_review_handoff tests/test_init_scaffolds.py::test_package_owned_agent_sources_cover_each_exported_role_for_both_tools tests/test_t074_change_request_continuation.py tests/test_t076_spec_todo_readiness.py` -> `12 passed`
- `UV_CACHE_DIR=/tmp/uv-cache-pr26-rereview uv run ruff check tests/test_init_scaffolds.py` -> passed
- `UV_CACHE_DIR=/tmp/uv-cache-pr26-rereview uv run ruff format --check tests/test_init_scaffolds.py` -> passed
- `python scripts/sync_init_scaffolds.py` -> completed without adding extra changes beyond the expected Planner scaffold files

Remote caveat: GitHub still reports PR head `82e6c8c87b80466e562eb389e7bb6d3acc9a611d` with 23 changed files, so this fix appears present in the local workspace but not yet pushed to the remote PR.
