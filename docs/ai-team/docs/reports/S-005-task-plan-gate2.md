# S-005 task plan — Gate 2 passed (2026-09-30)

Planner output, transcribed by the coordinator; reviewed by the Architect (Gate 2: round 1 FAIL, round 2 PASS with R1–R4 folded in). Tasks were created from this plan with `ai-team task new`.

## Plan ID to task ID

| Plan | Task |
|---|---|
| P1 | T-078 |
| P2 | T-079 |
| P3 | T-080 |
| P4 | T-081 |
| P5 | T-082 |
| P6 | T-083 |
| P7 | T-084 |
| P8 | T-085 |
| P9 | T-086 |
| P10 | T-087 |
| P11 | T-088 |
| P12 | T-089 |
| P13 | T-090 |
| P14 | T-091 |
| P15 | T-092 |
| P16 | T-093 |
| P17 | T-094 |
| P18 | T-095 |
| P19 | T-096 |
| P20 | T-097 |
| P21 | T-098 |
| P22 | T-099 |
| P23 | T-100 |
| P24 | T-101 |
| P25 | T-102 |
| P26 | T-103 |
| P27 | T-104 |
| P28 | T-105 |
| P29 | T-106 |
| P30 | T-107 |
| P31 | T-108 |
| P32 | T-109 |
| P33 | T-110 |
| P34 | T-111 |
| P35 | T-112 |
| P36 | T-113 |
| P37 | T-114 |
| P38 | T-115 |
| P39 | T-116 |
| P40 | T-117 |
| P41 | T-118 |
| P42 | T-119 |
| P43 | T-120 |
| P44 | T-121 |
| P45 | T-122 |
| P46 | T-123 |
| P47 | T-124 |
| P48 | T-125 |

Revision 3: Gate 2 PASSED (round 2); R1–R4 folded in. Revision 2: Gate 2 round-1 findings B1–B7, N1–N13 and ruling conditions applied (marked [G2]).

Spec: docs/ai-team/specs/S-005-pi-extension-package-skeleton-and-artifact-core.md (v1.0, approved)
ADRs: ADR-001, ADR-002, ADR-003, ADR-004
Every task: spec S-005, assigned-role developer. Plan-local IDs P1–P48 map to T-IDs at creation.

## Verification shorthands

- V-PY (from cli/): `uv run pytest && uv run ruff format --check . && uv run ruff check .` (UV_CACHE_DIR under /tmp if needed)
- V-SYNC: the sync command documented in CLAUDE.md's Build section (currently, from cli/: `python scripts/sync_init_scaffolds.py`; if P22 changes it, every later task and P47 follow the documented command) [G2 R1]
- V-DOCS (repo root): `bash cli/scripts/gen_docs.sh && git diff --exit-code cli/docs/commands.md`
- V-GOLD (repo root): `git diff --exit-code "$(git merge-base HEAD main)" -- cli/src/ai_team/init/scaffolds/claude cli/src/ai_team/init/scaffolds/codex`
- V-PI (from pi/, after V-SYNC): `npm ci && npm run typecheck && npm test` (names proposed; fixed in CLAUDE.md by P3)
- V-PI-F <prefix> (from pi/): `npm test -- parity -t "<prefix>"`

## Phase 0: guides and architecture docs

### P1: Update the skill guide for the pi target and the marker contract
- Priority high. Depends: none. Files: guides/skill_template.md
- Scope: pi as third render target; three marker kinds and per-target rendering (command marker call vs mention form by required-positional presence; `{{ai-team-flag}}` renders "set `<field>`" or bare field inside backticks; `{{ai-team-cli|cc|pi}}`); fence rules (markers-only fence becomes prose for pi, mixed fence fails); call-form placeholders checked by field name/presence not value; inline-context rule; markers allowed in [claude]/[codex] headers; pi header derived from [claude] name/description, no [pi] section (ADR-002); how Skill(<name>), the self-contained .claude/ rule and allowed-tools apply to pi; orchestrators (dev-loop, bug-loop, integrate) rendered but excluded from pi manifest until sub-project 5; command map is the single command surface (ADR-004). Out of scope: skill sources, sync, tests, other guides.
- AC-1 guide defines syntax and per-target rendering of all three kinds, incl. call/mention selection and fence rules (SC-1, marker contract). AC-2 pi header derivation, no [pi] section, noun markers render pi text (SC-1, ADR-002). AC-3 pi applicability of Skill(), .claude/ rule, allowed-tools (SC-1). AC-4 orchestrators rendered but not shipped (SC-10). AC-5 command map named as single source (ADR-004).
- Verify: grep for ai-team-flag / ai-team-cli / mention form / [claude] in the guide; V-PY.

### P2: Update the component map and system overview
- Priority high. Depends: none. Files: ai-process/architecture/component-map.md, ai-process/architecture/system-overview.md
- Scope: add pi/ package and adapter, TS core, command map, sync pi target and generated pi/resources/ (incl. git-ignored version file), fixtures/parity/ contract and two runners, per-implementation locks (ADR-003), co-equal implementations (ADR-004); map CLI commands to ai_team tool commands. Out of scope: guides, CLAUDE.md, code.
- AC-1 each new component with owning path and interface (SC-1). AC-2 flow sync→pi resources→adapter→TS core, fixtures bind both implementations (SC-1, ADR-004). AC-3 own locks, mixed concurrency unsupported (ADR-003). AC-4 pi/resources generated never hand-edited; claude/codex exports unchanged.
- Verify: grep for pi/ / parity / command map; V-PY.

### P3: CLAUDE.md pi checks and setup-guide pi install steps
- Priority high. Depends: none. Files: CLAUDE.md, guides/setup-guide.md
- Scope: CLAUDE.md Key Conventions gain pi/, pi/resources/ (generated), fixtures/parity/ (reviewed contract); pi commands from pi/: `npm ci`, `npm run typecheck`, `npm test`, sync first (writes version file); behaviour change starts with reviewed fixture change. Setup guide: one-time sync then `pi install <path-to-pi>`; cross-commit Level 4 mismatch expected; mixed concurrent allocation unsupported; pi init writes empty [init].tools and no .claude/.codex. Out of scope: pi README (P23), other guides.
- AC-1 CLAUDE.md documents pi typecheck/test and sync-first (SC-1, SC-13). AC-2 pi/resources generated, fixtures/parity reviewed contract (ADR-004). AC-3 local-path install incl. one-time sync (SC-1). AC-4 mixed concurrency unsupported, cross-commit mismatch expected (SC-7, Config). AC-5 pi init empty tools, no .claude/.codex.
- Verify: grep for npm run typecheck / pi install / unsupported; V-PY.

