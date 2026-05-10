from pathlib import Path

import pytest

from ai_team.core.templates import load_template


def test_load_template_task_matches_bundled_source() -> None:
    source_template = (
        Path(__file__).resolve().parents[2]
        / ".claude/skills/new-task/assets/TEMPLATE-task.md"
    )

    assert load_template("task") == source_template.read_text(encoding="utf-8")


@pytest.mark.parametrize("kind", ["task", "bug", "spec", "adr"])
def test_load_template_returns_non_empty_frontmatter_for_each_kind(kind: str) -> None:
    content = load_template(kind)

    assert content
    assert content.startswith("---")


def test_load_template_rejects_unknown_kind_with_supported_kinds() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Unsupported template kind 'unknown'. "
            "Supported kinds: task, bug, spec, adr"
        ),
    ):
        load_template("unknown")
