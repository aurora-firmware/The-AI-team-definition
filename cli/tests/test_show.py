"""Tests for T-006: ai-team show command."""

from pathlib import Path

from typer.testing import CliRunner


TASK_TEMPLATE = """\
---
id: "{id}"
title: "{title}"
status: pending
priority: medium
assigned-role: developer
created: 2026-05-10
---

# {title}

{body}
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _task(id: str, title: str, body: str) -> str:
    return TASK_TEMPLATE.format(id=id, title=title, body=body)


def test_show_exact_id_single_match_prints_markdown(monkeypatch, tmp_path):
    """`ai-team show T-001` prints the artifact markdown when exactly one file matches."""
    from ai_team.cli import app

    task_path = tmp_path / "project" / "tasks" / "pending" / "T-001-initial-scaffold.md"
    _write(task_path, _task("T-001", "Initial scaffold", "Task body line."))

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["show", "T-001"])

    assert result.exit_code == 0
    assert "Initial scaffold" in result.output
    assert "Task body line." in result.output


def test_show_json_outputs_path_frontmatter_and_body(monkeypatch, tmp_path):
    """`--json` emits a single JSON object with path/frontmatter/body and no Rich output."""
    import json

    from ai_team.cli import app

    task_path = tmp_path / "project" / "tasks" / "pending" / "T-002-json-case.md"
    _write(task_path, _task("T-002", "JSON case", "Body for json."))

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["show", "T-002", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload == {
        "path": str(task_path),
        "frontmatter": {
            "id": "T-002",
            "title": "JSON case",
            "status": "pending",
            "priority": "medium",
            "assigned-role": "developer",
            "created": "2026-05-10",
        },
        "body": "# JSON case\n\nBody for json.\n",
    }
