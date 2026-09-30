# Runtime overrides (maintainers)

Test-only hooks for making CLI output deterministic. Not part of the
user-facing interface; do not document these in `usage.md`.

All reads live in `src/ai_team/core/runtime.py`. Commands and core modules call
`today()` and `framework_version()` from that module instead of
`date.today()` or `importlib.metadata.version("ai-team")`.

| Environment variable | Effect |
|---|---|
| `AI_TEAM_TODAY` | ISO date (`YYYY-MM-DD`) returned by `today()`. Drives created dates, Work Log session dates, the report date, and the archive cut-off. |
| `AI_TEAM_FRAMEWORK_VERSION` | String returned by `framework_version()`. Written to the marker as `framework_version` and used for layout version comparison. |

Behavior notes:

- With neither variable set, behavior is unchanged.
- An `AI_TEAM_TODAY` value that is not an ISO date raises `ValueError` naming
  the variable.
- `framework_version()` calls `importlib.metadata.version` at call time, so
  monkeypatching it in tests keeps working.
- `ai-team --version` in `cli.py` is intentionally exempt and reads the
  installed metadata directly.
