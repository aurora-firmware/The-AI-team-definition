"""Validation checks for AI-team artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_team.core.locator import ProjectRoot


@dataclass(frozen=True)
class Finding:
    """A single validation result item."""

    path: str
    level: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "level": self.level,
            "code": self.code,
            "message": self.message,
        }


def validate_project(
    _root: ProjectRoot,
    *,
    tasks: bool = False,
    bugs: bool = False,
    specs: bool = False,
    adrs: bool = False,
) -> list[Finding]:
    """Validate selected artifact categories and return findings.

    This initial implementation returns no findings. Additional checks are
    added in subsequent TDD cycles.
    """
    _ = (tasks, bugs, specs, adrs)
    return []


def to_relative_path(path: Path, repo: Path) -> str:
    """Return *path* relative to *repo* when possible."""
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)
