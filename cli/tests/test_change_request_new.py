"""Tests for T-047: ai-team change-request new command."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from ai_team.core.models import parse_change_request


def _mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def test_change_request_new_creates_file_and_prints_absolute_path(
    monkeypatch, tmp_path
):
    """`ai-team change-request new` creates one CR-NNN-<slug>.md and echoes its path."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "change-requests")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["change-request", "new", "Add dark mode"])

    expected = tmp_path / "project" / "change-requests" / "CR-001-add-dark-mode.md"

    assert result.exit_code == 0, result.output
    assert result.output.strip() == str(expected)

    files = list((tmp_path / "project" / "change-requests").glob("*.md"))
    assert files == [expected]

    cr = parse_change_request(expected)
    assert cr.id == "CR-001"
    assert cr.title == "Add dark mode"
    assert cr.status == "pending"
    assert cr.created == date.today().isoformat()


def test_change_request_new_writes_metadata_into_frontmatter(monkeypatch, tmp_path):
    """`change-request new` writes the title and status into the artifact frontmatter."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "change-requests")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app, ["change-request", "new", "Revamp onboarding flow"]
    )

    assert result.exit_code == 0, result.output

    expected = (
        tmp_path / "project" / "change-requests" / "CR-001-revamp-onboarding-flow.md"
    )

    cr = parse_change_request(expected)
    assert cr.id == "CR-001"
    assert cr.title == "Revamp onboarding flow"
    assert cr.status == "pending"
    assert cr.created == date.today().isoformat()


def test_change_request_new_json_flag_emits_id_and_path_without_table(
    monkeypatch, tmp_path
):
    """`change-request new --json` emits id/path without table formatting."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "change-requests")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app, ["change-request", "new", "Add dark mode", "--json"]
    )

    expected = tmp_path / "project" / "change-requests" / "CR-001-add-dark-mode.md"

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload == {"id": "CR-001", "path": str(expected)}
    assert "┏" not in result.output


def test_change_request_new_refuses_to_overwrite_existing_path(monkeypatch, tmp_path):
    """Existing output path causes non-zero exit and preserves file bytes."""
    from ai_team.cli import app

    cr_dir = tmp_path / "project" / "change-requests"
    _mkdir(cr_dir)

    existing = cr_dir / "CR-001-add-dark-mode.md"
    existing.write_text("existing bytes\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "ai_team.commands.change_request.next_change_request_id",
        lambda _dirs: "CR-001",
    )
    result = CliRunner().invoke(app, ["change-request", "new", "Add dark mode"])

    assert result.exit_code != 0
    assert "already exists" in result.stderr.lower()
    assert existing.read_text(encoding="utf-8") == "existing bytes\n"
