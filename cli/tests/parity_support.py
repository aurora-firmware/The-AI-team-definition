"""Shared machinery for the parity fixtures (S-005 Component 5, ADR-004).

Used by the pytest runner and by ``scripts/seed_parity_fixture.py``. The format
is documented in ``fixtures/parity/README.md``.
"""

from __future__ import annotations

import base64
import difflib
import json
import os
import re
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any

from ai_team.commands import adr, archive, bug, change_request, check_layout, init
from ai_team.commands import list as list_command
from ai_team.commands import report, show, spec, status, task, validate
from ai_team.core.locator import ProjectRoot, ProjectRootNotFound, find_project_root
from ai_team.core.result import Result
from ai_team.core.runtime import FRAMEWORK_VERSION_ENV_VAR, TODAY_ENV_VAR

FIXTURES_ROOT = Path(__file__).resolve().parents[2] / "fixtures" / "parity"
LOCK_SENTINELS_FILE = "lock-sentinels.json"
CASE_FILE = "case.json"
PROJECT_DIR_PLACEHOLDER = "<project_dir>"

ROOT_PLACEHOLDER = "<ROOT>"
ROOT_ENV_VAR = "AI_TEAM_ROOT"
GIT_CEILING_ENV_VAR = "GIT_CEILING_DIRECTORIES"
CASE_NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*--[a-z0-9]+(-[a-z0-9]+)*$")
REQUIRED_CASE_FIELDS = ("command", "input", "today", "version", "expected")

TreeEntry = dict[str, str]


def serialize_tree(root: Path) -> list[TreeEntry]:
    """Return a manifest of every directory and file under *root*, sorted by path."""
    entries: list[TreeEntry] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError(f"Symlinks are not supported in fixture trees: {path}")
        if path.is_dir():
            entries.append({"path": relative, "type": "dir"})
            continue
        data = path.read_bytes()
        try:
            entries.append({"path": relative, "type": "file", "text": data.decode()})
        except UnicodeDecodeError:
            encoded = base64.b64encode(data).decode("ascii")
            entries.append({"path": relative, "type": "file", "base64": encoded})
    return sorted(entries, key=lambda entry: entry["path"])


