"""CR-003: the skill template guide documents supporting-folder export and placeholders."""

from __future__ import annotations

from pathlib import Path

GUIDE = Path(__file__).resolve().parents[2] / "guides" / "skill_template.md"


def guide_text() -> str:
    return GUIDE.read_text(encoding="utf-8")


def test_guide_does_not_point_to_missing_new_task_template() -> None:
    assert "new-task/assets/TEMPLATE-task.md" not in guide_text()


def test_guide_states_which_source_skill_files_are_exported() -> None:
    text = " ".join(guide_text().split())
    assert (
        "only `body.md`, `metadata.toml` and the `assets/`, `references/` and "
        "`scripts/` folders" in text
    )
    assert "cli/src/ai_team/init/sources/skills/<name>/" in text


def test_guide_states_supporting_folders_reach_claude_and_codex_exports() -> None:
    text = " ".join(guide_text().split())
    assert "both the Claude and the Codex export" in text
    assert "next to `SKILL.md`" in text


def test_guide_states_placeholder_filling_and_byte_copy_rules() -> None:
    text = " ".join(guide_text().split())
    assert "`{{project_dir}}`" in text
    assert "`{{integration_branch}}`" in text
    assert "not UTF-8 text" in text
    assert "byte for byte" in text
