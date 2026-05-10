"""Tests for T-015: bug lifecycle commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_team.core.models import parse_bug


BUG_TEMPLATE = """\
---
id: "{id}"
title: "{title}"
severity: {severity}
status: {status}
created: 2026-05-10
---

## Summary

Bug details.
"""


def _write_bug(path: Path, bug_id: str, title: str, severity: str, status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        BUG_TEMPLATE.format(
            id=bug_id,
            title=title,
            severity=severity,
            status=status,
        ),
        encoding="utf-8",
    )


def test_bug_start_moves_open_bug_to_in_progress_and_updates_status(
    monkeypatch, tmp_path
):
    """`bug start` moves open->in-progress and sets frontmatter status."""
    from ai_team.cli import app

    source = tmp_path / "project" / "bugs" / "open" / "B-007-memory-leak.md"
    _write_bug(source, "B-007", "Memory leak", "high", "open")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["bug", "start", "B-007"])

    destination = (
        tmp_path / "project" / "bugs" / "in-progress" / "B-007-memory-leak.md"
    )
    assert result.exit_code == 0
    assert not source.exists()
    assert destination.exists()
    assert parse_bug(destination).status == "in-progress"


def test_bug_resolve_moves_in_progress_bug_to_resolved_and_updates_status(
    monkeypatch, tmp_path
):
    """`bug resolve` moves in-progress->resolved and sets frontmatter status."""
    from ai_team.cli import app

    source = (
        tmp_path / "project" / "bugs" / "in-progress" / "B-008-timeout-spike.md"
    )
    _write_bug(source, "B-008", "Timeout spike", "medium", "in-progress")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["bug", "resolve", "B-008"])

    destination = (
        tmp_path / "project" / "bugs" / "resolved" / "B-008-timeout-spike.md"
    )
    assert result.exit_code == 0
    assert not source.exists()
    assert destination.exists()
    assert parse_bug(destination).status == "resolved"


@pytest.mark.parametrize(
    ("command", "state", "bug_id", "severity"),
    [
        ("start", "in-progress", "B-009", "high"),
        ("resolve", "resolved", "B-010", "low"),
    ],
)
def test_bug_lifecycle_command_is_idempotent_when_bug_already_in_destination_state(
    monkeypatch, tmp_path, command, state, bug_id, severity
):
    """Lifecycle command exits zero and preserves bytes when already in destination."""
    from ai_team.cli import app

    bug_path = tmp_path / "project" / "bugs" / state / f"{bug_id}-demo-bug.md"
    _write_bug(bug_path, bug_id, "Demo Bug", severity, state)
    before_bytes = bug_path.read_bytes()

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["bug", command, bug_id])

    assert result.exit_code == 0
    assert f"already in {state}" in result.output
    assert bug_path.exists()
    assert bug_path.read_bytes() == before_bytes


@pytest.mark.parametrize("command", ["start", "resolve"])
def test_bug_lifecycle_command_reports_not_found_and_names_searched_folders(
    monkeypatch, tmp_path, command
):
    """Missing bug ID returns non-zero and includes searched bug state folders."""
    from ai_team.cli import app

    for state in ("open", "in-progress", "resolved"):
        (tmp_path / "project" / "bugs" / state).mkdir(parents=True, exist_ok=True)

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["bug", command, "B-999"])

    assert result.exit_code != 0
    assert "not found" in result.stderr.lower()
    assert "bugs/open" in result.stderr
    assert "bugs/in-progress" in result.stderr
    assert "bugs/resolved" in result.stderr
