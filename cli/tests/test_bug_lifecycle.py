"""Tests for bug lifecycle commands on field-based state (S-006).

Bugs live in the local tracker; every transition rewrites the frontmatter
``status`` in place and never moves the file.
"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_team.core.fs import read_artifact
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

Bug body.
"""


def _write_bug(tmp_path: Path, bug_id: str, status: str) -> Path:
    (tmp_path / "ai-team").mkdir(exist_ok=True)
    path = tmp_path / ".ai-team" / "tracker" / "bugs" / f"{bug_id}-demo-bug.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        BUG_TEMPLATE.format(
            id=bug_id, title="Demo Bug", severity="high", status=status
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    ("command", "from_status", "to_status"),
    [("start", "open", "in-progress"), ("resolve", "in-progress", "resolved")],
)
def test_bug_transition_updates_status_in_place(
    monkeypatch, tmp_path, command, from_status, to_status
):
    """Bug transitions set the status field and leave the file where it is."""
    from ai_team.cli import app

    path = _write_bug(tmp_path, "B-007", from_status)

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["bug", command, "B-007"])

    assert result.exit_code == 0, result.output
    assert path.exists()
    assert parse_bug(path).status == to_status


@pytest.mark.parametrize(
    ("command", "status"), [("start", "in-progress"), ("resolve", "resolved")]
)
def test_bug_lifecycle_command_is_idempotent_when_already_in_destination_status(
    monkeypatch, tmp_path, command, status
):
    """A bug already in the target status is left byte-for-byte unchanged."""
    from ai_team.cli import app

    path = _write_bug(tmp_path, "B-009", status)
    before_bytes = path.read_bytes()

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["bug", command, "B-009"])

    assert result.exit_code == 0
    assert f"already in {status}" in result.output
    assert path.read_bytes() == before_bytes


@pytest.mark.parametrize(
    ("command", "status"), [("start", "resolved"), ("resolve", "open")]
)
def test_bug_lifecycle_command_rejects_unexpected_source_status(
    monkeypatch, tmp_path, command, status
):
    """A shortcut command refuses a bug that is not in its expected source status."""
    from ai_team.cli import app

    path = _write_bug(tmp_path, "B-010", status)

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["bug", command, "B-010"])

    assert result.exit_code != 0
    assert f"is '{status}'" in result.stderr
    assert parse_bug(path).status == status


def test_bug_set_status_records_reason(monkeypatch, tmp_path):
    """`bug set-status` sets any allowed status and logs an optional reason."""
    from ai_team.cli import app

    path = _write_bug(tmp_path, "B-011", "resolved")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app, ["bug", "set-status", "B-011", "open", "--reason", "regressed again"]
    )

    assert result.exit_code == 0, result.output
    assert parse_bug(path).status == "open"
    _, body = read_artifact(path, "bug")
    assert "Status set to open: regressed again" in body


@pytest.mark.parametrize("command", ["start", "resolve"])
def test_bug_lifecycle_command_reports_not_found_and_names_tracker_folder(
    monkeypatch, tmp_path, command
):
    """A missing bug ID returns non-zero and names the tracker bugs folder."""
    from ai_team.cli import app

    (tmp_path / "ai-team").mkdir()

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["bug", command, "B-999"])

    assert result.exit_code != 0
    assert "not found" in result.stderr.lower()
    assert ".ai-team/tracker/bugs" in result.stderr
