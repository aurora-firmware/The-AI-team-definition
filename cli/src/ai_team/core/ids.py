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
_CHANGE_REQUEST_PATTERN = re.compile(r"^CR-(\d{3})-.*\.md$")
_SPEC_FRONTMATTER_ID_PATTERN = re.compile(
    r'^id:\s*["\']?S-(\d{3})["\']?\s*(?:#.*)?$',
    re.MULTILINE,
)


def next_task_id(project_root: ProjectRoot) -> str:
    """Return the next task ID in T-NNN format across the tracker and its archive."""
    return _next_id(
        prefix="T",
        directories=(project_root.tasks, *_archive_buckets(project_root)),
        pattern=_TASK_PATTERN,
    )


def next_bug_id(project_root: ProjectRoot) -> str:
    """Return the next bug ID in B-NNN format across the tracker and its archive."""
    return _next_id(
        prefix="B",
        directories=(project_root.bugs, *_archive_buckets(project_root)),
        pattern=_BUG_PATTERN,
    )


def _archive_buckets(project_root: ProjectRoot) -> tuple[Path, ...]:
    """Return the ``YYYY-MM`` archive bucket folders in the tracker."""
    if not project_root.archive.is_dir():
        return ()
    return tuple(
        sorted(path for path in project_root.archive.iterdir() if path.is_dir())
    )


def next_spec_id(project_root: ProjectRoot) -> str:
    """Return the next spec ID in S-NNN format across specs/ and specs/archive/."""
    directories = (project_root.specs, project_root.specs / "archive")
    max_number = max(
        _max_matching_number(directories=directories, pattern=_SPEC_PATTERN),
        _max_spec_frontmatter_id_number(directories=directories),
    )
    return f"S-{max_number + 1:03d}"


def next_adr_id(project_root: ProjectRoot) -> str:
    """Return the next ADR ID in ADR-NNN format from ai-team/decisions/."""
    return _next_id(
        prefix="ADR",
        directories=(project_root.decisions,),
        pattern=_ADR_PATTERN,
    )


def next_change_request_id(search_directories: tuple[Path, ...]) -> str:
    """Return the next CR-NNN identifier for the provided directories."""
    return _next_id(
        prefix="CR",
        directories=search_directories,
        pattern=_CHANGE_REQUEST_PATTERN,
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


def _max_spec_frontmatter_id_number(directories: tuple[Path, ...]) -> int:
    """Return the largest S-NNN id found in spec frontmatter across directories."""
    max_number = 0
    for directory in directories:
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            rest = text[3:]
            close_idx = rest.find("\n---")
            if close_idx == -1:
                continue
            frontmatter = rest[:close_idx]
            match = _SPEC_FRONTMATTER_ID_PATTERN.search(frontmatter)
            if match is None:
                continue
            max_number = max(max_number, int(match.group(1)))
    return max_number
