"""Record a new parity fixture case from the Python implementation (ADR-004).

Cases are seeded once and then maintained by hand as the contract; this helper
refuses to overwrite an existing case and is never used to regenerate one.

Run from ``cli/``:

    uv run python scripts/seed_parity_fixture.py --command status --case empty \
        --before-tree path/to/tree --today 2026-01-15 --version 1.0.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLI_DIR))

from tests import parity_support  # noqa: E402


def _parse_env(pairs: list[str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for pair in pairs:
        name, separator, value = pair.partition("=")
        if not separator:
            raise SystemExit(f"--env expects NAME=VALUE, got {pair!r}")
        env[name] = value
    return env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--command", required=True, help="e.g. 'task new'")
    parser.add_argument("--case", required=True, help="case suffix after '--'")
    parser.add_argument("--input", default="{}", help="tool-contract fields as JSON")
    parser.add_argument("--before-tree", type=Path, help="directory to snapshot")
    parser.add_argument("--today", required=True, help="ISO date for AI_TEAM_TODAY")
    parser.add_argument("--version", required=True, help="framework version override")
    parser.add_argument("--env", action="append", default=[], metavar="NAME=VALUE")
    parser.add_argument("--project-dir", default="project")
    parser.add_argument(
        "--fixtures-root", type=Path, default=parity_support.FIXTURES_ROOT
    )
    args = parser.parse_args(argv)

    try:
        case_dir = parity_support.record_case(
            args.fixtures_root,
            command=args.command,
            case=args.case,
            input=json.loads(args.input),
            before_dir=args.before_tree,
            today=args.today,
            version=args.version,
            env=_parse_env(args.env),
            project_dir=args.project_dir,
        )
    except (FileExistsError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(case_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
