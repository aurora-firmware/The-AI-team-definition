"""Tests for T-010: ai-team task new command."""

from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from ai_team.core.models import parse_task


def _mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def test_task_new_creates_pending_task_with_defaults_and_prints_absolute_path(
    monkeypatch, tmp_path
):
    """`ai-team task new` creates one pending task file and echoes its absolute path."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "tasks" / "pending")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["task", "new", "Ship API"])

    expected = tmp_path / "project" / "tasks" / "pending" / "T-001-ship-api.md"

    assert result.exit_code == 0
    assert result.output.strip() == str(expected)

    files = list((tmp_path / "project" / "tasks" / "pending").glob("*.md"))
    assert files == [expected]

    task = parse_task(expected)
    assert task.id == "T-001"
    assert task.title == "Ship API"
    assert task.status == "pending"
    assert task.priority == "medium"
    assert task.assigned_role == "unassigned"
    assert task.created == date.today().isoformat()
    assert task.spec is None
