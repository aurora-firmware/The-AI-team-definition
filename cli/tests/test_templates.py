from pathlib import Path

from ai_team.core.templates import load_template


def test_load_template_task_matches_bundled_source() -> None:
    source_template = (
        Path(__file__).resolve().parents[2]
        / ".claude/skills/new-task/assets/TEMPLATE-task.md"
    )

    assert load_template("task") == source_template.read_text(encoding="utf-8")
