"""
ai_team.core.ids — pure-Python artifact ID allocation helpers.
"""

from __future__ import annotations

import re
from pathlib import Path

from ai_team.core.locator import ProjectRoot

_TASK_PATTERN = re.compile(r"^T-(\d{3})-.*\.md$")
_BUG_PATTERN = re.compile(r"^B-(\d{3})-.*\.md$")
_SPEC_PATTERN = re.compile(r"^S-(\d{3})-.*\.md$")
_ADR_PATTERN = re.compile(r"^ADR-(\d{3})-.*\.md$")


def next_task_id(project_root: ProjectRoot) -> str:
    """Return the next task ID in T-NNN format across all task state folders."""
    return _next_id(
        prefix="T",
        directories=(
            project_root.tasks_pending,
            project_root.tasks_in_progress,
            project_root.tasks_completed,
            project_root.tasks_blocked,
        ),
        pattern=_TASK_PATTERN,
    )


def next_bug_id(project_root: ProjectRoot) -> str:
    """Return the next bug ID in B-NNN format across all bug state folders."""
    return _next_id(
        prefix="B",
        directories=(
            project_root.bugs_open,
            project_root.bugs_in_progress,
            project_root.bugs_resolved,
        ),
        pattern=_BUG_PATTERN,
    )


def next_spec_id(project_root: ProjectRoot) -> str:
    """Return the next spec ID in S-NNN format across specs/ and specs/archive/."""
    return _next_id(
        prefix="S",
        directories=(project_root.specs, project_root.specs / "archive"),
        pattern=_SPEC_PATTERN,
    )


def next_adr_id(project_root: ProjectRoot) -> str:
    """Return the next ADR ID in ADR-NNN format from project/decisions/."""
    return _next_id(
        prefix="ADR",
        directories=(project_root.decisions,),
        pattern=_ADR_PATTERN,
    )


def _next_id(
    prefix: str, directories: tuple[Path, ...], pattern: re.Pattern[str]
) -> str:
    """Return the next zero-padded identifier for a prefix and search scope."""
    max_number = _max_matching_number(directories=directories, pattern=pattern)
    return f"{prefix}-{max_number + 1:03d}"


def _max_matching_number(
    directories: tuple[Path, ...], pattern: re.Pattern[str]
) -> int:
    """Return the largest numeric capture in matching filenames across directories."""
    max_number = 0
    for directory in directories:
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if not path.is_file():
                continue
            match = pattern.match(path.name)
            if match is None:
                continue
            max_number = max(max_number, int(match.group(1)))
    return max_number
