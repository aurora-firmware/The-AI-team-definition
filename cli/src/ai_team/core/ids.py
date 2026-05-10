"""
ai_team.core.ids — pure-Python artifact ID allocation helpers.
"""

from __future__ import annotations

import re
from pathlib import Path

from ai_team.core.locator import ProjectRoot


def next_task_id(project_root: ProjectRoot) -> str:
    """Return the next task ID in T-NNN format across all task state folders."""
    max_number = _max_matching_number(
        directories=(
            project_root.tasks_pending,
            project_root.tasks_in_progress,
            project_root.tasks_completed,
            project_root.tasks_blocked,
        ),
        pattern=re.compile(r"^T-(\d{3})-.*\.md$"),
    )
    return f"T-{max_number + 1:03d}"


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
