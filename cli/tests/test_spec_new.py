"""Tests for T-012: ai-team spec new command."""

import json
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


def test_spec_new_supports_custom_flags_and_json_output(monkeypatch, tmp_path):
    """`spec new --json` emits id/path and writes frontmatter from supplied flags."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "specs")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "spec",
            "new",
            "Auth Spec",
            "--author",
            "architect",
            "--status",
            "review",
            "--json",
        ],
    )

    expected = tmp_path / "project" / "specs" / "auth-spec.md"
    payload = json.loads(result.output)

    assert result.exit_code == 0
    assert payload == {"id": "S-001", "path": str(expected)}
    assert "┏" not in result.output

    spec = parse_spec(expected)
    assert spec.title == "Auth Spec"
    assert spec.version == "0.1"
    assert spec.status == "review"
    assert spec.created == date.today().isoformat()
    assert spec.author == "architect"

    content = expected.read_text(encoding="utf-8")
    assert "id: S-001" in content


def test_spec_new_refuses_to_overwrite_when_allocated_path_exists(
    monkeypatch, tmp_path
):
    """Existing output path causes non-zero exit and preserves file bytes."""
    from ai_team.cli import app

    specs = tmp_path / "project" / "specs"
    _mkdir(specs)

    existing = specs / "launch-plan.md"
    existing.write_text("existing bytes\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["spec", "new", "Launch Plan"])

    assert result.exit_code != 0
    assert "already exists" in result.stderr.lower()
    assert existing.read_text(encoding="utf-8") == "existing bytes\n"


def test_spec_new_substitutes_body_h1_with_provided_title(monkeypatch, tmp_path):
    """`spec new` replaces the body H1 placeholder with the provided title."""
    from ai_team.cli import app

    _mkdir(tmp_path / "project" / "specs")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["spec", "new", "My New Spec"])

    assert result.exit_code == 0

    expected = tmp_path / "project" / "specs" / "my-new-spec.md"
    content = expected.read_text(encoding="utf-8")

    assert "# My New Spec" in content
    assert "# [Specification Title]" not in content
