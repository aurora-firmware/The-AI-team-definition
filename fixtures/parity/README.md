# Parity fixtures

The shared behavioural contract for the Python CLI and the TypeScript core
(S-005 Component 5, ADR-004). Both runners auto-discover every case here; a diff
in any case fails both. Fixtures are seeded once from the Python CLI and are then
maintained as the source of truth. They are never regenerated from either
implementation. A behaviour change starts with a reviewed fixture change.

## Layout

```text
fixtures/parity/
  README.md
  .gitattributes          # `* -text`: bytes and line endings are never rewritten
  lock-sentinels.json     # the two lock paths excluded from after-tree comparison
  <command-slug>--<case>/
    case.json
    before.json
    after.json
```

A case is one directory named `<command-slug>--<case>`. The command slug is the
command with spaces replaced by `-` (`task new` becomes `task-new`); both parts use
lowercase letters, digits and single hyphens. A directory is a case when it holds a
`case.json`. There is no index: adding a directory adds a case.

## Case fields (`case.json`)

| Field | Required | Meaning |
|---|---|---|
| `command` | yes | Command path, space-separated, as in the `ai_team` tool contract (`task new`, `list tasks`, `check-layout`). |
| `input` | yes | Tool-contract fields for the command, using the tool's camelCase names (`assignedRole`, `olderThan`, `dryRun`). No `json` field. |
| `today` | yes | ISO date applied through the clock override (`AI_TEAM_TODAY`). |
| `version` | yes | Framework version applied through the version override (`AI_TEAM_FRAMEWORK_VERSION`). |
| `env` | no | Extra environment variables. `<ROOT>` in a value becomes the materialised root. |
| `project_dir` | no | Artifact folder name, default `project`. Used to resolve `<project_dir>` in the lock list. |
| `expected` | yes | Expected result: `status` (exit status), and `payload` (structured result) and/or `message` (errors). |

Clock and version are applied only through these two overrides; a case without
`today` or `version` is rejected. Remediation hints are not part of `expected`:
errors compare the message only (ADR-004).

`init` runs in the empty-tools mode. Its `path` field is relative to the root.

## Tree encoding (`before.json`, `after.json`)

Directory trees do not survive git (empty directories are dropped, the repository
`.gitignore` ignores `.claude`, `.codex`, `.pi` and `.ai-team.toml` at any depth, and
nested `.gitignore` files and `.ai-team.lock` would act on the repo itself). So each
side is a serialised manifest: a JSON list of entries sorted by `path`, one per
directory or file under the root (the root itself is not listed).

```json
{"path": "project", "type": "dir"}
{"path": "project/.gitignore", "type": "file", "text": "a\r\nb\n"}
{"path": "blob.bin", "type": "file", "base64": "//4A"}
```

Paths are POSIX and relative. `text` holds UTF-8 content with exact line endings
(JSON escapes keep `\r\n` intact); content that is not valid UTF-8 uses `base64`.
`.gitattributes` sets `-text` so git never rewrites line endings in the fixture
files. Symlinks are not supported. Absolute paths and `..` are rejected.

## Normalisation

Only the absolute root path is normalised: in the result (every string in `payload`
and `message`) and in file text, the materialised root is replaced with `<ROOT>`.
Nothing else is rewritten; dates and versions are fixed by the overrides instead.

## Lock-sentinel scoping

The project `.ai-team.lock` (Python, `flock`) and the TS core's lock are
implementation-private. Python never deletes its sentinel, and the TS lock is a
file or a directory. The two implementations therefore leave different leftovers
after the same command (ADR-003, SC-5).

Exactly two literal paths are excluded, and only from the after-tree comparison:

- `<project_dir>/.ai-team.lock`
- `<project_dir>/.ai-team-ts.lock` (the T-087 TS lock path; a file, or a directory
  and everything beneath it)

There are no globs: `project/sub/.ai-team.lock` is compared like any other file. The
list lives in one machine-readable file, `lock-sentinels.json`, which both runners
load. `<project_dir>` is replaced by the case's `project_dir`. This is tree
scoping, not normalisation: nothing is rewritten, and the paths are simply not
part of the compared tree. Before-trees may contain `.ai-team.lock`. The project
`.gitignore` that lists both paths is still compared byte for byte.

## Isolation rules (both runners)

- Unset `AI_TEAM_ROOT` unless the case sets it in `env`.
- Materialise the before-tree in a temporary directory outside any git work tree,
  and set `GIT_CEILING_DIRECTORIES` to the temporary parent so git never finds an
  enclosing repository.
- Not-found cases are recorded through an explicit root or `AI_TEAM_ROOT` only.
  The runner passes the materialised root explicitly unless the case sets
  `AI_TEAM_ROOT`. Messages then contain only the root path, as `<ROOT>`.
- Clock and version come only from the overrides above.

## Running and seeding

The Python runner is `cli/tests/test_parity_fixtures.py` (support code in
`cli/tests/parity_support.py`); run it with `uv run pytest` from `cli/`.

To record a new case from the Python CLI, from `cli/`:

```bash
uv run python scripts/seed_parity_fixture.py --command "task new" --case basic \
  --input '{"title": "Example"}' --before-tree path/to/tree \
  --today 2026-01-15 --version 1.0.0
```

The helper refuses to overwrite an existing case. Review the recorded files before
committing them; after that they are maintained by hand and never regenerated.
