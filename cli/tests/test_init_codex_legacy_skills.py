"""CR-002: `init --force` removes legacy `.codex/skills` framework copies."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from ai_team.cli import app
from ai_team.core.tool_paths import framework_skill_names


def _framework_skill() -> str:
    return framework_skill_names("codex")[0]


def _make_legacy_skill(repo: Path, name: str) -> Path:
    folder = repo / ".codex" / "skills" / name
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text("legacy", encoding="utf-8")
    return folder


def _init(repo: Path, *flags: str, tools: str = "codex"):
    return CliRunner().invoke(
        app, ["init", str(repo), "--tools", tools, "--no-interactive", *flags]
    )


def test_force_removes_legacy_framework_skill_and_reports_it(tmp_path):
    legacy = _make_legacy_skill(tmp_path, _framework_skill())

    result = _init(tmp_path, "--force")

    assert result.exit_code == 0
    assert not legacy.exists()
    assert f"REMOVED: {legacy}" in result.output


def test_force_leaves_user_skill_in_place_and_reports_it(tmp_path):
    mine = _make_legacy_skill(tmp_path, "my-own-skill")

    result = _init(tmp_path, "--force")

    assert result.exit_code == 0
    assert (mine / "SKILL.md").read_text(encoding="utf-8") == "legacy"
    assert f"LEFT IN PLACE: {mine}" in result.output
    assert f"REMOVED: {mine}" not in result.output


def test_force_removes_legacy_skills_folder_when_it_ends_up_empty(tmp_path):
    _make_legacy_skill(tmp_path, _framework_skill())

    result = _init(tmp_path, "--force")

    assert result.exit_code == 0
    assert not (tmp_path / ".codex" / "skills").exists()


def test_force_keeps_legacy_skills_folder_when_user_skill_remains(tmp_path):
    _make_legacy_skill(tmp_path, _framework_skill())
    _make_legacy_skill(tmp_path, "my-own-skill")

    result = _init(tmp_path, "--force")

    assert result.exit_code == 0
    assert (tmp_path / ".codex" / "skills" / "my-own-skill").is_dir()


def test_dry_run_reports_planned_changes_and_leaves_filesystem_unchanged(tmp_path):
    legacy = _make_legacy_skill(tmp_path, _framework_skill())
    mine = _make_legacy_skill(tmp_path, "my-own-skill")

    result = _init(tmp_path, "--force", "--dry-run")

    assert result.exit_code == 0
    assert f"WOULD REMOVE: {legacy}" in result.output
    assert f"LEFT IN PLACE: {mine}" in result.output
    assert (legacy / "SKILL.md").is_file()
    assert (mine / "SKILL.md").is_file()
    assert "REMOVED:" not in result.output.replace("WOULD REMOVE:", "")


def test_without_force_legacy_folders_are_neither_removed_nor_reported(tmp_path):
    legacy = _make_legacy_skill(tmp_path, _framework_skill())

    result = _init(tmp_path)

    assert result.exit_code == 0
    assert legacy.is_dir()
    assert "REMOVED:" not in result.output
    assert "LEFT IN PLACE:" not in result.output
    assert "WOULD REMOVE:" not in result.output


def test_dry_run_without_force_does_not_report_legacy_folders(tmp_path):
    _make_legacy_skill(tmp_path, _framework_skill())

    result = _init(tmp_path, "--dry-run")

    assert "WOULD REMOVE:" not in result.output
    assert "LEFT IN PLACE:" not in result.output


def test_force_without_codex_never_touches_legacy_folders(tmp_path):
    legacy = _make_legacy_skill(tmp_path, _framework_skill())

    result = _init(tmp_path, "--force", tools="claude")

    assert result.exit_code == 0
    assert legacy.is_dir()
    assert "REMOVED:" not in result.output
    assert "LEFT IN PLACE:" not in result.output


def test_force_unlinks_framework_named_symlink_and_keeps_its_target(tmp_path):
    target = tmp_path / "elsewhere" / _framework_skill()
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text("mine", encoding="utf-8")
    link = tmp_path / ".codex" / "skills" / _framework_skill()
    link.parent.mkdir(parents=True)
    link.symlink_to(target, target_is_directory=True)

    result = _init(tmp_path, "--force")

    assert result.exit_code == 0
    assert not link.is_symlink()
    assert (target / "SKILL.md").read_text(encoding="utf-8") == "mine"
    assert f"REMOVED: {link}" in result.output
    assert (tmp_path / ".ai-team.toml").exists()


def test_force_removes_legacy_framework_skill_when_tools_are_claude_and_codex(
    tmp_path,
):
    legacy = _make_legacy_skill(tmp_path, _framework_skill())

    result = _init(tmp_path, "--force", tools="claude,codex")

    assert result.exit_code == 0
    assert not legacy.exists()
    assert f"REMOVED: {legacy}" in result.output


def test_force_keeps_legacy_skills_folder_when_stray_file_remains(tmp_path):
    _make_legacy_skill(tmp_path, _framework_skill())
    stray = tmp_path / ".codex" / "skills" / "notes.txt"
    stray.write_text("keep", encoding="utf-8")

    result = _init(tmp_path, "--force")

    assert result.exit_code == 0
    assert stray.read_text(encoding="utf-8") == "keep"
