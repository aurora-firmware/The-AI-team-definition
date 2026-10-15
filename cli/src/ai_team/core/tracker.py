"""
ai_team.core.tracker — the local work-item tracker (spec S-006).

Tasks, bugs, and change-requests live outside version control in one tracker
folder per repository. Lifecycle state is the frontmatter ``status`` field;
no folder or filename encodes it.

Provides:
  - ``resolve_tracker_dir(repo)`` — the tracker folder configured by
    ``[tracker] dir`` in ``.ai-team.toml`` (default ``.ai-team/tracker``).
    Relative paths resolve against the repository's main working tree so that
    every git worktree shares one tracker.
  - ``TASK_STATUSES``, ``BUG_STATUSES``, ``CHANGE_REQUEST_STATUSES`` — the
    allowed ``status`` values per work-item kind.
  - ``iter_items(folder)`` / ``find_item(folder, item_id)`` — enumerate and
    look up work-item files.
  - ``legacy_work_item_dirs(project_dir)`` / ``legacy_warning(dirs)`` — detect
    pre-tracker ``tasks/``, ``bugs/``, and ``change-requests/`` folders that
    still hold files, and describe how to migrate them.

This module has no Typer dependency and does not import the locator.
"""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

DEFAULT_TRACKER_DIR = ".ai-team/tracker"

TASK_STATUSES = (
    "planned",
    "pending",
    "in-progress",
    "blocked",
    "completed",
    "cancelled",
)
BUG_STATUSES = ("open", "in-progress", "resolved")
CHANGE_REQUEST_STATUSES = ("pending", "approved", "rejected")

LEGACY_WORK_ITEM_DIRS = ("tasks", "bugs", "change-requests")

MIGRATION_GUIDE = "'Migrating to the local tracker' in the ai-team setup guide"


def _toml_tracker_dir(repo: Path) -> str | None:
    """Return the ``[tracker] dir`` value from ``repo/.ai-team.toml``, if any."""
    toml_path = repo / ".ai-team.toml"
    if not toml_path.is_file():
        return None
    try:
        with toml_path.open("rb") as fh:
            data = tomllib.load(fh)
    except OSError, tomllib.TOMLDecodeError:
        return None
    value = data.get("tracker", {}).get("dir")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def main_worktree(repo: Path) -> Path:
    """Return the main working tree of the git repository containing *repo*.

    Every linked worktree shares the main worktree's ``.git`` directory, so its
    parent is the same for all of them. Falls back to *repo* when *repo* is not
    inside a git repository, git is unavailable, or the repository is bare.
    """
    try:
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "rev-parse",
                "--path-format=absolute",
                "--git-common-dir",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except OSError, subprocess.CalledProcessError:
        return repo

    common_dir = Path(completed.stdout.strip())
    if common_dir.name != ".git":
        return repo
    return common_dir.parent


def resolve_tracker_dir(repo: Path) -> Path:
    """Return the absolute tracker folder for the repository at *repo*.

    Absolute and ``~`` paths are used as given. Relative paths resolve against
    the main working tree, so a Developer in a linked worktree and a loop in the
    main checkout read and write the same tracker.
    """
    configured = Path(_toml_tracker_dir(repo) or DEFAULT_TRACKER_DIR).expanduser()
    if configured.is_absolute():
        return configured
    return main_worktree(repo) / configured


def is_inside(path: Path, directory: Path) -> bool:
    """Return True when *path* is *directory* or lies below it."""
    try:
        path.resolve().relative_to(directory.resolve())
    except ValueError:
        return False
    return True


def _should_skip(path: Path) -> bool:
    return path.name == ".gitkeep" or path.match("TEMPLATE-*.md")


def iter_items(folder: Path) -> list[Path]:
    """Return the sorted work-item markdown files directly inside *folder*."""
    if not folder.is_dir():
        return []
    return sorted(
        path
        for path in folder.glob("*.md")
        if path.is_file() and not _should_skip(path)
    )


def find_item(folder: Path, item_id: str) -> Path | None:
    """Return the file in *folder* whose name is ``<item_id>.md`` or ``<item_id>-*.md``."""
    for path in iter_items(folder):
        if path.stem == item_id or path.stem.startswith(f"{item_id}-"):
            return path
    return None


def legacy_work_item_dirs(project_dir: Path) -> list[Path]:
    """Return pre-tracker work-item folders under *project_dir* that still hold files."""
    legacy: list[Path] = []
    for name in LEGACY_WORK_ITEM_DIRS:
        folder = project_dir / name
        if not folder.is_dir():
            continue
        if any(
            path.is_file() and not _should_skip(path) for path in folder.rglob("*.md")
        ):
            legacy.append(folder)
    return legacy


def legacy_warning(dirs: list[Path]) -> str:
    """Describe legacy folders that must be migrated into the tracker."""
    names = ", ".join(str(folder) for folder in dirs)
    return (
        f"Warning: legacy work-item folders still hold files: {names}. "
        "Tasks, bugs, and change-requests now live in the local tracker "
        "(see `ai-team tracker path`); these files are ignored until migrated. "
        f"Follow {MIGRATION_GUIDE}."
    )
