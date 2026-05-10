"""Tests for T-016: ai-team archive command."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from typer.testing import CliRunner

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

    old_task_src = (
        tmp_path / "project" / "tasks" / "completed" / "T-100-old-task.md"
    )
    old_bug_src = tmp_path / "project" / "bugs" / "resolved" / "B-100-old-bug.md"
    fresh_task_src = (
        tmp_path / "project" / "tasks" / "completed" / "T-101-fresh-task.md"
    )

    _write_completed_task(old_task_src, "T-100", "2025-01-15")
    _write_resolved_bug(old_bug_src, "B-100", "2024-12-09")
    _write_completed_task(
        fresh_task_src,
        "T-101",
        (date.today() - timedelta(days=10)).isoformat(),
    )

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["archive"])

    old_task_dest = tmp_path / "project" / "archive" / "2025-01" / old_task_src.name
    old_bug_dest = tmp_path / "project" / "archive" / "2024-12" / old_bug_src.name

    assert result.exit_code == 0
    assert not old_task_src.exists()
    assert not old_bug_src.exists()
    assert old_task_dest.exists()
    assert old_bug_dest.exists()
    assert fresh_task_src.exists()