## Phase 1: Python parity groundwork

### P4: Injectable "today" and framework version in the Python CLI
- Priority high. Depends: P1, P2, P3. Files: new cli/src/ai_team/core/<runtime>.py; commands/{spec,task,bug,adr,change_request,archive,report,init}.py; core/layout.py; new test; new maintainer note under cli/docs/ (not usage.md). Size note: over file guideline, one-line swaps.
- Scope: one core module exposes today and framework version, each reading a test-only env override in one place (task picks names, records them); replace every date.today() and importlib.metadata.version("ai-team"); invalid ISO override fails naming the variable. Out of scope: structured results, locking, --version output, user-visible output.
- AC-1 only the new module supplies today/version; no other date.today()/metadata.version("ai-team") in commands/ or core/. cli.py `--version` is explicitly exempt. [G2 N1]
- AC-6 the new module looks up importlib.metadata.version at call time (no from-import), so the existing monkeypatch in cli/tests/test_layout.py keeps working. [G2 N1] AC-2 clock override used for created dates, work-log dates, report date, archive cut-off. AC-3 version override written/compared as framework_version. AC-4 without overrides stdout/stderr/exit codes unchanged (SC-6). AC-5 invalid ISO fails naming the variable.
- Verify: V-PY; grep for date.today()/metadata.version in commands and core (only new module).

### P5: Structured-result type; apply to spec new, adr new, change-request new
- Priority high. Depends: P4. Files: new core/result.py (or equivalent), commands/spec.py, adr.py, change_request.py, cli/src/ai_team/core/locator.py [G2 B5], new cli/tests/test_structured_results_create.py
- Scope: internal result type with exit status, payload, error message and hint as separate fields; CLI text still joins them as today; each command split into a pure handler (explicit ProjectRoot, typed input → result) and the Typer wrapper; for --json commands payload equals the printed JSON. Out of scope: other modules, new public flags (ADR-004).
- [G2 B5] Also split ProjectRootNotFound in core/locator.py (lines ~133-188) so the exception carries message and hint separately, while str() joins them exactly as today. P5 is the only task that edits locator.py.
- AC-1 result type carries status, payload, message, hint separately. AC-2 --json output equals handler payload. AC-3 handlers run with explicit root, no Typer, no process cwd. AC-4 domain errors: message equals today's stderr minus hint. AC-5 CLI output unchanged (SC-6). AC-6 ProjectRootNotFound exposes separate message and hint fields, and its str() equals today's text (SC-6, Tool contract). [G2 B5]
- Verify: V-PY.

### P6: Structured results for task and bug commands
- Priority high. Depends: P5. Files: commands/task.py, commands/bug.py, new cli/tests/test_structured_results_lifecycle.py
- Scope: task new/start/complete/block/unblock, bug new/start/resolve; "already in <state>" (exit 0) and not-found become structured results.
- AC-1 pure handlers for every task/bug leaf command. AC-2 --json equals payload. AC-3 already-in-state returns success with today's text. AC-4 not-found error with today's message. AC-5 output unchanged (SC-6).
- Verify: V-PY.

### P7: Structured results for list, show, status, report
- Priority high. Depends: P5. Files: commands/list.py, show.py, status.py, report.py, new cli/tests/test_structured_results_query.py [G2 N6]
- Scope: --json JSON is the result where it exists; define report's internal result (written path, content/summary pinned by fixtures). [G2 B6] The latest-integration-result lookup (status.py `_latest_integration_result`, a `git log --all --grep` call reused by report via `_payload`) is part of the structured result; fixtures pin its "not found" branch.
- AC-1 pure handlers for every list leaf, show, status, report. AC-2 payload equals --json where it exists. AC-3 report returns written path with/without --out. AC-4 show unknown id error with today's message. AC-5 output unchanged (SC-6).
- Verify: V-PY.

### P8: Structured results for validate, archive, check-layout
- Priority high. Depends: P5. Files: commands/validate.py, archive.py, check_layout.py, new cli/tests/test_structured_results_checks.py [G2 N6]
- Scope: validate returns findings (code, path, message) and selecting flags; archive returns moved/would-move paths; check-layout findings carry suggested fix separately; internal only (S-003 deferral stands). Out of scope: public --json, new finding codes.
- AC-1 pure handlers. AC-2 check-layout suggested fix separate from message. AC-3 archive --dry-run returns candidates, changes nothing. AC-4 validation failure exit status equals today's. AC-5 output unchanged, no public flags (SC-6, ADR-004).
- Verify: V-PY; V-DOCS.

### P9: Structured result for init with internal empty-tools mode
- Priority high. Depends: P5. Files: commands/init.py, new cli/tests/test_structured_results_init.py [G2 N6]
- Scope: pure handler with path, force, dry_run, create_root_guidance and an explicit (possibly empty) tool list, non-interactive; result lists written/planned files and root-guidance outcome; "declined" note is presentation only; can write .ai-team.toml with tools = [] so pi-semantics fixtures can be seeded from Python; CLI --tools/--no-interactive surface unchanged. Out of scope: skeleton .gitignore (P10), TS.
- AC-1 explicit possibly-empty tool list without prompting. AC-2 empty list writes empty [init].tools and framework_version from P4. AC-3 declined note excluded from result. AC-4 dry_run returns plan, writes nothing. AC-5 CLI output and prompts unchanged (SC-6); `--no-interactive` without `--tools` still fails (init.py:67) — the empty-tools mode is internal only (ruling 5).
- Verify: V-PY.

### P10: TS lock entry in skeleton .gitignore; update B-017 tests and usage guide
- Priority high. Depends: P1, P2, P3. Files: cli/src/ai_team/init/sources/project/.gitignore, scaffolds/project/.gitignore (generated), cli/tests/test_init_scaffolds.py, test_init.py, test_usage_guide.py, cli/docs/usage.md. Size note: over guideline, SC-6 binds them, one-line edits.
- Scope: choose the TS lock path inside the artifact dir, distinct from .ai-team.lock, entry matching file or directory; add to skeleton .gitignore; V-SYNC; update B-017 tests and usage.md (entry reserved for the pi package lock); regenerate command docs. P32 consumes the path. Out of scope: TS lock implementation, Python flock (unchanged).
- AC-1 skeleton .gitignore has both entries (SC-6, ADR-003). AC-2 V-SYNC gives identical scaffolds/project/.gitignore. AC-3 B-017 tests assert both entries. AC-4 usage.md documents the TS entry. AC-5 V-DOCS no unintended diff (SC-6).
- Verify: V-SYNC; V-PY; V-DOCS.

