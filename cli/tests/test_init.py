"""Tests for T-025: `ai-team init` command."""

from __future__ import annotations

import tomllib

import importlib.metadata

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


def test_init_scaffolds_explicit_target_path_with_claude_and_marker(tmp_path):
    """`ai-team init <path> --tools claude --no-interactive` scaffolds target path."""
    from ai_team.cli import app

    target = tmp_path / "repo"
    result = CliRunner().invoke(
        app,
        ["init", str(target), "--tools", "claude", "--no-interactive"],
    )

    marker = target / ".ai-team.toml"
    assert result.exit_code == 0
    assert (target / "project" / "bugs" / "open" / ".gitkeep").is_file()
    assert (target / ".claude" / "skills" / "brainstorm" / "SKILL.md").is_file()
    assert marker.is_file()
    assert not (target / "ai-process").exists()


def test_init_refuses_to_overwrite_when_force_is_not_set(monkeypatch, tmp_path):
    """Init exits non-zero and does not write any files when collisions exist."""
    from ai_team.cli import app

    target = tmp_path / "repo"
    target.mkdir()

    existing = target / "project" / "specs" / ".gitkeep"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("occupied\n", encoding="utf-8")

    monkeypatch.chdir(target)
    result = CliRunner().invoke(app, ["init", "--tools", "claude", "--no-interactive"])

    assert result.exit_code != 0
    assert existing.read_text(encoding="utf-8") == "occupied\n"
    assert not (target / ".claude" / "agents" / "planner.md").exists()
    assert not (target / ".ai-team.toml").exists()


def test_init_dry_run_lists_files_and_writes_nothing(tmp_path):
    """Dry-run reports planned writes but does not create files or directories."""
    from ai_team.cli import app

    target = tmp_path / "new-repo"
    result = CliRunner().invoke(
        app,
        [
            "init",
            str(target),
            "--tools",
            "claude",
            "--no-interactive",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "WOULD WRITE:" in result.output
    assert str(target / "project" / "tasks" / "pending" / ".gitkeep") in result.output
    assert str(target / ".claude" / "agents" / "planner.md") in result.output
    assert str(target / ".ai-team.toml") in result.output
    assert not target.exists()


def test_init_include_ai_process_copies_snapshot_and_records_marker(tmp_path):
    """`--include-ai-process` copies ai-process and records the marker flag."""
    from ai_team.cli import app

    target = tmp_path / "repo"
    result = CliRunner().invoke(
        app,
        [
            "init",
            str(target),
            "--tools",
            "claude",
            "--no-interactive",
            "--include-ai-process",
        ],
    )

    marker = target / ".ai-team.toml"
    assert result.exit_code == 0
    assert (target / "ai-process" / "processes" / "workflow-overview.md").is_file()
    data = tomllib.loads(marker.read_text(encoding="utf-8"))
    assert data["init"]["include_ai_process"] is True
    assert data["init"]["tools"] == ["claude"]
    assert data["init"]["framework_version"] == importlib.metadata.version("ai-team")


def test_init_force_allows_overwriting_existing_files(monkeypatch, tmp_path):
    """`--force` permits init to overwrite scaffold destination files."""
    from ai_team.cli import app

    target = tmp_path / "repo"
    target.mkdir()
    existing = target / "project" / "specs" / ".gitkeep"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("occupied\n", encoding="utf-8")

    marker = target / ".ai-team.toml"
    marker.write_text("occupied = true\n", encoding="utf-8")

    monkeypatch.chdir(target)
    result = CliRunner().invoke(
        app,
        ["init", "--tools", "claude", "--no-interactive", "--force"],
    )

    assert result.exit_code == 0
    assert existing.read_text(encoding="utf-8") == ""
    assert (target / ".claude" / "skills" / "tdd" / "SKILL.md").is_file()
    data = tomllib.loads(marker.read_text(encoding="utf-8"))
    assert data["project"]["dir"] == "project"
