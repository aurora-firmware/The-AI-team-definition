"""Tests for T-084: structured results for list, show, status, report."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_team.cli import app
from ai_team.commands.list import (
    list_adrs,
    list_bugs,
    list_change_requests,
    list_specs,
    list_tasks,
)
from ai_team.commands.report import write_report
from ai_team.commands.show import show_artifact
from ai_team.commands.status import status_summary
from ai_team.core.locator import ProjectRoot, find_project_root

TASK = """\
---
id: "{id}"
title: "{title}"
status: {status}
priority: medium
assigned-role: developer
created: 2026-05-10
---

Body.
"""

BUG = """\
---
id: "{id}"
title: "{title}"
severity: high
status: {status}
created: 2026-05-10
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


def _cli_json(tmp_path: Path, monkeypatch, *args: str):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, [*args, "--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


# AC-1, AC-2
def test_list_tasks_handler_payload_equals_json_output(tmp_path, monkeypatch):
    root = _root(tmp_path)
    _write(
        root.tasks_pending / "T-001-a.md",
        TASK.format(id="T-001", title="A", status="pending"),
    )
    _write(
        root.tasks_blocked / "T-002-b.md",
        TASK.format(id="T-002", title="B", status="blocked"),
    )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    result = list_tasks(root, None)

    assert result.status == 0
    assert [row["id"] for row in result.payload] == ["T-001", "T-002"]
    assert result.payload == _cli_json(tmp_path, monkeypatch, "list", "tasks")


def test_list_tasks_handler_filters_by_state(tmp_path):
    root = _root(tmp_path)
    _write(
        root.tasks_pending / "T-001-a.md",
        TASK.format(id="T-001", title="A", status="pending"),
    )
    _write(
        root.tasks_blocked / "T-002-b.md",
        TASK.format(id="T-002", title="B", status="blocked"),
    )

    result = list_tasks(root, "blocked")

    assert [row["id"] for row in result.payload] == ["T-002"]


def test_list_bugs_handler_payload_equals_json_output(tmp_path, monkeypatch):
    root = _root(tmp_path)
    _write(
        root.bugs_open / "B-001-a.md",
        BUG.format(id="B-001", title="A", status="open"),
    )

    result = list_bugs(root, None)

    assert result.payload == _cli_json(tmp_path, monkeypatch, "list", "bugs")
    assert result.payload[0]["severity"] == "high"


def test_list_specs_adrs_and_change_requests_handlers_match_json(tmp_path, monkeypatch):
    root = _root(tmp_path)
    _write(
        root.specs / "S-001-a.md",
        '---\nid: "S-001"\ntitle: "Spec"\nversion: "0.1"\nstatus: approved\n'
        "created: 2026-05-10\nauthor: planner\n---\n\nBody.\n",
    )
    _write(
        root.decisions / "ADR-001-a.md",
        '---\nid: "ADR-001"\ntitle: "Adr"\nstatus: accepted\n'
        "created: 2026-05-10\n---\n\nBody.\n",
    )
    cli_specs = _cli_json(tmp_path, monkeypatch, "list", "specs")
    cli_adrs = _cli_json(tmp_path, monkeypatch, "list", "adrs")
    cli_crs = _cli_json(tmp_path, monkeypatch, "list", "change-requests")

    assert list_specs(root).payload == cli_specs
    assert list_adrs(root).payload == cli_adrs
    assert list_change_requests(root).payload == cli_crs
    assert cli_specs and cli_adrs and cli_crs == []


@pytest.mark.parametrize("handler", [list_tasks, list_bugs])
def test_list_handlers_return_empty_payload_for_unknown_state(tmp_path, handler):
    root = _root(tmp_path)

    assert handler(root, "nonsense").payload == []


# AC-1, AC-2
def test_show_handler_payload_equals_json_output(tmp_path, monkeypatch):
    root = _root(tmp_path)
    _write(
        root.tasks_pending / "T-001-a.md",
        TASK.format(id="T-001", title="A", status="pending"),
    )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    result = show_artifact(root, "T-001")

    assert result.status == 0
    assert result.payload["frontmatter"]["id"] == "T-001"
    assert result.payload == _cli_json(tmp_path, monkeypatch, "show", "T-001")


# AC-4
def test_show_handler_reports_unknown_id_with_todays_message(tmp_path, monkeypatch):
    root = _root(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = show_artifact(root, "T-999")
    cli = CliRunner().invoke(app, ["show", "T-999"])

    assert result.status == 1
    assert result.payload is None
    assert result.message.startswith("Artifact 'T-999' not found. Searched roots: ")
    assert cli.exit_code == 1
    assert result.text() in cli.output


def test_show_handler_lists_every_path_when_identifier_is_ambiguous(tmp_path):
    root = _root(tmp_path)
    _write(
        root.tasks_pending / "T-001-dup-a.md",
        TASK.format(id="T-001", title="A", status="pending"),
    )
    _write(
        root.tasks_completed / "T-002-dup-b.md",
        TASK.format(id="T-002", title="B", status="completed"),
    )

    result = show_artifact(root, "dup")

    assert result.status == 1
    assert result.message.splitlines()[0] == "Multiple artifacts matched 'dup':"
    assert len(result.message.splitlines()) == 3


# AC-1, AC-2
def test_status_handler_payload_equals_json_output(tmp_path, monkeypatch):
    root = _root(tmp_path)
    _write(
        root.tasks_in_progress / "T-001-a.md",
        TASK.format(id="T-001", title="A", status="in-progress"),
    )
    _write(
        root.bugs_open / "B-001-a.md",
        BUG.format(id="B-001", title="A", status="open"),
    )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    result = status_summary(root)

    assert result.status == 0
    assert result.payload["counts"]["tasks"]["in_progress"] == 1
    assert result.payload["critical_high_open_bugs"][0]["id"] == "B-001"
    assert result.payload == _cli_json(tmp_path, monkeypatch, "status")


def test_status_handler_reports_integration_result_not_found_outside_git(tmp_path):
    root = _root(tmp_path)

    result = status_summary(root)

    assert result.payload["latest_integration_result"] == "not found"


# AC-1, AC-3
def test_report_handler_returns_default_path_and_content_without_out(
    tmp_path, monkeypatch
):
    root = _root(tmp_path)
    _write(
        root.tasks_in_progress / "T-001-a.md",
        TASK.format(id="T-001", title="Alpha", status="in-progress"),
    )
    monkeypatch.setenv("AI_TEAM_TODAY", "2026-01-02")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    result = write_report(root, None)

    expected = (root.docs / "reports" / "progress-report-2026-01-02.md").resolve()
    assert result.status == 0
    assert Path(result.payload["path"]) == expected
    assert expected.read_text(encoding="utf-8") == result.payload["content"]
    assert "Progress Report — 2026-01-02" in result.payload["content"]
    assert "T-001 | Alpha" in result.payload["content"]
    assert "Latest integration-test result: not found" in result.payload["content"]


def test_report_handler_writes_to_out_path_and_cli_prints_same_path(
    tmp_path, monkeypatch
):
    root = _root(tmp_path)
    destination = tmp_path / "custom" / "nested" / "report.md"
    monkeypatch.chdir(tmp_path)

    result = write_report(root, destination)
    cli = CliRunner().invoke(app, ["report", "--out", str(destination)])

    assert Path(result.payload["path"]) == destination.resolve()
    assert destination.is_file()
    assert cli.stdout.strip() == result.payload["path"]
