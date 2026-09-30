"""Tests for T-085: structured results for validate, archive, check-layout."""

import json
from datetime import date, timedelta
from pathlib import Path

from typer.testing import CliRunner

from ai_team.cli import app
from ai_team.commands.archive import archive_artifacts
from ai_team.commands.check_layout import check_repository_layout
from ai_team.commands.validate import validate_artifacts
from ai_team.core.layout import LayoutFinding
from ai_team.core.locator import ProjectRoot, find_project_root

TASK = """\
---
id: "{id}"
title: "{title}"
status: {status}
priority: medium
assigned-role: developer
created: {created}
{extra}
---

Body.
"""

BUG = """\
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


def _root(tmp_path: Path) -> ProjectRoot:
    for state in ("pending", "in-progress", "completed", "blocked"):
        (tmp_path / "project" / "tasks" / state).mkdir(parents=True)
    for state in ("open", "in-progress", "resolved"):
        (tmp_path / "project" / "bugs" / state).mkdir(parents=True)
    for folder in ("specs", "decisions", "change-requests"):
        (tmp_path / "project" / folder).mkdir(parents=True)
    return find_project_root(tmp_path, root=tmp_path)


def _old_date() -> str:
    return (date.today() - timedelta(days=400)).isoformat()


def _task(root: ProjectRoot, **fields: str) -> None:
    values = {
        "id": "T-001",
        "title": "A",
        "status": "pending",
        "created": "2026-05-10",
        "extra": "",
    }
    values.update(fields)
    _write(root.tasks_pending / "T-001-a.md", TASK.format(**values))


# AC-1
def test_validate_handler_returns_findings_with_code_path_message(tmp_path):
    root = _root(tmp_path)
    _task(root, status="completed")

    result = validate_artifacts(root, False, False, False, False, False, False)

    assert result.payload
    for finding in result.payload:
        assert {"code", "path", "message"} <= set(finding)


def test_validate_handler_selecting_flags_limit_scope(tmp_path):
    root = _root(tmp_path)
    _task(root, status="completed")

    tasks_only = validate_artifacts(root, False, True, False, False, False, False)
    bugs_only = validate_artifacts(root, False, False, True, False, False, False)

    assert tasks_only.payload
    assert bugs_only.payload == []


def test_validate_handler_payload_equals_json_output(tmp_path, monkeypatch):
    root = _root(tmp_path)
    _task(root, status="completed")
    monkeypatch.chdir(tmp_path)

    result = validate_artifacts(root, True, False, False, False, False, False)
    cli = CliRunner().invoke(app, ["validate", "--json"])

    assert json.loads(cli.stdout) == result.payload


# AC-4
def test_validate_handler_status_is_one_when_error_findings_exist(tmp_path):
    root = _root(tmp_path)
    _task(root, status="completed")

    result = validate_artifacts(root, True, False, False, False, False, False)

    assert result.status == 1
    assert any(f["level"] == "error" for f in result.payload)


def test_validate_handler_status_is_zero_for_clean_project(tmp_path):
    root = _root(tmp_path)

    result = validate_artifacts(root, True, False, False, False, False, False)

    assert result.status == 0
    assert result.payload == []


def test_validate_cli_exit_status_matches_handler_status(tmp_path, monkeypatch):
    root = _root(tmp_path)
    _task(root, status="completed")
    monkeypatch.chdir(tmp_path)

    cli = CliRunner().invoke(app, ["validate"])

    assert cli.exit_code == 1
    assert "findings" in cli.stdout


# AC-1, AC-3
def test_archive_handler_dry_run_returns_candidates_and_moves_nothing(tmp_path):
    root = _root(tmp_path)
    source = root.tasks_completed / "T-001-a.md"
    _write(
        source,
        TASK.format(
            id="T-001", title="A", status="completed", created=_old_date(), extra=""
        ),
    )

    result = archive_artifacts(root, "90d", True)

    assert result.status == 0
    assert result.payload["dry_run"] is True
    assert [Path(m["source"]) for m in result.payload["moves"]] == [source]
    assert source.exists()
    assert not (root.project_dir / "archive").exists()


def test_archive_handler_moves_old_artifacts_and_reports_destinations(tmp_path):
    root = _root(tmp_path)
    created = _old_date()
    source = root.bugs_resolved / "B-001-a.md"
    _write(source, BUG.format(id="B-001", title="A", created=created))

    result = archive_artifacts(root, "90d", False)

    destination = Path(result.payload["moves"][0]["destination"])
    assert result.payload["dry_run"] is False
    assert destination.exists()
    assert not source.exists()


def test_archive_handler_returns_failure_for_invalid_duration(tmp_path):
    root = _root(tmp_path)

    result = archive_artifacts(root, "soon", False)

    assert result.status == 1
    assert "Invalid --older-than 'soon'" in result.text()


def test_archive_cli_output_is_unchanged_for_dry_run(tmp_path, monkeypatch):
    root = _root(tmp_path)
    source = root.tasks_completed / "T-001-a.md"
    _write(
        source,
        TASK.format(
            id="T-001", title="A", status="completed", created=_old_date(), extra=""
        ),
    )
    monkeypatch.chdir(tmp_path)

    cli = CliRunner().invoke(app, ["archive", "--dry-run"])

    assert cli.exit_code == 0
    assert cli.stdout.startswith(f"WOULD MOVE: {source} -> ")


# AC-1, AC-2
def test_check_layout_handler_keeps_suggested_fix_separate_from_message(
    monkeypatch, tmp_path
):
    from ai_team.commands import check_layout as command

    monkeypatch.setattr(
        command,
        "run_layout_checks",
        lambda repo: [
            LayoutFinding(2, "b.md", "bad file", "rename it"),
            LayoutFinding(1, "a", "missing", "restore it"),
        ],
    )

    result = check_repository_layout(tmp_path)

    assert result.status == 1
    assert result.payload["findings"] == [
        {"level": 1, "path": "a", "message": "missing", "suggested_fix": "restore it"},
        {
            "level": 2,
            "path": "b.md",
            "message": "bad file",
            "suggested_fix": "rename it",
        },
    ]


def test_check_layout_handler_status_is_zero_without_findings(monkeypatch, tmp_path):
    from ai_team.commands import check_layout as command

    monkeypatch.setattr(command, "run_layout_checks", lambda repo: [])

    result = check_repository_layout(tmp_path)

    assert result.status == 0
    assert result.payload == {"findings": []}


# AC-5
def test_no_public_json_flag_on_archive_or_check_layout(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    assert runner.invoke(app, ["archive", "--json"]).exit_code == 2
    assert runner.invoke(app, ["check-layout", "--json"]).exit_code == 2
