"""Tests for T-016: ai-team archive command."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture(autouse=True)
def _project_dir(tmp_path):
    """The locator needs the project directory; work items live in the tracker."""
    (tmp_path / "ai-team").mkdir(exist_ok=True)


TASK_TEMPLATE = """\
---
id: "{id}"
title: "{title}"
status: completed
priority: medium
assigned-role: developer
created: {created}
---

Body.
"""

BUG_TEMPLATE = """\
---
id: "{id}"
title: "{title}"
severity: medium
status: resolved
created: {created}
---

Body.
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_completed_task(path: Path, task_id: str, created: str) -> None:
    _write(
        path,
        TASK_TEMPLATE.format(
            id=task_id,
            title=f"Task {task_id}",
            created=created,
        ),
    )


def _write_resolved_bug(path: Path, bug_id: str, created: str) -> None:
    _write(
        path,
        BUG_TEMPLATE.format(
            id=bug_id,
            title=f"Bug {bug_id}",
            created=created,
        ),
    )


def test_archive_moves_old_completed_tasks_and_resolved_bugs_to_created_month(
    monkeypatch, tmp_path: Path
) -> None:
    """Default archive run moves artifacts older than 90 days into archive/YYYY-MM."""
    from ai_team.cli import app

    old_task_src = tmp_path / ".ai-team" / "tracker" / "tasks" / "T-100-old-task.md"
    old_bug_src = tmp_path / ".ai-team" / "tracker" / "bugs" / "B-100-old-bug.md"
    fresh_task_src = tmp_path / ".ai-team" / "tracker" / "tasks" / "T-101-fresh-task.md"

    _write_completed_task(old_task_src, "T-100", "2025-01-15")
    _write_resolved_bug(old_bug_src, "B-100", "2024-12-09")
    _write_completed_task(
        fresh_task_src,
        "T-101",
        (date.today() - timedelta(days=10)).isoformat(),
    )

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["archive"])

    old_task_dest = (
        tmp_path / ".ai-team" / "tracker" / "archive" / "2025-01" / old_task_src.name
    )
    old_bug_dest = (
        tmp_path / ".ai-team" / "tracker" / "archive" / "2024-12" / old_bug_src.name
    )

    assert result.exit_code == 0
    assert not old_task_src.exists()
    assert not old_bug_src.exists()
    assert old_task_dest.exists()
    assert old_bug_dest.exists()
    assert fresh_task_src.exists()


def test_archive_dry_run_lists_would_move_without_mutating_filesystem(
    monkeypatch, tmp_path: Path
) -> None:
    """`archive --dry-run` reports planned moves and leaves source files untouched."""
    from ai_team.cli import app

    old_task_src = tmp_path / ".ai-team" / "tracker" / "tasks" / "T-110-old-task.md"
    _write_completed_task(
        old_task_src,
        "T-110",
        (date.today() - timedelta(days=120)).isoformat(),
    )
    expected_bucket = (date.today() - timedelta(days=120)).strftime("%Y-%m")
    expected_dest = (
        tmp_path
        / ".ai-team"
        / "tracker"
        / "archive"
        / expected_bucket
        / old_task_src.name
    )

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["archive", "--dry-run"])

    assert result.exit_code == 0
    assert "would move" in result.output.lower()
    assert str(old_task_src) in result.output
    assert str(expected_dest) in result.output
    assert old_task_src.exists()
    assert not expected_dest.exists()


def test_archive_uses_older_than_cutoff_to_select_artifacts(
    monkeypatch, tmp_path: Path
) -> None:
    """`archive --older-than` moves only artifacts strictly older than the cutoff."""
    from ai_team.cli import app

    should_move = (
        tmp_path / ".ai-team" / "tracker" / "tasks" / "T-120-older-than-cutoff.md"
    )
    should_stay = tmp_path / ".ai-team" / "tracker" / "tasks" / "T-121-within-cutoff.md"

    move_created = (date.today() - timedelta(days=85)).isoformat()
    stay_created = (date.today() - timedelta(days=80)).isoformat()
    _write_completed_task(should_move, "T-120", move_created)
    _write_completed_task(should_stay, "T-121", stay_created)

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["archive", "--older-than", "12w"])

    moved_dest = (
        tmp_path
        / ".ai-team"
        / "tracker"
        / "archive"
        / date.fromisoformat(move_created).strftime("%Y-%m")
        / should_move.name
    )

    assert result.exit_code == 0
    assert moved_dest.exists()
    assert not should_move.exists()
    assert should_stay.exists()


def test_archive_rejects_invalid_older_than_value(monkeypatch, tmp_path: Path) -> None:
    """Invalid --older-than syntax exits non-zero with a clear error message."""
    from ai_team.cli import app

    (tmp_path / "ai-team").mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, ["archive", "--older-than", "abc"])

    assert result.exit_code != 0
    assert "invalid --older-than" in result.stderr.lower()
    assert "number" in result.stderr.lower()
