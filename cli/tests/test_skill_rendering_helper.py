"""Coverage for the shared helper that renders skill sources for test assertions."""

from __future__ import annotations

import pytest

from tests.skill_rendering import (
    SCAFFOLDS,
    rendered_skill_body,
    rendered_skill_header,
    rendered_skill_text,
)


@pytest.mark.parametrize("tool", ["claude", "codex"])
def test_rendered_skill_text_matches_generated_scaffold(tool: str) -> None:
    scaffold = (SCAFFOLDS / tool / "skills" / "tdd" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert rendered_skill_text("tdd", tool) == scaffold


@pytest.mark.parametrize("tool", ["claude", "codex"])
def test_rendered_skill_text_is_header_then_body(tool: str) -> None:
    header = rendered_skill_header("tdd", tool)
    body = rendered_skill_body("tdd", tool)

    assert header.startswith("---\nname: tdd\n")
    assert rendered_skill_text("tdd", tool) == header + "\n\n" + body


def test_rendered_skill_body_rejects_unknown_tool() -> None:
    with pytest.raises(ValueError, match="pi"):
        rendered_skill_body("tdd", "pi")
