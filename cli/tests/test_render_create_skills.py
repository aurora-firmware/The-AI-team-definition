"""Rendered output of the new-task, new-spec and new-bug skills (S-005 marker contract)."""

from __future__ import annotations

import re
import tomllib

import pytest

from tests.skill_rendering import (
    CLI_ROOT,
    SKILL_SOURCES,
    _command_map,
    _markers_module,
    rendered_skill_body,
    rendered_skill_header,
)

CREATE_SKILLS = ("new-task", "new-spec", "new-bug")
PI_SKILLS = CLI_ROOT.parent / "pi" / "resources" / "skills"
_MARKER = re.compile(r"\{\{.*?\}\}")

_CLAUDE_DESCRIPTIONS = {
    "new-task": "Create a new task via the ai-team CLI",
    "new-spec": "Create a new specification document via the ai-team CLI",
    "new-bug": "Create a new bug report via the ai-team CLI",
}


def _source_text(skill: str, name: str) -> str:
    return (SKILL_SOURCES / skill / name).read_text(encoding="utf-8")


def _rendered_for_pi(skill: str) -> str:
    path = SKILL_SOURCES / skill / "body.md"
    return _markers_module().render_markers(
        path.read_text(encoding="utf-8"), "pi", _command_map(), str(path)
    )


# AC-1: every reference uses a marker.


@pytest.mark.parametrize("skill", CREATE_SKILLS)
def test_body_has_no_cli_reference_outside_a_marker(skill) -> None:
    unmarked = _MARKER.sub("", _source_text(skill, "body.md"))

    assert "ai-team" not in unmarked
    assert not re.search(r"\bCLI\b", unmarked)


@pytest.mark.parametrize("skill", CREATE_SKILLS)
@pytest.mark.parametrize("target", ["claude", "codex"])
def test_header_uses_noun_marker_that_renders_the_original_description(
    skill, target
) -> None:
    metadata = tomllib.loads(_source_text(skill, "metadata.toml"))

    assert "{{ai-team-cli|" in metadata[target]["header"]
    assert f"description: {_CLAUDE_DESCRIPTIONS[skill]}\n" in rendered_skill_header(
        skill, target
    )


# AC-2: claude and codex text reproduces each site exactly.


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_new_task_renders_original_command_and_nouns(target) -> None:
    body = rendered_skill_body("new-task", target)

    assert (
        '`ai-team task new "<title>" --priority <priority> '
        "[--assigned-role <assigned-role>] --json`" in body
    )
    assert "using the CLI response values" in body


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_new_spec_renders_original_command_and_nouns(target) -> None:
    body = rendered_skill_body("new-spec", target)

    assert "using `ai-team spec new --json`, then fill" in body
    assert 'Base: `ai-team spec new "<title>" --json`' in body
    assert '`--author "<author>"`' in body
    assert '`--status "<status>"`' in body
    assert "Build the CLI command:" in body
    assert "NOT passed to the CLI)" in body
    assert "otherwise allow the CLI default." in body
    assert "the CLI has no `--description` flag." in body
    assert "return the CLI response values" in body


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_new_bug_renders_original_command_and_nouns(target) -> None:
    body = rendered_skill_body("new-bug", target)

    assert "using `ai-team bug new --json`." in body
    assert 'Base: `ai-team bug new "<title>" --severity "<severity>" --json`' in body
    assert 'Add `--task "<task>"` only when' in body
    assert "Build the CLI command:" in body


# AC-3: pi skills never refer to the binary.


@pytest.mark.parametrize("skill", CREATE_SKILLS)
def test_pi_skill_has_no_lowercase_ai_team(skill) -> None:
    skill_md = (PI_SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")

    assert "ai-team" not in skill_md


# AC-4: new-task renders task new as a call form with title and priority.


def test_new_task_pi_render_calls_task_new_with_title_and_priority() -> None:
    body = _rendered_for_pi("new-task")

    assert (
        'the `ai_team` tool call `{"command": "task new", "title": "<title>", '
        '"priority": "<priority>", "assignedRole": "<assigned-role>"}`'
    ) in body


def test_new_spec_pi_render_mentions_spec_new_and_calls_it_with_title() -> None:
    body = _rendered_for_pi("new-spec")

    assert "the `ai_team` tool's `spec new` command" in body
    assert (
        'the `ai_team` tool call `{"command": "spec new", "title": "<title>"}`' in body
    )


def test_new_bug_pi_render_calls_bug_new_with_title_and_severity() -> None:
    body = _rendered_for_pi("new-bug")

    assert (
        'the `ai_team` tool call `{"command": "bug new", "title": "<title>", '
        '"severity": "<severity>"}`'
    ) in body


def test_pi_header_of_create_skills_names_the_tool() -> None:
    for skill in CREATE_SKILLS:
        skill_md = (PI_SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")

        assert "via the ai_team tool" in skill_md.split("---")[1]
