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
