"""Tests for T-025: `ai-team init` command."""

from __future__ import annotations

import tomllib

from typer.testing import CliRunner


def test_init_defaults_to_cwd_and_scaffolds_project_claude_and_marker(
    monkeypatch, tmp_path
):
    """`ai-team init --tools claude --no-interactive` scaffolds cwd."""
    from ai_team.cli import app

    target = tmp_path / "repo"
    target.mkdir()
    monkeypatch.chdir(target)

    result = CliRunner().invoke(app, ["init", "--tools", "claude", "--no-interactive"])

    marker = target / ".ai-team.toml"

    assert result.exit_code == 0
    assert (target / "project" / "tasks" / "pending" / ".gitkeep").is_file()
    assert (target / ".claude" / "agents" / "planner.md").is_file()
    assert not (target / "ai-process").exists()
    assert marker.is_file()

    data = tomllib.loads(marker.read_text(encoding="utf-8"))
    assert data["project"]["dir"] == "project"
    assert data["init"]["tools"] == ["claude"]
    assert data["init"]["include_ai_process"] is False
    assert isinstance(data["init"]["framework_version"], str)
    assert data["init"]["framework_version"]
