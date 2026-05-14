"""Tests for T-010: ai-team task new command."""

import json
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


def test_task_new_supports_custom_flags_and_json_output(monkeypatch, tmp_path):
    """`task new --json` emits id/path and writes frontmatter from supplied flags."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "tasks" / "pending")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "task",
            "new",
            "Build Auth Gateway",
            "--priority",
            "critical",
            "--assigned-role",
            "developer",
            "--spec",
            "S-101",
            "--json",
        ],
    )

    expected = (
        tmp_path / "project" / "tasks" / "pending" / "T-001-build-auth-gateway.md"
    )
    payload = json.loads(result.output)

    assert result.exit_code == 0
    assert payload == {"id": "T-001", "path": str(expected)}
    assert "┏" not in result.output

    task = parse_task(expected)
    assert task.id == "T-001"
    assert task.title == "Build Auth Gateway"
    assert task.status == "pending"
    assert task.priority == "critical"
    assert task.assigned_role == "developer"
    assert task.created == date.today().isoformat()
    assert task.spec == "S-101"


def test_task_new_refuses_to_overwrite_when_allocated_path_exists(
    monkeypatch, tmp_path
):
    """If the allocated output file exists, command exits non-zero and keeps file bytes."""
    from ai_team.cli import app

    pending = tmp_path / "project" / "tasks" / "pending"
    _mkdir(pending)

    existing = pending / "T-001-ship-api.md"
    existing.write_text("existing bytes\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("ai_team.commands.task.next_task_id", lambda _root: "T-001")
    result = CliRunner().invoke(app, ["task", "new", "Ship API"])

    assert result.exit_code != 0
    assert "already exists" in result.stderr.lower()
    assert existing.read_text(encoding="utf-8") == "existing bytes\n"
