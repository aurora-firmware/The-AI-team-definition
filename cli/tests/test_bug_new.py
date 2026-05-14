"""Tests for T-011: ai-team bug new command."""

import json
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from ai_team.core.models import parse_bug


def _mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def test_bug_new_creates_open_bug_with_defaults_and_prints_absolute_path(
    monkeypatch, tmp_path
):
    """`ai-team bug new` creates one open bug file and echoes its absolute path."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "bugs" / "open")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["bug", "new", "Crash on launch"])

    expected = tmp_path / "project" / "bugs" / "open" / "B-001-crash-on-launch.md"

    assert result.exit_code == 0
    assert result.output.strip() == str(expected)

    files = list((tmp_path / "project" / "bugs" / "open").glob("*.md"))
    assert files == [expected]

    bug = parse_bug(expected)
    assert bug.id == "B-001"
    assert bug.title == "Crash on launch"
    assert bug.severity == "medium"
    assert bug.status == "open"
    assert bug.created == date.today().isoformat()
    assert bug.task is None


def test_bug_new_supports_custom_flags_and_json_output(monkeypatch, tmp_path):
    """`bug new --json` emits id/path and writes frontmatter from supplied flags."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "bugs" / "open")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "bug",
            "new",
            "Fix auth race",
            "--severity",
            "critical",
            "--task",
            "T-011",
            "--json",
        ],
    )

    expected = tmp_path / "project" / "bugs" / "open" / "B-001-fix-auth-race.md"
    payload = json.loads(result.output)

    assert result.exit_code == 0
    assert payload == {"id": "B-001", "path": str(expected)}
    assert "┏" not in result.output

    bug = parse_bug(expected)
    assert bug.id == "B-001"
    assert bug.title == "Fix auth race"
    assert bug.severity == "critical"
    assert bug.status == "open"
    assert bug.created == date.today().isoformat()
    assert bug.task == "T-011"


def test_bug_new_refuses_to_overwrite_when_allocated_path_exists(monkeypatch, tmp_path):
    """Existing output path causes non-zero exit and preserves file bytes."""
    from ai_team.cli import app

    open_folder = tmp_path / "project" / "bugs" / "open"
    _mkdir(open_folder)

    existing = open_folder / "B-001-crash-on-launch.md"
    existing.write_text("existing bytes\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("ai_team.commands.bug.next_bug_id", lambda _root: "B-001")
    result = CliRunner().invoke(app, ["bug", "new", "Crash on launch"])

    assert result.exit_code != 0
    assert "already exists" in result.stderr.lower()
    assert existing.read_text(encoding="utf-8") == "existing bytes\n"


def test_bug_new_substitutes_body_h1_with_provided_title(monkeypatch, tmp_path):
    """`bug new` replaces the `# [Bug Title]` body placeholder with the given title."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "bugs" / "open")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["bug", "new", "Crash on startup"])

    assert result.exit_code == 0

    expected = tmp_path / "project" / "bugs" / "open" / "B-001-crash-on-startup.md"
    content = expected.read_text(encoding="utf-8")

    assert "# Crash on startup" in content
    assert "# [Bug Title]" not in content