### P11: Parity fixture format and Python fixture runner
- Priority high. Depends: P4, P5, P6, P7, P8, P9, P10. Files: fixtures/parity/README.md, fixtures/parity/.gitattributes, cli/tests/test_parity_fixtures.py (+ optional support module), cli/scripts/seed_parity_fixture.py, fixtures/parity/status--empty/
- Scope: README defines one directory per case named <command-slug>--<case>, holding command and input (tool-contract field names), clock and version, expected exit status and structured result (errors compared on message only), before and after trees. Trees must survive git (empty dirs, nested .gitignore, names like .ai-team.lock, exact bytes/line endings): recommend a serialized tree manifest per side plus .gitattributes -text. Only absolute root paths normalised. [G2 ruling 1] Lock-sentinel scoping: exactly two literal paths, <project_dir>/.ai-team.lock and the P10 TS lock path (file or directory subtree), no globs, are excluded from the after-tree comparison only; the list is defined once in a machine-readable file under fixtures/parity/ that both runners load, and the README records the reasoning (tree scoping, not normalisation; SC-5, ADR-003). Before-trees may contain .ai-team.lock. The project .gitignore listing both paths is still compared byte for byte. [G2 ruling 2] Serialized tree format is required (the root .gitignore ignores .claude, .codex, .pi and .ai-team.toml at any depth). [G2 B6] Isolation rules for both runners, recorded in the README: unset AI_TEAM_ROOT unless the case sets it; materialise trees outside any git work tree and set GIT_CEILING_DIRECTORIES to the tmp parent; not-found cases are recorded through explicit root or AI_TEAM_ROOT only, so messages contain only the root path. Runner auto-discovers cases (no index), materialises before tree in tmp, sets overrides, dispatches to P5–P9 handlers, compares tree/status/result. Seed helper records a new case from Python and refuses to overwrite (ADR-004). One smoke case: status on an empty project. Out of scope: bulk cases (P12–P16), TS runner (P35).
- AC-1 README defines fields, tree encoding, normalisation, the two-path lock scoping with its reasoning, and the isolation rules (Component 5, ADR-004, ruling 1). [G2]
- AC-6 the lock-scoping list lives in one machine-readable file that the Python runner loads (and the TS runner will load). [G2 ruling 1]
- AC-7 cases run with AI_TEAM_ROOT unset unless set by the case, outside any git work tree, with GIT_CEILING_DIRECTORIES set. [G2 B6] AC-2 new case discovered without registration. AC-3 tree/status/message mismatch fails with diff (SC-5). AC-4 seed helper refuses existing case. AC-5 clock and version set only via P4 overrides.
- Verify: V-PY.

### P12: Seed fixtures for artifact-creation commands
- Priority high. Depends: P11. Files: case dirs spec-new--, task-new--, bug-new--, adr-new--, change-request-new--
- Scope: spec new (every status, author); task new (every priority, assignedRole, spec); bug new (every severity, task); adr new (every status, supersedes); change-request new; Unicode/punctuation titles; a long title exercising YAML folding; ID gaps and archived/completed-only IDs; artifact-exists errors where reachable. [G2 ruling 1c] One task-new case whose before-tree contains .ai-team.lock (pins ADR-003: TS is not blocked by the Python sentinel).
- AC-1 every creation command has a case (SC-3). AC-2 every enum value appears (SC-3). AC-3 Unicode/punctuation, folding title, ID gaps, archived IDs (SC-4). AC-4 Python runner passes (SC-5).
- Verify: V-PY.

### P13: Seed fixtures for lifecycle transitions
- Priority high. Depends: P11. Files: case dirs task-start--, task-complete--, task-block--, task-unblock--, bug-start--, bug-resolve--
- Scope: every valid transition; already-in-destination; not found; every invalid transition from each command's source-state set; task block with reason appends a work-log entry on the fixed clock.
- AC-1 each lifecycle command has a valid case (SC-3). AC-2 every invalid source state has a case (SC-4). AC-3 already-in-destination and not-found. AC-4 Python runner passes (SC-5).
- Verify: V-PY.

### P14: Seed fixtures for list, show, status, report
- Priority high. Depends: P11. Files: case dirs list-*--, show--, status--, report--
- Scope: list tasks/bugs/specs/adrs with every state value plus no filter; list change-requests; show per artifact kind plus unknown id; status on a populated project; report default and with out.
- AC-1 each leaf command has a case (SC-3). AC-2 every list state value appears (SC-3). AC-3 Python runner passes (SC-5).
- Verify: V-PY.

### P15: Seed fixtures for validate and archive
- Priority high. Depends: P11. Files: case dirs validate--, archive--
- Scope: validate each flag alone, combined, all, none; malformed frontmatter (missing fence, missing required key, invalid ID pattern); archive various olderThan values and dryRun; archive age boundary (one day before, on, one day after the cut-off, fixed clock).
- AC-1 every flag covered (SC-3). AC-2 malformed frontmatter (SC-4). AC-3 age boundary both sides and at cut-off (SC-4). AC-4 Python runner passes (SC-5).
- Verify: V-PY.

### P16: Seed fixtures for check-layout and init, incl. init→check-layout chain
- Priority high. Depends: P11, P10. Files: case dirs check-layout--, init--
- Scope: check-layout clean tree; broken tree (missing dirs, bad .ai-team.toml, placeholder root guidance, version mismatch); root not found (the case sets AI_TEAM_ROOT, because check-layout's resolver walks up past the tmp dir and GIT_CEILING_DIRECTORIES doesn't stop it) [G2 R4]; tools = ["claude","codex"] with only the needed scaffold dirs. init with/without createRootGuidance, force, dryRun, path; all with empty tool list. SC-8 chain: each init after tree reused as a check-layout before tree expecting zero findings. Init fixtures never include .claude/.codex content. Out of scope: cross-implementation run (P43).
- AC-1 every tool-contract field covered (SC-3). AC-2 broken tree and init with/without guidance (SC-4). AC-3 chained check-layout expects zero findings (SC-8). AC-4 init after trees contain the P10 .gitignore entry (SC-6). AC-5 Python runner passes (SC-5).
- Verify: V-PY.

## Phase 2: command map, sync pi target, skill conversion, pi skeleton

### P17: Command map plus agreement test against the Typer CLI
- Priority high. Depends: P1, P2, P3. Files: new command-map source under cli/src/ai_team/init/sources/, new cli/tests/test_command_map.py
- Scope: single map (hand-authored or generated from Typer; choice recorded in Work Log) listing per leaf command positionals, flags incl. --json, defaults, allowed values, camelCase tool-field names; CLI-only options (--json, init --tools, --no-interactive) have no tool field; no version. Test fails on any disagreement with Typer.
- AC-1 every tool-contract leaf command with fields (ADR-004). AC-2 disagreement fails the test. AC-3 no version string (ADR-004). AC-4 CLI-only options marked with no tool field.
- Verify: V-PY.

