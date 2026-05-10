"""Tests for T-012: ai-team spec new command."""

from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from ai_team.core.models import parse_spec


def _mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def test_spec_new_creates_spec_with_defaults_and_prints_absolute_path(
    monkeypatch, tmp_path
):
    """`ai-team spec new` creates one spec file with default frontmatter values."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "specs")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["spec", "new", "Launch Plan"])

    expected = tmp_path / "project" / "specs" / "launch-plan.md"

    assert result.exit_code == 0
    assert result.output.strip() == str(expected)

    files = list((tmp_path / "project" / "specs").glob("*.md"))
    assert files == [expected]

    spec = parse_spec(expected)
    assert spec.title == "Launch Plan"
    assert spec.version == "0.1"
    assert spec.status == "draft"
    assert spec.created == date.today().isoformat()
    assert spec.author == "planner"

    content = expected.read_text(encoding="utf-8")
    assert "id: S-001" in content
