"""B-023 and CR-002: `ai-team init` next steps name only scaffolded skills, in each tool's syntax."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

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
DOLLAR_COMMAND_PATTERN = re.compile(r"\$([a-z][a-z0-9-]*)")

TOOL_COMBINATIONS = [[], ["claude"], ["codex"], ["claude", "codex"]]

SKILL_PURPOSES = [
    ("brainstorm", "to explore the request and constraints."),
    ("spec-breakdown", "to break the approved spec into tasks."),
    ("dev-loop", "to execute tasks through review and integration."),
]


def _named_skills(tools: list[str]) -> list[str]:
    names: list[str] = []
    for step in _next_steps(tools):
        names.extend(SLASH_COMMAND_PATTERN.findall(step))
        names.extend(DOLLAR_COMMAND_PATTERN.findall(step))
    return names


@pytest.mark.parametrize("tools", TOOL_COMBINATIONS)
def test_next_steps_name_at_least_one_skill(tools):
    """Guards the skill-name check below against passing on an empty list."""
    assert _named_skills(tools), f"expected _next_steps({tools}) to name a skill"


@pytest.mark.parametrize("tools", TOOL_COMBINATIONS)
def test_every_skill_named_in_next_steps_is_scaffolded(tools):
    """A printed name with no matching skill directory sends new users to an unknown command."""
    missing = [
        name
        for name in _named_skills(tools)
        if not (SKILLS_SOURCE_DIR / name / "body.md").is_file()
    ]

    assert missing == [], (
        f"next steps name skills that are not scaffolded: {missing}; "
        f"expected a directory with body.md under {SKILLS_SOURCE_DIR}"
    )


def test_next_steps_use_slash_form_only_when_only_claude_is_selected():
    assert _next_steps(["claude"]) == [
        f"Run /{skill} {purpose}" for skill, purpose in SKILL_PURPOSES
    ]


def test_next_steps_use_dollar_form_only_when_only_codex_is_selected():
    assert _next_steps(["codex"]) == [
        f"Run ${skill} {purpose}" for skill, purpose in SKILL_PURPOSES
    ]


def test_next_steps_show_both_forms_when_both_tools_are_selected():
    assert _next_steps(["claude", "codex"]) == [
        f"Run /{skill} (Claude Code) or ${skill} (Codex) {purpose}"
        for skill, purpose in SKILL_PURPOSES
    ]


def test_next_steps_keep_slash_form_when_no_tool_is_selected():
    assert _next_steps([]) == [
        f"Run /{skill} {purpose}" for skill, purpose in SKILL_PURPOSES
    ]