### P18: Fixture coverage test for commands and enum values
- Priority medium. Depends: P12, P13, P14, P15, P16, P17. Files: new cli/tests/test_parity_fixture_coverage.py
- Scope: loads the command map and every case; every leaf command has a case; every enum value appears; each case's input fields exist for its command.
- AC-1 missing command fails naming it (SC-3). AC-2 missing enum value fails naming it (SC-3). AC-3 undefined field fails.
- Verify: V-PY.

### P19: Marker parsing and claude/codex rendering in the sync
- Priority high. Depends: P17, P10 [G2 B1]. Files: cli/scripts/sync_init_scaffolds.py, new marker module in cli/scripts/, new cli/tests/test_skill_markers.py, cli/tests/test_init_scaffolds.py [G2 B1]
- Scope: parse three marker kinds against the command map; reject unknown prefixes, unparseable content, flags undefined for the command; claude/codex render verbatim in bodies and [claude]/[codex] headers; wire into sync; test with synthetic bodies. [G2 B1] Update the fake-repo setup in test_init_scaffolds.py (it copies only the sync script, ~lines 171-175) to also copy the marker module and a minimal command map. Out of scope: pi rendering (P21), skill source edits.
- AC-1 claude/codex render verbatim (marker contract). AC-2 unknown kind/unparseable fails naming file and marker (SC-10). AC-3 header markers rendered per target. AC-4 unchanged sources pass V-GOLD (SC-2).
- Verify: V-SYNC; V-GOLD; V-PY.

### P20: Move raw-body/raw-header test assertions to rendered output
- Priority high. Depends: P19, P10. Files: affected cli/tests/test_*.py and a new shared helper. Size note: over guideline, mechanical.
- Scope: tests reading body.md or raw [claude]/[codex] headers assert on rendered output via a helper calling the P19 renderer. Known: test_t063, t064, t066, t068, t074, t076, test_status_report_invocation, test_bug_evidence_chain, test_b016, test_init_scaffolds (confirm by grep). Out of scope: changing what is asserted.
- AC-1 no test reads body.md/raw headers for content (SC-2). AC-2 same expectations on rendered output. AC-3 V-PY passes.
- Verify: V-PY; review that no remaining test asserts on real source body.md or header content (fixture writes and source-structure checks in test_init_scaffolds.py, ~lines 41-66 and 359-389, are legitimate). [G2 N5]

### P21: Pi marker rendering and derived pi headers
- Priority high. Depends: P19. Files: marker module in cli/scripts/, new cli/tests/test_skill_markers_pi.py
- Scope: call form (all required positionals, or none required) renders ai_team tool-call instruction with input object, --json dropped; mention form renders "the `ai_team` tool's `<cmd>` command"; flag renders "set `<field>`" or bare field inside backticks; noun renders pi text; markers-only fence becomes prose, mixed fence fails; placeholders checked for field name/presence only; pi header from [claude] name/description with noun markers' pi text (ADR-002). Out of scope: writing pi/resources (P22).
- AC-1 call vs mention form correct, no --json (marker contract). AC-2 mixed fence fails. AC-3 flag inside backticks renders bare field, no nested span. AC-4 pi header from [claude] name/description only (ADR-002). AC-5 undefined placeholder field fails.
- Verify: V-PY.

