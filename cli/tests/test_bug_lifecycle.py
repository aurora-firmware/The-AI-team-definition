"""Tests for T-015: bug lifecycle commands."""

from pathlib import Path

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
