"""Tests for T-086: structured result for init with an internal empty-tools mode."""

import tomllib
from pathlib import Path

from typer.testing import CliRunner

from ai_team.cli import app
from ai_team.commands.init import init_repository
from ai_team.core.runtime import framework_version


def _outcomes(result) -> dict[str, str]:
    return {
        Path(entry["path"]).name: entry["outcome"]
        for entry in result.payload["root_guidance"]
    }


def test_empty_tool_list_initializes_without_prompting(tmp_path: Path) -> None:
    result = init_repository(
        tmp_path, tools=[], force=False, dry_run=False, create_root_guidance=False
    )

    assert result.status == 0
    assert (tmp_path / "project").is_dir()
    assert not (tmp_path / ".claude").exists()
    assert not (tmp_path / ".codex").exists()


def test_explicit_tool_list_writes_only_selected_tool_scaffold(tmp_path: Path) -> None:
    result = init_repository(
        tmp_path,
        tools=["codex"],
        force=False,
        dry_run=False,
        create_root_guidance=False,
    )

    assert result.status == 0
    assert (tmp_path / ".codex").is_dir()
    assert not (tmp_path / ".claude").exists()


def test_unsupported_tool_returns_error_result(tmp_path: Path) -> None:
    result = init_repository(
        tmp_path,
        tools=["vim"],
        force=False,
        dry_run=False,
        create_root_guidance=False,
    )

    assert result.status == 1
    assert "vim" in result.text()
    assert not (tmp_path / ".ai-team.toml").exists()


def test_empty_tools_writes_empty_init_tools_and_framework_version(
    tmp_path: Path,
) -> None:
    init_repository(
        tmp_path, tools=[], force=False, dry_run=False, create_root_guidance=False
    )

    data = tomllib.loads((tmp_path / ".ai-team.toml").read_text(encoding="utf-8"))
    assert data["init"]["tools"] == []
    assert data["init"]["framework_version"] == framework_version()
    assert data["project"] == {"dir": "project"}


def test_result_lists_written_files_including_marker(tmp_path: Path) -> None:
    result = init_repository(
        tmp_path, tools=[], force=False, dry_run=False, create_root_guidance=False
    )

    files = result.payload["files"]
    assert str(tmp_path / ".ai-team.toml") in files
    assert all(Path(path).is_file() for path in files)
    assert result.payload["dry_run"] is False


def test_root_guidance_created_when_requested(tmp_path: Path) -> None:
    result = init_repository(
        tmp_path, tools=[], force=False, dry_run=False, create_root_guidance=True
    )

    assert _outcomes(result) == {"CLAUDE.md": "created", "AGENTS.md": "created"}
    assert (tmp_path / "CLAUDE.md").is_file()


def test_root_guidance_not_created_when_not_requested(tmp_path: Path) -> None:
    result = init_repository(
        tmp_path, tools=[], force=False, dry_run=False, create_root_guidance=False
    )

    assert _outcomes(result) == {
        "CLAUDE.md": "not-requested",
        "AGENTS.md": "not-requested",
    }
    assert not (tmp_path / "CLAUDE.md").exists()


def test_existing_root_guidance_is_kept_without_force(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("mine", encoding="utf-8")

    result = init_repository(
        tmp_path, tools=[], force=False, dry_run=False, create_root_guidance=True
    )

    assert _outcomes(result)["CLAUDE.md"] == "exists"
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == "mine"


def test_declined_note_text_is_not_part_of_result(tmp_path: Path) -> None:
    result = init_repository(
        tmp_path,
        tools=[],
        force=False,
        dry_run=False,
        create_root_guidance=False,
        confirm_root_guidance=lambda filename: False,
    )

    assert _outcomes(result) == {"CLAUDE.md": "declined", "AGENTS.md": "declined"}
    assert "Note:" not in repr(result)
    assert "add your test and run" not in repr(result)


def test_dry_run_returns_plan_and_writes_nothing(tmp_path: Path) -> None:
    result = init_repository(
        tmp_path, tools=["claude"], force=False, dry_run=True, create_root_guidance=True
    )

    assert result.status == 0
    assert result.payload["dry_run"] is True
    assert str(tmp_path / ".ai-team.toml") in result.payload["files"]
    assert str(tmp_path / ".claude" / "agents") not in result.payload["files"]
    assert list(tmp_path.iterdir()) == []
    assert _outcomes(result) == {
        "CLAUDE.md": "would-write",
        "AGENTS.md": "would-write",
    }


def test_collision_without_force_returns_error_and_writes_nothing(
    tmp_path: Path,
) -> None:
    (tmp_path / ".ai-team.toml").write_text("# existing", encoding="utf-8")

    result = init_repository(
        tmp_path, tools=[], force=False, dry_run=False, create_root_guidance=False
    )

    assert result.status == 1
    assert str(tmp_path / ".ai-team.toml") in result.text()
    assert not (tmp_path / "project").exists()


def test_cli_no_interactive_without_tools_still_fails(tmp_path: Path) -> None:
    result = CliRunner().invoke(app, ["init", str(tmp_path), "--no-interactive"])

    assert result.exit_code == 1
    assert "you must provide --tools" in result.output
    assert list(tmp_path.iterdir()) == []


def test_cli_tools_none_still_initializes_with_empty_tools(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app, ["init", str(tmp_path), "--tools", "none", "--no-interactive"]
    )

    assert result.exit_code == 0
    assert "Initialization complete." in result.output
    data = tomllib.loads((tmp_path / ".ai-team.toml").read_text(encoding="utf-8"))
    assert data["init"]["tools"] == []


def test_cli_prints_declined_note_when_interactive_prompt_declined(
    tmp_path: Path,
) -> None:
    result = CliRunner().invoke(
        app, ["init", str(tmp_path), "--tools", "none"], input="n\nn\n"
    )

    assert result.exit_code == 0
    assert "Note: To help agents run your project" in result.output
