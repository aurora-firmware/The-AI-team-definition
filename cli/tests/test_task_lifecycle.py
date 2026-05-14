"""Tests for T-014: task lifecycle commands."""

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_team.core.fs import read_artifact
from ai_team.core.models import parse_task

TASK_TEMPLATE = """\
---
id: "{id}"
title: "{title}"
status: {status}
priority: medium
assigned-role: developer
created: 2026-05-10
---

## Description

Task body.

## Work Log
"""


def _write_task(path: Path, task_id: str, title: str, status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        TASK_TEMPLATE.format(id=task_id, title=title, status=status),
        encoding="utf-8",
    )


def test_task_start_moves_pending_task_to_in_progress_and_updates_status(
    monkeypatch, tmp_path
):
    """`task start` moves pending->in-progress and sets frontmatter status."""
    from ai_team.cli import app

    pending = tmp_path / "project" / "tasks" / "pending" / "T-042-demo-task.md"
    _write_task(pending, "T-042", "Demo Task", "pending")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["task", "start", "T-042"])

    destination = tmp_path / "project" / "tasks" / "in-progress" / "T-042-demo-task.md"
    assert result.exit_code == 0
    assert not pending.exists()
    assert destination.exists()
    assert parse_task(destination).status == "in-progress"


def test_task_complete_moves_in_progress_task_to_completed_and_updates_status(
    monkeypatch, tmp_path
):
    """`task complete` moves in-progress->completed and sets frontmatter status."""
    from ai_team.cli import app

    source = tmp_path / "project" / "tasks" / "in-progress" / "T-043-demo-task.md"
    _write_task(source, "T-043", "Demo Task", "in-progress")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["task", "complete", "T-043"])

    destination = tmp_path / "project" / "tasks" / "completed" / "T-043-demo-task.md"
    assert result.exit_code == 0
    assert not source.exists()
    assert destination.exists()
    assert parse_task(destination).status == "completed"


def test_task_unblock_moves_blocked_task_to_in_progress_and_updates_status(
    monkeypatch, tmp_path
):
    """`task unblock` moves blocked->in-progress and sets frontmatter status."""
    from ai_team.cli import app

    source = tmp_path / "project" / "tasks" / "blocked" / "T-044-demo-task.md"
    _write_task(source, "T-044", "Demo Task", "blocked")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["task", "unblock", "T-044"])

    destination = tmp_path / "project" / "tasks" / "in-progress" / "T-044-demo-task.md"
    assert result.exit_code == 0
    assert not source.exists()
    assert destination.exists()
    assert parse_task(destination).status == "in-progress"


def test_task_block_moves_task_to_blocked_updates_status_and_appends_reason(
    monkeypatch, tmp_path
):
    """`task block --reason` moves task, sets blocked status, and logs reason entry."""
    from ai_team.cli import app

    source = tmp_path / "project" / "tasks" / "pending" / "T-045-demo-task.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        """\
---
id: "T-045"
title: "Demo Task"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
---

## Description

Task body.

## Work Log

### Session 1 — 2026-05-09
initial setup complete
""",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    reason = "waiting on architect decision"
    result = CliRunner().invoke(
        app,
        ["task", "block", "T-045", "--reason", reason],
    )

    destination = tmp_path / "project" / "tasks" / "blocked" / "T-045-demo-task.md"
    assert result.exit_code == 0
    assert not source.exists()
    assert destination.exists()
    assert parse_task(destination).status == "blocked"

    _, body = read_artifact(destination, "task")
    assert "### Session 2" in body
    assert date.today().isoformat() in body
    assert reason in body


def test_task_block_moves_completed_task_to_blocked(monkeypatch, tmp_path):
    """`task block` can move a task from completed->blocked."""
    from ai_team.cli import app

    source = tmp_path / "project" / "tasks" / "completed" / "T-046-demo-task.md"
    _write_task(source, "T-046", "Demo Task", "completed")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app,
        ["task", "block", "T-046", "--reason", "needs rework"],
    )

    destination = tmp_path / "project" / "tasks" / "blocked" / "T-046-demo-task.md"
    assert result.exit_code == 0
    assert not source.exists()
    assert destination.exists()
    assert parse_task(destination).status == "blocked"


@pytest.mark.parametrize(
    ("command", "state", "task_id", "extra_args", "expected_state"),
    [
        ("start", "in-progress", "T-050", [], "in-progress"),
        ("complete", "completed", "T-051", [], "completed"),
        ("block", "blocked", "T-052", ["--reason", "new reason"], "blocked"),
        ("unblock", "in-progress", "T-053", [], "in-progress"),
    ],
)
def test_lifecycle_command_is_idempotent_when_task_already_in_destination_state(
    monkeypatch, tmp_path, command, state, task_id, extra_args, expected_state
):
    """Lifecycle commands are no-ops when task is already in destination."""
    from ai_team.cli import app

    task_path = tmp_path / "project" / "tasks" / state / f"{task_id}-demo-task.md"
    _write_task(task_path, task_id, "Demo Task", state)
    before_bytes = task_path.read_bytes()

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["task", command, task_id, *extra_args])

    assert result.exit_code == 0
    assert f"already in {expected_state}" in result.output
    assert task_path.exists()
    assert task_path.read_bytes() == before_bytes


def test_lifecycle_command_reports_not_found_and_names_searched_folders(
    monkeypatch, tmp_path
):
    """Missing task ID returns non-zero and includes searched lifecycle folders."""
    from ai_team.cli import app

    for state in ("pending", "in-progress", "completed", "blocked"):
        (tmp_path / "project" / "tasks" / state).mkdir(parents=True, exist_ok=True)

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["task", "start", "T-999"])

    assert result.exit_code != 0
    assert "not found" in result.stderr.lower()
    assert "tasks/pending" in result.stderr
    assert "tasks/in-progress" in result.stderr
    assert "tasks/completed" in result.stderr
    assert "tasks/blocked" in result.stderr
