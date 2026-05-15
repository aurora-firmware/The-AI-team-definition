"""Tests for T-025: `ai-team init` command."""

from __future__ import annotations

import importlib.metadata
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
    assert "include_ai_process" not in data["init"]
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


def test_init_include_ai_process_is_unknown_option(tmp_path):
    """`--include-ai-process` is not a recognised option and must be rejected."""
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

    assert result.exit_code != 0


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


def test_init_tools_codex_scaffolds_codex_agents_and_skills(tmp_path):
    """`--tools codex` scaffolds .codex/agents/ and .codex/skills/ directories."""
    from ai_team.cli import app

    target = tmp_path / "repo"
    result = CliRunner().invoke(
        app,
        ["init", str(target), "--tools", "codex", "--no-interactive"],
    )

    assert result.exit_code == 0
    assert (target / ".codex" / "agents" / "planner.toml").is_file()
    assert (target / ".codex" / "skills" / "tdd" / "SKILL.md").is_file()
    assert not (target / ".claude").exists()
    assert not (target / "ai-process").exists()


def test_init_tools_codex_scaffolds_real_files_not_symlinks(tmp_path):
    """`--tools codex` writes real files, not symlinks, under .codex/."""
    from ai_team.cli import app

    target = tmp_path / "repo"
    CliRunner().invoke(
        app,
        ["init", str(target), "--tools", "codex", "--no-interactive"],
    )

    agent_file = target / ".codex" / "agents" / "planner.toml"
    skill_file = target / ".codex" / "skills" / "tdd" / "SKILL.md"
    assert agent_file.is_file() and not agent_file.is_symlink()
    assert skill_file.is_file() and not skill_file.is_symlink()


def test_init_tools_all_scaffolds_both_claude_and_codex(tmp_path):
    """`--tools all` scaffolds both .claude/ and .codex/ directories."""
    from ai_team.cli import app

    target = tmp_path / "repo"
    result = CliRunner().invoke(
        app,
        ["init", str(target), "--tools", "all", "--no-interactive"],
    )

    assert result.exit_code == 0
    assert (target / ".claude" / "agents" / "planner.md").is_file()
    assert (target / ".codex" / "agents" / "planner.toml").is_file()
    assert not (target / "ai-process").exists()

    data = __import__("tomllib").loads(
        (target / ".ai-team.toml").read_text(encoding="utf-8")
    )
    assert set(data["init"]["tools"]) == {"claude", "codex"}
    assert "include_ai_process" not in data["init"]


def test_init_interactive_does_not_prompt_for_ai_process_snapshot(tmp_path):
    """Interactive mode does not ask whether to include an ai-process snapshot."""
    from ai_team.cli import app

    target = tmp_path / "repo"
    # Provide "claude\n" to answer the tools prompt; no further input should be needed.
    result = CliRunner().invoke(
        app,
        ["init", str(target)],
        input="claude\n",
    )

    assert result.exit_code == 0
    assert "Include ai-process" not in result.output