### P22: Pi target in the sync; generate pi/resources/
- Priority high. Depends: P21, P10, P20 [G2 B1], P3 [G2 N2]. Files: cli/scripts/sync_init_scaffolds.py, pi/.gitignore, pi/resources/** (generated), new cli/tests/test_sync_pi_target.py, cli/tests/test_init_scaffolds.py [G2 B1], possibly cli/pyproject.toml, cli/uv.lock, CLAUDE.md and cli/docs/usage.md [G2 N2]
- Scope: write pi/resources/skills/<name>/SKILL.md for every skill (incl. orchestrators); pi/resources/skill-calls/<name>.json (call-form inputs for P46); artifact templates, project skeleton (incl. .gitignore and leaf dirs), root guidance templates; claude/codex scaffold dir list for check-layout Level 1; copy of command map; git-ignored version file (pi/.gitignore) computed from the source tree via hatch-vcs, not installed metadata; fail if undeterminable. Claude/codex output unchanged. [G2 B1] The fake-repo tests in test_init_scaffolds.py set the version override (or SETUPTOOLS_SCM_PRETEND_VERSION) and one test asserts the "cannot determine version" failure. [G2 N2] The sync still runs under bare `python`: either compute the version without new imports (for example a subprocess to hatch), or switch the documented command to `uv run python scripts/sync_init_scaffolds.py` and update CLAUDE.md's Build section and cli/docs/usage.md's maintainer section accordingly. Out of scope: package.json, TS code, skill conversions.
- AC-1 V-SYNC produces all listed outputs (Component 2). AC-2 version file git-ignored and equal to source-tree hatch-vcs version (Config, ADR-004). AC-3 undeterminable version fails with clear message, asserted by a test (B1). AC-4 two syncs leave no committed diff; V-GOLD passes (SC-2). AC-5 the version equals what hatch/setuptools-scm reports with cli/pyproject.toml's raw-options (root "..", tag_regex). [G2 N2]
- Verify: V-SYNC twice; git status --porcelain pi/ cli/src (empty after commit); V-GOLD; V-PY.

### P23: Pi package skeleton
- Priority high. Depends: P22, P3. Files: pi/package.json, pi/package-lock.json, pi/tsconfig.json, pi vitest config, pi/src/index.ts, pi/README.md, pi/.gitignore (add node_modules/) [G2 N4], pi/test/imports.test.ts [G2 N4]. Size note: boilerplate for a new package.
- Scope: pi manifest with extension entry and every generated skill except dev-loop, bug-loop, integrate; minimum Node; pi host peer deps with minimum 0.87.1; typecheck and test scripts per CLAUDE.md; full Phase 3/4 runtime dependency set settled here (round-tripping YAML, TOML parser, slug transliteration, pi's schema library) so later tasks run in parallel; strict tsconfig; vitest config; stub index.ts; README (dev setup, one-time sync, scratch PI_CODING_AGENT_DIR, mixed concurrency unsupported). Out of scope: core logic, tool registration.
- AC-1 manifest lists every non-orchestrator skill and no orchestrator (SC-10). AC-2 min Node and pi peer ≥0.87.1 (Config). AC-3 V-PI after V-SYNC on clean checkout: zero type errors, tests pass (SC-9). AC-4 README documents scratch dir, sync prerequisite, mixed concurrency unsupported (SC-7). AC-5 only entry and adapter import the pi API, enforced by a pi/test guard that fails on any pi import under pi/src/core. [G2 N4] AC-6 the package scripts are named exactly `typecheck` and `test`, matching CLAUDE.md (ruling 4).
- Verify: V-SYNC; V-PI.

### P24: Convert new-task, new-spec, new-bug to markers
- Priority high. Depends: P20, P22. Files: sources/skills/{new-task,new-spec,new-bug}/{body.md,metadata.toml}, their generated pi skills and skill-calls, new cli/tests/test_render_create_skills.py [G2 N6]
- Scope: replace every CLI reference in bodies and "via the ai-team CLI" in [claude]/[codex] headers with the right marker kind; noun marker claude/codex text reproduces each site exactly; V-SYNC.
- AC-1 every reference uses a marker. AC-2 V-GOLD passes (SC-2). AC-3 pi SKILL.md has no lowercase ai-team (SC-10). AC-4 new-task renders task new as call form with title and priority.
- Verify: V-SYNC; V-GOLD; grep ai-team in the three pi skills (none); V-PY.

### P25: Convert new-adr and change-request to markers
- Priority high. Depends: P20, P22. Files: sources/skills/{new-adr,change-request}/{body.md,metadata.toml}, generated pi output, new cli/tests/test_render_adr_cr_skills.py [G2 N6]
- Scope: as P24; plus the Phase 2 render assertion for the new-adr --supersedes site (bare `supersedes` inside backticks for pi, unchanged for claude/codex).
- AC-1 every reference uses a marker. AC-2 V-GOLD (SC-2). AC-3 supersedes as bare field, no nested span (Inline context). AC-4 shortened adr new --json intros render as mention form. AC-5 no lowercase ai-team in pi output (SC-10).
- Verify: V-SYNC; V-GOLD; grep guard; V-PY.

### P26: Convert remaining skills with CLI references
- Priority high. Depends: P20, P22. Files: sources/skills/{status-report,dev-loop,bug-loop}/{body.md,metadata.toml} and generated pi output (grep confirms exactly these three) [G2 N6]
- Scope: as P24 for status-report, dev-loop and bug-loop; orchestrators converted even though not shipped. Out of scope: manifest.
- AC-1 no ai-team token outside a marker in any skill source. AC-2 V-GOLD (SC-2). AC-3 no lowercase ai-team under pi/resources/skills (SC-10).
- Verify: V-SYNC; V-GOLD; grep -rn ai-team pi/resources/skills (none); V-PY.

### P27: Record the Phase 2 scaffold golden comparison
- Priority high. Depends: P24, P25, P26, P23 [G2 N7]. Files: none (Work Log only)
- Scope: clean checkout with all Phase 2 merged: V-SYNC, V-GOLD against merge-base with main, no unrendered {{ in generated files; record commands and output. One-time migration gate (SC-2). If it fails, fix the owning source.
- AC-1 V-GOLD no diff (SC-2). AC-2 no {{ under scaffolds/ or pi/resources/. AC-3 Work Log records commands, results and the merge-base commit hash; any unrelated skill edit landing on the base branch before P27 invalidates the gate and must be reconciled (SC-2). [G2 N7]
- Verify: V-SYNC; V-GOLD; grep -rn "{{" scaffolds and pi/resources (none); V-PY.

## Phase 3: TS core, TS lock, TS runner (no pi API imports; nobody edits pi/package.json)

### P28: TS result types, runtime clock/version, template loader
- Priority high. Depends: P23, P4. Files: pi/src/core/{result,runtime,templates}.ts, tests, pi/README.md
- Scope: result/error types with separate message and hint (mirror P5); runtime reads the same clock/version override names as P4 in one place, else the generated version file; missing file raises "run the sync"; template loader reads pi/resources/templates; record variable names in README.
- AC-1 same override names as Python (Config). AC-2 missing version file → error telling user to run the sync. AC-3 loader returns bytes identical to cli/src/ai_team/templates. AC-4 V-PI passes (SC-9).
- Verify: V-SYNC; V-PI.

### P29: Port frontmatter models and byte-identical YAML dump
- Priority high. Depends: P23, P12 [G2 B2]. Files: pi/src/core/{models,frontmatter}.ts, tests
- Scope: port core/models.py parse/dump for all five artifact kinds with the same required-field and FrontmatterError messages; dump byte-identical to ruamel round-trip (key order, quoting, Unicode, folding width); pin with golden strings from P12 after trees.
- AC-1 the dump of every artifact in the P12 after-trees equals the fixture bytes (SC-5). [G2 B2] AC-2 malformed/missing-key errors equal Python messages. AC-3 same folding width. AC-4 V-PI passes (SC-9).
- Verify: V-PI.

### P30: Port filesystem layer and slug generation
- Priority high. Depends: P29, P12 [G2 B2]. Files: pi/src/core/{fs,slug}.ts, tests
- Scope: port core/fs.py (read, atomic write, move, update status, ArtifactExists/ArtifactNotFound messages) and python-slugify-equivalent slugs incl. transliteration; test slugs against every P12 title.
- AC-1 slugs equal fixture filenames (SC-5). AC-2 atomic writes. AC-3 existing destination error equals Python's. AC-4 V-PI passes (SC-9).
- Verify: V-PI.

### P31: Port the project root locator
- Priority high. Depends: P28, P5 [G2 B5]. Files: pi/src/core/locator.ts, tests
- Scope: explicit root → AI_TEAM_ROOT → .ai-team.toml [project] dir → default project folder, from a caller-provided directory, never process cwd; ProjectRoot paths; not-found keeps core message with hint separate. Out of scope: hint rewriting (P45).
- AC-1 same resolution order (Config). AC-2 start dir is a parameter, never process cwd. AC-3 not-found message equals Python's. AC-4 V-PI passes (SC-9).
- Verify: V-PI; grep process.cwd in pi/src/core (none).

### P32: Port ID allocation and implement the TS lock
- Priority critical. Depends: P29, P31, P10, P12 [G2 B2]. Files: pi/src/core/{ids,lock}.ts, tests, test helper under pi/test/
- Scope: port core/ids.py (all kinds, archived IDs, spec IDs from frontmatter); lock at the P10 path with create-under-lock semantics: atomic acquisition, holder liveness check, reclaim of dead holder, same bounded wait and core timeout message as core/lock.py; test with two concurrent Node processes ≥50 repetitions and a holder killed mid-allocation. Out of scope: Python locking (ADR-003).
- AC-1 no duplicate ID across ≥50 concurrent repetitions (SC-7). AC-2 killed holder doesn't block beyond bounded wait (SC-7). AC-3 timeout message uses the same template as Python's, with the TS lock path (core/lock.py:96-99 embeds the path). [G2 N3] AC-4 never touches .ai-team.lock (ADR-003). AC-5 next IDs match P12 gap/archived cases.
- Notes: [G2 N11] the vitest config has one owner (P35); the ≥50-repetition concurrency test uses per-test timeouts instead of editing the config.
- Verify: V-PI.

### P33: Port the validation core
- Priority high. Depends: P30, P31, P15 [G2 B2]. Files: pi/src/core/validate.ts, tests
- Scope: port core/validate.py with identical finding codes, messages, relative paths, ordering. Out of scope: validate command (P41).
- AC-1 same findings in same order for every P15 tree (SC-5). AC-2 malformed frontmatter same code and message. AC-3 V-PI passes (SC-9).
- Verify: V-PI.

### P34: Port the layout-diagnostics core
- Priority high. Depends: P33, P28, P22, P16 [G2 B2]. Files: pi/src/core/layout.ts, tests
- Scope: port core/layout.py Levels 1–4; reads scaffold dir list and root-guidance starter sections from pi/resources and version from P28 runtime; suggested fixes a separate field.
- AC-1 same findings as Python for every P16 check-layout tree (SC-5). AC-2 checks directories from the generated scaffold list when tools list claude/codex (S-003 Level 1). AC-3 suggested fix separate. AC-4 V-PI passes (SC-9).
- Verify: V-SYNC; V-PI.

### P35: TS parity runner, command registry, handler stubs
- Priority high. Depends: P11, P28, P31, P23. Files: pi/test/parity.test.ts, pi/src/core/commands/registry.ts, 13 stub modules under pi/src/core/commands/ (spec, adr, change-request, task, bug, list, show, status, report, validate, archive, check-layout, init); vitest config may be touched. Size note: trivial stubs; removes shared-file conflicts for P36–P42.
- Scope: vitest runner auto-discovers fixtures/parity cases with the P11 rules (loads the shared lock-scoping list, applies the isolation rules, normalises only root paths); resolves root, sets overrides, compares tree/status/message; registry maps every tool-contract command to a handler module; stubs throw "not implemented"; later tasks edit only their module; filter by name prefix. [G2 B4] Cases whose command resolves to a stub are reported as skipped/todo, so `npm test` stays green. [G2 B7] Handler interface: `init` takes the start directory (plus `path`); `check-layout` takes the start directory and resolves its own root (port of check_layout.py `_repository_root`); every other handler takes a located ProjectRoot.
- AC-1 new case discovered without registration (ADR-004). AC-2 registry maps every command to exactly one handler (SC-11 groundwork). AC-3 mismatch fails with diff (SC-5). AC-4 V-PI passes; V-PI-F status-- reports the smoke case as pending (stub). [G2 B4] AC-5 the registry's handler signatures follow the init / check-layout / located-root split. [G2 B7]
- Verify: V-PI; V-PI-F status-- to confirm discovery.

### P36: TS spec new, adr new, change-request new handlers
- Priority high. Depends: P35, P30, P32, P12. Files: pi/src/core/commands/{spec,adr,change-request}.ts, optional tests
- Notes: [G2 N9] Python adr new and change-request new take no lock; the TS lock there is allowed by ADR-003 and fixtures are unaffected thanks to the lock-path scoping.
- AC-1 V-PI-F spec-new--, adr-new--, change-request-new-- pass (SC-5). AC-2 IDs allocated only under the TS lock (SC-7). AC-3 zero type errors (SC-9).
- Verify: V-PI-F per prefix; full V-PI. [G2 B4]

### P37: TS task handlers
- Priority high. Depends: P35, P30, P32, P12, P13. Files: pi/src/core/commands/task.ts, optional tests
- Scope: task new, start, complete, block (work-log append with P28 clock), unblock.
- AC-1 V-PI-F task- passes (SC-5). AC-2 invalid transition errors equal fixtures (SC-4). AC-3 zero type errors (SC-9).
- Verify: V-PI-F task-; full V-PI. [G2 B4]

### P38: TS bug handlers
- Priority high. Depends: P35, P30, P32, P12, P13. Files: pi/src/core/commands/bug.ts, optional tests
- Scope: bug new, start, resolve.
- AC-1 V-PI-F bug- passes (SC-5). AC-2 invalid transition errors equal fixtures (SC-4). AC-3 zero type errors (SC-9).
- Verify: V-PI-F bug-; full V-PI. [G2 B4]

### P39: TS list, show, status handlers
- Priority high. Depends: P35, P30, P14. Files: pi/src/core/commands/{list,show,status}.ts, a unit test for the git lookup
- Scope: [G2 B6] port the latest-integration-result git lookup including the "not found" fallback, with a unit test for the found branch in a temporary git repo (allowed: it is not the Python CLI, ADR-004 Alternative C). status.ts exports the payload builder that report reuses.
- AC-1 V-PI-F list-, show--, status-- pass (SC-5). AC-2 show unknown id returns fixture message. AC-3 zero type errors (SC-9).
- Verify: V-PI-F per prefix; full V-PI. [G2 B4]

### P40: TS report handler
- Priority high. Depends: P35, P30, P14, P39 [G2 B3]. Files: pi/src/core/commands/report.ts
- Scope: port commands/report.py (content, default path, out) using P28 clock. [G2 B3] Import the status payload from status.ts (owned by P39); do not edit status.ts. [G2 N12] `out` resolves against the handler's start directory, never process.cwd().
- AC-1 V-PI-F report-- passes, report file byte-identical (SC-5). AC-2 out writes to that path. AC-3 zero type errors (SC-9).
- Verify: V-PI-F report--; full V-PI. [G2 B4]

### P41: TS validate and archive handlers
- Priority high. Depends: P35, P33, P30, P15. Files: pi/src/core/commands/{validate,archive}.ts
- Scope: validate with combinable flags on P33; archive with olderThan and dryRun on the P28 clock.
- AC-1 V-PI-F validate--, archive-- pass (SC-5). AC-2 age boundary exactly as fixtures (SC-4). AC-3 dryRun changes nothing. AC-4 zero type errors (SC-9).
- Verify: V-PI-F per prefix; full V-PI. [G2 B4]

### P42: TS check-layout and init handlers
- Priority high. Depends: P35, P34, P30, P16, P22. Files: pi/src/core/commands/{check-layout,init}.ts
- Scope: check-layout on P34, porting check_layout.py `_repository_root` (AI_TEAM_ROOT, else walk up for .ai-team.toml or project/, else the start directory; never fails not-found) [G2 B7]; init (path, force, dryRun, createRootGuidance), always non-interactive, writes project skeleton from pi/resources plus .ai-team.toml with empty [init].tools and runtime version, root guidance only when asked, never the declined note, never .claude/.codex. Out of scope: hint rewriting.
- AC-1 V-PI-F check-layout--, init-- pass (SC-5). AC-2 init writes empty tools and runtime framework_version (Tool contract). AC-3 check-layout on init output has zero findings (SC-8). AC-4 zero type errors (SC-9).
- Verify: V-SYNC; V-PI-F per prefix; full V-PI. [G2 B4]

### P43: Full parity suite and recorded SC-8 cross-implementation check
- Priority critical. Depends: P36, P37, P38, P39, P40, P41, P42, P18. Files: pi/test/parity.test.ts, pi/test/imports.test.ts (process.cwd guard) [G2 R3], possibly pi/src/core/commands/registry.ts (removing stub support)
- Scope: runner fails if any case resolves to a stub; full suite under both runners; [G2 N8] before the cross runs, on a clean tree reinstall the editable package (`uv sync --reinstall-package ai-team`) and record both version strings; [G2 N12] add a permanent guard test: no process.cwd under pi/src/core; from the same checkout record in the Work Log that a pi-init project passes Python check-layout with zero findings, and Python-init projects (no tools; claude,codex) pass TS check-layout with zero findings. Recorded, not a permanent test (TS tests must not shell out to Python, ADR-004 Alternative C).
- AC-1 every case passes under both runners, none skipped (SC-5). AC-2 stub-resolved case fails the TS runner (SC-11 groundwork). AC-3 Work Log records both cross runs with zero findings (SC-8). AC-4 zero type errors (SC-9).
- Verify: V-SYNC; V-PY; V-PI.

## Phase 4: adapter, guards, CI, smoke test

### P44: ai_team tool schema from the command map; handler-mapping test
- Priority high. Depends: P43, P22. Files: pi/src/adapter/schema.ts, pi/test/schema.test.ts
- Scope: union discriminated on command from pi/resources command map; one variant per leaf command; camelCase fields, defaults and enums from the map; no json field; init has no tools/noInteractive; SC-11 tests (variant↔handler both ways) and map agreement.
- AC-1 exactly one variant per leaf command (Tool contract). AC-2 variant without handler or handler without variant fails (SC-11). AC-3 no json, no init tools/noInteractive. AC-4 V-PI passes (SC-9).
- Verify: V-SYNC; V-PI.

### P45: ai_team tool adapter
- Priority high. Depends: P44. Files: pi/src/index.ts, pi/src/adapter/{tool,hints}.ts, pi/test/adapter.test.ts
- Scope: register ai_team; validate input with P44; resolve root from session cwd via P31 only for commands that need a located root (init and check-layout get the session cwd as their start directory) [G2 B7]; dispatch to registry; 1–3 line summary plus structured result as details; domain errors → tool errors with message plus rewritten hint (binary hints like "Run 'ai-team init'" and check-layout suggested fixes become tool instructions); unexpected exceptions → one-line error, no stack; never the dev warning; missing version file → tool fails to load with sync message; tested with a fake pi API, without starting pi.
- AC-1 summary 1–3 lines plus structured details (Tool contract). AC-2 root from session cwd, never process cwd (Config). AC-3 binary hints/suggested fixes rewritten (Tool contract). AC-4 unexpected exception → one-line error, no stack. AC-5 missing version file → load failure with sync message. AC-6 init and check-layout succeed from a directory with no project/. [G2 B7]
- Verify: V-SYNC; V-PI.

### P46: Rendered-skill schema check, binary guard, manifest check
- Priority high. Depends: P44, P27. Files: pi/test/rendered-skills.test.ts
- Scope: every entry in pi/resources/skill-calls/*.json validates against the P44 schema (placeholders by field name/presence) and appears in its rendered SKILL.md; no lowercase ai-team token (case-sensitive) under pi/resources/skills/; manifest skill list equals generated skills minus dev-loop, bug-loop, integrate. Out of scope: marker rejection (P19, P21).
- AC-1 invalid call snippet fails naming the skill (SC-10). AC-2 ai-team token fails naming file and line (SC-10). AC-3 orchestrator included or non-orchestrator missing fails (SC-10). AC-4 V-PI passes (SC-9).
- Verify: V-SYNC; V-PI.

### P47: Pi package checks in CI
- Priority medium. Depends: P45, P46. Files: .github/workflows/ci.yml
- Scope: new job: Python and uv, V-SYNC (existing SETUPTOOLS_SCM_PRETEND_VERSION pattern acceptable); fail if `git diff --exit-code -- cli/src/ai_team/init/scaffolds pi/resources`; Node at manifest minimum or higher; npm ci, npm run typecheck, npm test in pi/; existing jobs unchanged. Out of scope: npm publishing.
- AC-1 PRs run pi typecheck and tests after a fresh sync (SC-13). AC-2 sync changing a committed generated file fails the job. AC-3 existing lint/test/release jobs unchanged.
- Verify: locally V-SYNC, git diff --exit-code on generated trees, V-PI, V-PY; then confirm the PR run and record it in the Work Log.

### P48: Manual pi smoke test
- Priority medium. Depends: P45, P46. Files: pi/README.md
- Scope: pi ≥0.87.1 with scratch PI_CODING_AGENT_DIR; V-SYNC; `pi install <repo>/pi`; session in a scratch project, init via the tool; ask the agent to create a task via the new-task skill; confirm T-001 via the ai_team tool and no shell call to ai-team in the session log; record in Work Log; add a "Manual smoke test" section to pi/README.md. Needs pi installed locally. [G2 N10] Manual / human-assisted task: if pi ≥0.87.1 is unavailable the developer returns BLOCKED, never a simulated result. Out of scope: automation.
- AC-1 T-001 via ai_team with no shell call to ai-team (SC-12). AC-2 scratch PI_CODING_AGENT_DIR only (Config). AC-3 Work Log records pi version, steps, evidence (SC-12). AC-4 README documents the procedure.
- Verify: manual steps; V-PI; V-PY.

## SC coverage

| SC | Tasks |
|---|---|
| SC-1 | P1, P2, P3 |
| SC-2 | P19, P20, P22, P24, P25, P26, P27 |
| SC-3 | P12–P16, P18 |
| SC-4 | P12, P13, P15, P16, P18 |
| SC-5 | P11, P12–P16, P29, P30, P33, P34, P35, P36–P42, P43 |
| SC-6 | P4–P10 |
| SC-7 | P32, P23, P3, P2 |
| SC-8 | P16, P42, P43 |
| SC-9 | P23, P28–P46 |
| SC-10 | P19, P21, P22, P23, P24, P25, P26, P46 |
| SC-11 | P35, P43, P44 |
| SC-12 | P48 |
| SC-13 | all via V-PY/V-PI; P3, P47 |

Contract clauses: no json field P44; summary + details P45; init pi semantics P9, P42, P44; message/hint separate P5–P9, P28; hint rewrite P45; no dev warning P45; command map single place P17, P44; clock/version overrides P4, P28; version file P22, P28, P45; root resolution P31, P45; TS lock location P10, P32; PI_CODING_AGENT_DIR P23, P48; runtime versions P23.

## Dependency summary

- P1, P2, P3: none
- P4: P1–P3. P5: P4. P6, P7, P8, P9: P5. P10: P1–P3.
- P11: P4–P10. P12–P15: P11. P16: P11, P10.
- P17: P1–P3. P18: P12–P17. P19: P17, P10. P20: P19, P10. P21: P19. P22: P21, P10, P20, P3. P23: P22, P3.
- P24, P25, P26: P20, P22. P27: P24–P26, P23.
- P28: P23, P4. P29: P23, P12. P30: P29, P12. P31: P28, P5. P32: P29, P31, P10, P12. P33: P30, P31, P15. P34: P33, P28, P22, P16.
- P35: P11, P28, P31, P23.
- P36: P35, P30, P32, P12. P37, P38: P35, P30, P32, P12, P13. P39: P35, P30, P14. P40: P35, P30, P14, P39. P41: P35, P33, P30, P15. P42: P35, P34, P30, P16, P22.
- P43: P36–P42, P18. P44: P43, P22. P45: P44. P46: P44, P27. P47, P48: P45, P46.

Parallel sets: {P1,P2,P3}; {P4,P10,P17}; {P6,P7,P8,P9}; {P12..P16}; {P20,P21}; {P24,P25,P26}; {P28,P29}; {P30,P31}; {P36..P39, P41, P42} then P40 after P39; {P45,P46}; {P47,P48}.

## File-conflict risks

1. pi/package.json and package-lock.json: P23 settles all Phase 3/4 dependencies; P28–P46 must not edit them. A task needing a new dependency must be serialized or given a dependency edge. Main parallelism hotspot.
2. Python command modules: P4 touches all, so P5–P9 depend on P4; P5–P9 touch disjoint sets. core/layout.py touched by P4 and possibly P8 (P8 depends on P4).
3. cli/tests/test_init_scaffolds.py: P10, P19, P20, P22 — serialized P10 → P19 → P20 → P22. [G2 B1]
3a. cli/src/ai_team/core/locator.py: only P5. [G2 B5]
3b. status payload: status.ts owned by P39; P40 imports it and depends on P39. [G2 B3]
3c. CLAUDE.md: P3, then possibly P22 (depends on P3). [G2 N2]
4. Sync script and marker module: sequential P19 → P21 → P22. P20 changes only tests.
5. Generated trees: scaffolds/project/.gitignore only by P10; claude/codex scaffolds must not change (V-GOLD); pi/resources/project gets the P10 entry via P22 → P10; pi skills and skill-calls are per skill, and P24/P25/P26 cover disjoint sets (no shared calls index).
6. fixtures/parity/: P11 owns README and .gitattributes; P12–P16 disjoint prefixes; no index file.
7. TS registry and command modules: P35 creates all; P36–P42 edit only their own modules; only P43 touches the registry later. vitest config: only P35. [G2 N11]
8. pi/README.md: P23 → P28 → P48, ordered.
9. pi/src/index.ts: created by P23, changed only by P45.
10. cli/docs/: usage.md by P10, then possibly P22 (ordered) [G2 R2]; P4 writes a separate new note; commands.md only regenerated (P8, P10), expected no diff.
11. cli/pyproject.toml and uv.lock: only P22 (hatch-vcs dependency for the sync).

## Phase mapping

| Phase | Tasks |
|---|---|
| 0 | P1–P3 (ADRs already recorded) |
| 1 | P4–P16 |
| 2 | P17–P27 (P18 bridges 1 and 2) |
| 3 | P28–P43 |
| 4 | P44–P48 |

## Gate 2 rulings on the open points (Architect, round 1)

1. Lock-path exclusion is tree scoping compatible with SC-5; no change request. Conditions (a)–(d) are folded into P11 and P12.
2. Serialized tree format is required (P11).
3. YAML/slug byte-parity risk is accepted, with the B2 dependency edges.
4. `npm ci` / `npm run typecheck` / `npm test` are accepted (P3, P23 AC-6).
5. The P9 internal empty-tools init is accepted; it stays internal only (P9 AC-5).
6. SC-8 via the P16 chain plus the recorded P43 cross-run is accepted (with N8 folded into P43).
7. All oversized tasks (P4, P10, P11, P20, P22, P23, P35) are accepted without splits; P11 absorbs B6 and ruling 1, and P22 absorbs B1 and N2.
8. Implementation-chosen names (P4 env vars, P10 TS lock path) are accepted; each chooser records them in its Work Log and docs.

## Original open points (answered above)

1. Lock files in fixture trees: Python leaves .ai-team.lock permanently and the TS lock uses another path, so whole-tree byte comparison would always fail after any ID-allocating command. P11 excludes both lock paths from tree capture. SC-5 says "no normalisation beyond absolute root paths". Confirm this is tree scoping, not normalisation; otherwise a change request against S-005 is needed before P11.
2. Fixture trees must survive git (empty dirs dropped, nested .gitignore effective in the repo, fixture files named .ai-team.lock, line-ending rewriting). P11 requires a serialized tree format.
3. Byte-parity risk in P29 (ruamel YAML dump quoting and folding) and P30 (python-slugify transliteration); P12 pins both with long and Unicode titles.
4. Pi check command names (npm ci, npm run typecheck, npm test from pi/) are the Planner's proposal; P3 fixes them in CLAUDE.md and later verification depends on them.
5. Python needs an internal empty-tools init mode (P9) to seed pi-semantics init fixtures without changing the CLI surface; the declined note is excluded from the result.
6. SC-8 is covered by the P16 fixture chain plus the one-off cross-implementation run recorded in P43, because TS tests may not shell out to Python (ADR-004 Alternative C).
7. Tasks over the 3–4 file guideline: P4, P10, P11, P20, P22, P23 (and P35 with trivial stubs). All mechanical; splitting would create file conflicts. The Architect may still ask for splits.
8. Names chosen during implementation: P4 chooses the env var names, P10 the TS lock path, as the spec allows.