def _safe_destination(target: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        raise ValueError(f"Unsafe path in tree manifest: {relative}")
    return target.joinpath(*pure.parts)


def materialize_tree(manifest: list[TreeEntry], target: Path) -> None:
    """Create *target* and write every manifest entry under it, byte for byte."""
    target.mkdir(parents=True, exist_ok=True)
    for entry in manifest:
        destination = _safe_destination(target, entry["path"])
        if entry["type"] == "dir":
            destination.mkdir(parents=True, exist_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if "base64" in entry:
            destination.write_bytes(base64.b64decode(entry["base64"]))
        else:
            destination.write_bytes(entry["text"].encode())


def load_lock_exclusions(fixtures_root: Path) -> list[str]:
    """Return the after-tree lock paths from the machine-readable sentinel file."""
    data = json.loads((fixtures_root / LOCK_SENTINELS_FILE).read_text("utf-8"))
    return list(data["after_tree_excluded_paths"])


def exclude_lock_paths(
    manifest: list[TreeEntry], project_dir: str, exclusions: list[str]
) -> list[TreeEntry]:
    """Drop the literal lock paths (and anything beneath them) from *manifest*."""
    literals = [
        entry.replace(PROJECT_DIR_PLACEHOLDER, project_dir) for entry in exclusions
    ]
    return [
        entry
        for entry in manifest
        if not any(
            entry["path"] == literal or entry["path"].startswith(literal + "/")
            for literal in literals
        )
    ]


def discover_cases(fixtures_root: Path) -> list[Path]:
    """Return every case directory under *fixtures_root*, sorted by name."""
    return sorted(
        path
        for path in fixtures_root.iterdir()
        if path.is_dir() and (path / CASE_FILE).is_file()
    )


# --- running a case ---------------------------------------------------------


@contextmanager
def materialized_root() -> Iterator[Path]:
    """Yield an empty ``repo`` directory inside a fresh temp directory."""
    with tempfile.TemporaryDirectory(prefix="ai-team-parity-") as parent:
        root = Path(parent).resolve() / "repo"
        root.mkdir()
        yield root


def _substitute_root(value: str, root: Path) -> str:
    return value.replace(ROOT_PLACEHOLDER, str(root))


@contextmanager
def isolated_environment(root: Path, case: dict[str, Any]) -> Iterator[None]:
    """Apply the case's clock, version and env; clear everything else that leaks in.

    ``AI_TEAM_ROOT`` is removed unless the case sets it. ``GIT_CEILING_DIRECTORIES``
    stops git walking above the temp parent. The previous environment and working
    directory are restored on exit.
    """
    saved_env = dict(os.environ)
    saved_cwd = Path.cwd()
    try:
        os.environ.pop(ROOT_ENV_VAR, None)
        os.environ[TODAY_ENV_VAR] = case["today"]
        os.environ[FRAMEWORK_VERSION_ENV_VAR] = case["version"]
        os.environ[GIT_CEILING_ENV_VAR] = str(root.parent)
        for name, value in case.get("env", {}).items():
            os.environ[name] = _substitute_root(value, root)
        os.chdir(root)
        yield
    finally:
        os.chdir(saved_cwd)
        os.environ.clear()
        os.environ.update(saved_env)


def _project_root(repo: Path) -> ProjectRoot:
    if ROOT_ENV_VAR in os.environ:
        return find_project_root(repo)
    return find_project_root(repo, root=repo)


def _flag(inp: dict[str, Any], name: str) -> bool:
    return bool(inp.get(name, False))


def _list_handler(
    handler: Callable[..., Result],
) -> Callable[[ProjectRoot, dict], Result]:
    return lambda root, inp: handler(root, inp.get("state"))


# command -> handler(ProjectRoot, tool-contract input) for commands that need a root.
ROOT_COMMANDS: dict[str, Callable[[ProjectRoot, dict[str, Any]], Result]] = {
    "spec new": lambda root, inp: spec.create_spec(
        root, inp["title"], inp.get("author", "planner"), inp.get("status", "draft")
    ),
    "task new": lambda root, inp: task.create_task(
        root,
        inp["title"],
        inp.get("priority", "medium"),
        inp.get("assignedRole", "unassigned"),
        inp.get("spec"),
    ),
    "task start": lambda root, inp: task.start_task(root, inp["id"]),
    "task complete": lambda root, inp: task.complete_task(root, inp["id"]),
    "task unblock": lambda root, inp: task.unblock_task(root, inp["id"]),
    "task block": lambda root, inp: task.block_task(root, inp["id"], inp["reason"]),
    "bug new": lambda root, inp: bug.create_bug(
        root, inp["title"], inp.get("severity", "medium"), inp.get("task")
    ),
    "bug start": lambda root, inp: bug.start_bug(root, inp["id"]),
    "bug resolve": lambda root, inp: bug.resolve_bug(root, inp["id"]),
    "adr new": lambda root, inp: adr.create_adr(
        root, inp["title"], inp.get("status", "proposed"), inp.get("supersedes")
    ),
    "change-request new": lambda root, inp: change_request.create_change_request(
        root, inp["title"]
    ),
    "list tasks": _list_handler(list_command.list_tasks),
    "list bugs": _list_handler(list_command.list_bugs),
    "list specs": lambda root, inp: list_command.list_specs(root),
    "list adrs": lambda root, inp: list_command.list_adrs(root),
    "list change-requests": lambda root, inp: list_command.list_change_requests(root),
    "show": lambda root, inp: show.show_artifact(root, inp["identifier"]),
    "status": lambda root, inp: status.status_summary(root),
    "report": lambda root, inp: report.write_report(
        root, root.repo / inp["out"] if inp.get("out") else None
    ),
    "validate": lambda root, inp: validate.validate_artifacts(
        root,
        _flag(inp, "all"),
        _flag(inp, "tasks"),
        _flag(inp, "bugs"),
        _flag(inp, "specs"),
        _flag(inp, "adrs"),
        _flag(inp, "changeRequests"),
    ),
    "archive": lambda root, inp: archive.archive_artifacts(
        root, inp.get("olderThan", "90d"), _flag(inp, "dryRun")
    ),
}


def dispatch(command: str, repo: Path, inp: dict[str, Any]) -> Result:
    """Run *command* against the structured-result handler for *repo*."""
    if command == "init":
        return init.init_repository(
            repo / inp.get("path", "."),
            [],
            _flag(inp, "force"),
            _flag(inp, "dryRun"),
            _flag(inp, "createRootGuidance"),
        )
    if command == "check-layout":
        return check_layout.check_repository_layout(repo)
    handler = ROOT_COMMANDS.get(command)
    if handler is None:
        raise ValueError(f"Unknown parity command: {command!r}")
    try:
        return handler(_project_root(repo), inp)
    except ProjectRootNotFound as exc:
        return Result(status=1, message=exc.message, hint=exc.hint)


def _normalise(value: Any, root: Path) -> Any:
    if isinstance(value, str):
        return value.replace(str(root), ROOT_PLACEHOLDER)
    if isinstance(value, list):
        return [_normalise(item, root) for item in value]
    if isinstance(value, dict):
        return {key: _normalise(item, root) for key, item in value.items()}
    return value


def _normalise_tree(tree: list[TreeEntry], root: Path) -> list[TreeEntry]:
    return [
        {**entry, "text": _normalise(entry["text"], root)} if "text" in entry else entry
        for entry in tree
    ]


def _expected_result(result: Result, root: Path) -> dict[str, Any]:
    """Build the comparable result: hints are dropped, only root paths normalised."""
    expected: dict[str, Any] = {"status": result.status}
    if result.payload is not None:
        expected["payload"] = _normalise(result.payload, root)
    if result.message is not None:
        expected["message"] = _normalise(result.message, root)
    return expected


def _require_fields(case: dict[str, Any], source: Path) -> None:
    for name in REQUIRED_CASE_FIELDS:
        if name not in case:
            raise ValueError(f"{source} is missing required field {name!r}")


def _execute(
    case: dict[str, Any], before: list[TreeEntry]
) -> tuple[dict[str, Any], list[TreeEntry]]:
    with materialized_root() as root:
        materialize_tree(before, root)
        with isolated_environment(root, case):
            result = dispatch(case["command"], root, case["input"])
        after = exclude_lock_paths(
            serialize_tree(root),
            case.get("project_dir", "project"),
            load_lock_exclusions(FIXTURES_ROOT),
        )
        return _expected_result(result, root), _normalise_tree(after, root)


def _dump(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _diff(label: str, expected: Any, actual: Any) -> list[str]:
    if expected == actual:
        return []
    lines = difflib.unified_diff(
        _dump(expected).splitlines(),
        _dump(actual).splitlines(),
        fromfile=f"expected {label}",
        tofile=f"actual {label}",
        lineterm="",
    )
    return ["\n".join(lines)]


def compare_case(case_dir: Path) -> list[str]:
    """Run the case and return one diff per mismatch (empty when it passes)."""
    case = json.loads((case_dir / CASE_FILE).read_text("utf-8"))
    _require_fields(case, case_dir / CASE_FILE)
    before = json.loads((case_dir / "before.json").read_text("utf-8"))
    expected_after = json.loads((case_dir / "after.json").read_text("utf-8"))

    actual_result, actual_after = _execute(case, before)
    expected_result = case["expected"]

    diffs: list[str] = []
    diffs += _diff("result", expected_result, actual_result)
    diffs += _diff("after tree", expected_after, actual_after)
    return diffs


# --- recording a case -------------------------------------------------------


def record_case(
    fixtures_root: Path,
    *,
    command: str,
    case: str,
    input: dict[str, Any],
    before_dir: Path | None,
    today: str,
    version: str,
    env: dict[str, str] | None = None,
    project_dir: str = "project",
) -> Path:
    """Seed a new case from the Python implementation; never overwrites."""
    name = f"{command.replace(' ', '-')}--{case}"
    if not CASE_NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid case name {name!r}: use <command-slug>--<case> in lowercase "
            "letters, digits and single hyphens"
        )
    case_dir = fixtures_root / name
    if case_dir.exists():
        raise FileExistsError(
            f"Parity case already exists, refusing to overwrite: {name}"
        )

    before = serialize_tree(before_dir) if before_dir is not None else []
    definition: dict[str, Any] = {
        "command": command,
        "input": input,
        "today": today,
        "version": version,
        "env": env or {},
        "project_dir": project_dir,
    }
    result, after = _execute(definition, before)
    definition["expected"] = result

    case_dir.mkdir()
    (case_dir / CASE_FILE).write_text(_dump(definition), encoding="utf-8")
    (case_dir / "before.json").write_text(_dump(before), encoding="utf-8")
    (case_dir / "after.json").write_text(_dump(after), encoding="utf-8")
    return case_dir
