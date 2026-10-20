"""B-023: every skill named in `ai-team init` next steps must be scaffolded."""

from __future__ import annotations

import re
from pathlib import Path

from ai_team.commands.init import _next_steps

SKILLS_SOURCE_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "ai_team"
    / "init"
    / "sources"
    / "skills"
)

SLASH_COMMAND_PATTERN = re.compile(r"/([a-z][a-z0-9-]*)")


def _named_skills() -> list[str]:
    names: list[str] = []
    for step in _next_steps():
        names.extend(SLASH_COMMAND_PATTERN.findall(step))
    return names


def test_next_steps_name_at_least_one_skill():
    """Guards the skill-name check below against passing on an empty list."""
    assert _named_skills(), "expected _next_steps() to name at least one /skill"


def test_every_skill_named_in_next_steps_is_scaffolded():
    """A printed /name with no matching skill directory sends new users to an unknown command."""
    missing = [
        name
        for name in _named_skills()
        if not (SKILLS_SOURCE_DIR / name / "body.md").is_file()
    ]

    assert missing == [], (
        f"next steps name skills that are not scaffolded: {missing}; "
        f"expected a directory with body.md under {SKILLS_SOURCE_DIR}"
    )
