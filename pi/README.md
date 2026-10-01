# ai-team pi package

The AI-team framework as a pi package. It will give a pi session an `ai_team`
tool and pi-rendered AI-team skills. This directory currently holds the package
skeleton only: the manifest, the TypeScript toolchain and a stub extension entry.

Requires Node 22.19 or newer and pi 0.87.1 or newer.

## Dev setup

`pi/resources/` is generated from the sources under `cli/src/ai_team/`. Never edit
it by hand. A fresh checkout needs a one-time sync before anything in this package
works, because the sync renders the resources and writes the git-ignored
`resources/version.txt` that the package reads at load time:

```bash
cd cli && python scripts/sync_init_scaffolds.py
```

`uv` must be on the PATH (the sync asks it for the version). Without git history,
set `SETUPTOOLS_SCM_PRETEND_VERSION`. Re-run the sync whenever the sources change.

Then, from `pi/`:

```bash
npm ci
npm run typecheck
npm test
```

## Manual smoke tests

Point pi at a scratch agent directory so your real pi configuration is never
touched:

```bash
export PI_CODING_AGENT_DIR="$(mktemp -d)"
pi install <path-to-pi>
```

Automated tests never start pi and never use your real agent directory.

## Runtime overrides

The core reads the same test-only overrides as the Python CLI, in one place
(`src/core/runtime.ts`):

| Variable | Effect |
|---|---|
| `AI_TEAM_TODAY` | ISO date (`YYYY-MM-DD`) used instead of the current date. |
| `AI_TEAM_FRAMEWORK_VERSION` | Version string used instead of `resources/version.txt`. |

Without an override the version comes from the generated `resources/version.txt`;
if that file is missing the core fails with a hint to run the sync.

## Architecture rule

Only `src/index.ts` and the pi adapter may import the pi API. Nothing under
`src/core/` may import it; `test/imports.test.ts` enforces this.

## Known limitation

Mixed concurrent allocation is unsupported. The TypeScript core and the Python
`ai-team` CLI each own their own ID-allocation lock, so running both at the same
time to create artifacts in the same project can produce duplicate IDs.
