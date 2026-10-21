"""CR-003: the skill template guide documents supporting-folder export and placeholders."""

from __future__ import annotations

import re
from pathlib import Path

GUIDE = Path(__file__).resolve().parents[2] / "guides" / "skill_template.md"


def guide_text() -> str:
    return GUIDE.read_text(encoding="utf-8")


def export_rules_text() -> str:
    text = guide_text()
    heading = "### Export Rules for Skills in This Repository"
    start = text.index(heading) + len(heading)
    following = re.search(r"^#{1,3} ", text[start:], flags=re.MULTILINE)
    end = start + following.start() if following else len(text)
    return " ".join(text[start:end].split())


def test_guide_does_not_point_to_missing_new_task_template() -> None:
    assert "new-task/assets/TEMPLATE-task.md" not in guide_text()


def test_guide_states_which_source_skill_files_are_exported() -> None:
    text = export_rules_text()
    assert (
        "only `body.md`, `metadata.toml` and the `assets/`, `references/` and "
        "`scripts/` folders" in text
    )
    assert "cli/src/ai_team/init/sources/skills/<name>/" in text


def test_guide_states_supporting_folders_reach_claude_and_codex_exports() -> None:
    text = export_rules_text()
    assert "both the Claude and the Codex export" in text
    assert "next to `SKILL.md`" in text


def test_guide_states_placeholder_filling_and_byte_copy_rules() -> None:
    text = export_rules_text()
    assert "`{{project_dir}}`" in text
    assert "`{{integration_branch}}`" in text
    assert "not UTF-8 text" in text
    assert "byte for byte" in text
