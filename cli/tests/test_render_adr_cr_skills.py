"""Rendered output of the new-adr and change-request skills (S-005 marker contract)."""

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

ADR_CR_SKILLS = ("new-adr", "change-request")
PI_SKILLS = CLI_ROOT.parent / "pi" / "resources" / "skills"
_MARKER = re.compile(r"\{\{.*?\}\}")
_FENCE = re.compile(r"```.*?```", re.DOTALL)

_CLAUDE_DESCRIPTIONS = {
    "new-adr": "Create a new Architecture Decision Record via the ai-team CLI",
    "change-request": "Create a new change-request artifact via the ai-team CLI",
}


def _source_text(skill: str, name: str) -> str:
    return (SKILL_SOURCES / skill / name).read_text(encoding="utf-8")


def _rendered_for_pi(skill: str) -> str:
    path = SKILL_SOURCES / skill / "body.md"
    return _markers_module().render_markers(
        path.read_text(encoding="utf-8"), "pi", _command_map(), str(path)
    )


# AC-1: every reference uses a marker.


@pytest.mark.parametrize("skill", ADR_CR_SKILLS)
def test_body_has_no_cli_reference_outside_a_marker(skill) -> None:
    # A pi fence may hold only command markers, so the Output Format placeholder
    # inside a plain text fence cannot carry a marker and is excluded here.
    unfenced = _FENCE.sub("", _source_text(skill, "body.md"))
    unmarked = _MARKER.sub("", unfenced)

    assert "ai-team" not in unmarked
    assert not re.search(r"\bCLI\b", unmarked)


@pytest.mark.parametrize("skill", ADR_CR_SKILLS)
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
def test_new_adr_renders_original_command_and_nouns(target) -> None:
    body = rendered_skill_body("new-adr", target)

    assert "using `ai-team adr new --json`." in body
    assert 'Base: `ai-team adr new "<title>" --status "<status>" --json`' in body
    assert 'Add `--supersedes "<supersedes>"` only when' in body
    assert "Build the CLI command:" in body
    assert "return the CLI response values" in body


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_change_request_renders_original_command_and_nouns(target) -> None:
    body = rendered_skill_body("change-request", target)

    assert "using `ai-team change-request new --json`, then fill" in body
    assert 'Run `ai-team change-request new "<title>" --json`.' in body
    assert "produced by the CLI." in body
    assert "return the CLI response values." in body
    assert "from the CLI response." in body
    assert "<CLI command result or reason not run>" in body


# AC-3: supersedes is a bare field name, with no nested code span.


def test_new_adr_pi_render_names_supersedes_as_bare_field_in_backticks() -> None:
    body = _rendered_for_pi("new-adr")

    assert '- Add `supersedes "<supersedes>"` only when' in body
    assert "``" not in body


# AC-4: shortened adr new --json introductions render as mention form.


def test_new_adr_pi_render_mentions_adr_new_in_the_introduction() -> None:
    body = _rendered_for_pi("new-adr")

    assert "using the `ai_team` tool's `adr new` command." in body


def test_new_adr_pi_render_calls_adr_new_with_title_and_status() -> None:
    body = _rendered_for_pi("new-adr")

    assert (
        'the `ai_team` tool call `{"command": "adr new", "title": "<title>", '
        '"status": "<status>"}`'
    ) in body


def test_change_request_pi_render_mentions_and_calls_change_request_new() -> None:
    body = _rendered_for_pi("change-request")

    assert "the `ai_team` tool's `change-request new` command" in body
    assert (
        'the `ai_team` tool call `{"command": "change-request new", '
        '"title": "<title>"}`'
    ) in body


# AC-5: pi skills never refer to the binary.


@pytest.mark.parametrize("skill", ADR_CR_SKILLS)
def test_pi_skill_has_no_lowercase_ai_team(skill) -> None:
    skill_md = (PI_SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")

    assert "ai-team" not in skill_md


def test_pi_header_names_the_tool() -> None:
    for skill in ADR_CR_SKILLS:
        skill_md = (PI_SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")

        assert "via the ai_team tool" in skill_md.split("---")[1]
