"""
ai_team.core.locator — locate the consuming project's root directory.

Resolution order:
  1. Explicit ``root`` keyword argument.
  2. ``AI_TEAM_ROOT`` environment variable.
  3. Walk up from ``cwd`` looking for ``.ai-team.toml``; use its ``[project] dir``
     setting as the artifact-folder name.
  4. Walk up from ``cwd`` looking for a folder whose name matches ``project_dir``
     (default ``"project"``).
  5. Raise ``ProjectRootNotFound`` with a message naming the searched paths and
     suggesting ``ai-team init``.

This module has no Typer dependency and may be imported from anywhere.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


class ProjectRootNotFound(RuntimeError):
    """Raised when no project root can be resolved from the given cwd."""


@dataclass(frozen=True)
class ProjectRoot:
    """Absolute paths to every AI-team artifact directory in a project."""

    repo: Path
    """The repository root (the directory that contains the project folder)."""

    project_dir: Path
    """The top-level artifact directory (e.g. ``repo/project``)."""

    specs: Path
    """``project_dir/specs``."""

    tasks_pending: Path
    """``project_dir/tasks/pending``."""

    tasks_in_progress: Path
    """``project_dir/tasks/in-progress``."""

    tasks_completed: Path
    """``project_dir/tasks/completed``."""

    tasks_blocked: Path
    """``project_dir/tasks/blocked``."""

    bugs_open: Path
    """``project_dir/bugs/open``."""

    bugs_in_progress: Path
    """``project_dir/bugs/in-progress``."""

    bugs_resolved: Path
    """``project_dir/bugs/resolved``."""

    change_requests: Path
    """``project_dir/change-requests``."""

    decisions: Path
    """``project_dir/decisions``."""

    docs: Path
    """``project_dir/docs``."""

    @classmethod
    def _from_repo_and_project_dir_name(
        cls, repo: Path, project_dir_name: str
    ) -> "ProjectRoot":
        """Build a ProjectRoot from a repo root and the artifact folder name."""
        pd = repo / project_dir_name
        return cls(
            repo=repo,
            project_dir=pd,
            specs=pd / "specs",
            tasks_pending=pd / "tasks" / "pending",
            tasks_in_progress=pd / "tasks" / "in-progress",
            tasks_completed=pd / "tasks" / "completed",
            tasks_blocked=pd / "tasks" / "blocked",
            bugs_open=pd / "bugs" / "open",
            bugs_in_progress=pd / "bugs" / "in-progress",
            bugs_resolved=pd / "bugs" / "resolved",
            change_requests=pd / "change-requests",
            decisions=pd / "decisions",
            docs=pd / "docs",
        )


def find_project_root(
    cwd: Path,
    *,
    root: Path | None = None,
    project_dir: str = "project",
) -> ProjectRoot:
    """Locate the project root and return a ``ProjectRoot`` with all artifact paths.

    Parameters
    ----------
    cwd:
        The directory to start searching from.  Must be an absolute path when
        the caller relies on ``ProjectRoot.repo`` being absolute, but any
        ``Path`` is accepted (it is resolved internally).
    root:
        When provided, treat this directory as the repo root and skip all
        environment-variable and filesystem searches.  The ``project_dir``
        folder must still exist under ``root``.
    project_dir:
        Name of the top-level artifact folder (default ``"project"``).  Used
        when no ``.ai-team.toml`` override is found.

    Raises
    ------
    ProjectRootNotFound
        When no project root can be resolved.  The message names the paths
        that were searched and suggests ``ai-team init``.
    """
    cwd = cwd.resolve()

    # ------------------------------------------------------------------
    # Strategy 1: explicit root= argument.
    # ------------------------------------------------------------------
    if root is not None:
        repo = root.resolve()
        dir_name = _toml_project_dir(repo) or project_dir
        if (repo / dir_name).is_dir():
            return ProjectRoot._from_repo_and_project_dir_name(repo, dir_name)
        raise ProjectRootNotFound(
            f"No '{dir_name}/' folder found under the provided --root {repo!s}. "
            "Run 'ai-team init' to bootstrap the project structure."
        )

    # ------------------------------------------------------------------
    # Strategy 2: AI_TEAM_ROOT environment variable.
    # ------------------------------------------------------------------
    env_root = os.environ.get("AI_TEAM_ROOT")
    if env_root:
        repo = Path(env_root).resolve()
        dir_name = _toml_project_dir(repo) or project_dir
        if (repo / dir_name).is_dir():
            return ProjectRoot._from_repo_and_project_dir_name(repo, dir_name)
        raise ProjectRootNotFound(
            f"No '{dir_name}/' folder found under AI_TEAM_ROOT={repo!s}. "
            "Run 'ai-team init' to bootstrap the project structure."
        )

    # ------------------------------------------------------------------
    # Strategy 3: Walk up looking for .ai-team.toml; use configured dir.
    # Strategy 4: Walk up looking for a folder named project_dir.
    #
    # Both strategies share a single upward walk.  At each directory we
    # check for .ai-team.toml first (strategy 3) then fall through to the
    # folder-name check (strategy 4).
    # ------------------------------------------------------------------
    searched: list[Path] = []
    candidate = cwd
    while True:
        searched.append(candidate)

        toml_dir_name = _toml_project_dir(candidate)
        if toml_dir_name is not None:
            # .ai-team.toml found; honour the configured dir name.
            if (candidate / toml_dir_name).is_dir():
                return ProjectRoot._from_repo_and_project_dir_name(
                    candidate, toml_dir_name
                )
            # TOML present but the declared folder is missing — keep walking.

        if (candidate / project_dir).is_dir():
            return ProjectRoot._from_repo_and_project_dir_name(candidate, project_dir)

        parent = candidate.parent
        if parent == candidate:
            # Reached the filesystem root without a match.
            break
        candidate = parent

    searched_str = ", ".join(str(p) for p in searched)
    raise ProjectRootNotFound(
        f"Could not locate a '{project_dir}/' directory by walking up from "
        f"{cwd!s}. Searched: {searched_str}. "
        "Run 'ai-team init' to bootstrap the project structure."
    )


def _toml_project_dir(directory: Path) -> str | None:
    """Return the ``[project] dir`` value from ``.ai-team.toml`` in *directory*.

    Returns ``None`` if the file does not exist, cannot be parsed, or does not
    contain the ``[project] dir`` key.
    """
    toml_path = directory / ".ai-team.toml"
    if not toml_path.is_file():
        return None
    try:
        with toml_path.open("rb") as fh:
            data = tomllib.load(fh)
    except OSError, tomllib.TOMLDecodeError:
        return None
    return data.get("project", {}).get("dir")
