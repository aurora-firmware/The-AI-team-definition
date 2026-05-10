"""Tests for T-013: ai-team adr new command."""

from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from ai_team.core.models import parse_adr


def _mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def test_adr_new_creates_decision_with_defaults_and_prints_absolute_path(
    monkeypatch, tmp_path
):
    """`ai-team adr new` creates one decision file and echoes its absolute path."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "decisions")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["adr", "new", "Use event bus"])

    expected = tmp_path / "project" / "decisions" / "ADR-001-use-event-bus.md"

    assert result.exit_code == 0
    assert result.output.strip() == str(expected)

    files = list((tmp_path / "project" / "decisions").glob("*.md"))
    assert files == [expected]

    adr = parse_adr(expected)
    assert adr.id == "ADR-001"
    assert adr.title == "Use event bus"
    assert adr.status == "proposed"
    assert adr.created == date.today().isoformat()
    assert adr.supersedes is None
