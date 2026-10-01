"""Rendered output of status-report, dev-loop and bug-loop (S-005 marker contract)."""

from __future__ import annotations

import re

import pytest

from tests.skill_rendering import (
    CLI_ROOT,
    SKILL_SOURCES,
    _command_map,
    _markers_module,
    rendered_skill_body,
)

SKILLS = ("status-report", "dev-loop", "bug-loop")
PI_SKILLS = CLI_ROOT.parent / "pi" / "resources" / "skills"
_MARKER = re.compile(r"\{\{.*?\}\}")


def _source(skill: str) -> str:
    return (SKILL_SOURCES / skill / "body.md").read_text(encoding="utf-8")


def _rendered_for_pi(skill: str) -> str:
    path = SKILL_SOURCES / skill / "body.md"
    return _markers_module().render_markers(
        path.read_text(encoding="utf-8"), "pi", _command_map(), str(path)
    )


def _fences(text: str) -> list[str]:
    return re.findall(r"```[^\n]*\n(.*?)```", text, flags=re.DOTALL)


# AC-1 and AC-4: every reference uses a marker.


@pytest.mark.parametrize("skill", SKILLS)
def test_body_has_no_cli_reference_outside_a_marker(skill) -> None:
    unmarked = _MARKER.sub("", _source(skill))

    assert "ai-team" not in unmarked
    assert not re.search(r"\bCLI\b", unmarked)


@pytest.mark.parametrize("skill", SKILLS)
def test_command_fences_hold_only_command_marker_lines(skill) -> None:
    for fence in _fences(_source(skill)):
        if "{{ai-team " not in fence:
            continue
        for line in filter(str.strip, fence.splitlines()):
            assert re.fullmatch(r"\s*\{\{ai-team [^}]*\}\}\s*", line)


# AC-2: claude and codex text reproduces each site exactly.


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_status_report_renders_original_commands_and_nouns(target) -> None:
    body = rendered_skill_body("status-report", target)

    assert "- **AI team CLI** — `ai-team status` and `ai-team report` are" in body
    assert "Run the CLI status command from the repository root:" in body
    assert "```bash\nai-team status\n```" in body
    assert "Use `ai-team status` output as the inline summary." in body
    assert "Run the CLI report command from the repository root:" in body
    assert "```bash\nai-team report\n```" in body


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_dev_loop_renders_original_commands_and_nouns(target) -> None:
    body = rendered_skill_body("dev-loop", target)

    assert "using the `ai-team` CLI:" in body
    assert "- `ai-team list tasks --state pending` — pending work queue" in body
    assert "pending tasks using: `ai-team list tasks --state pending`." in body
    assert "skill runs `ai-team status`, scans project" in body


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_bug_loop_renders_original_status_command(target) -> None:
    body = rendered_skill_body("bug-loop", target)

    assert "skill runs `ai-team status`, scans project" in body


# AC-3 and AC-4: pi output names the tool, never the binary or the CLI.


@pytest.mark.parametrize("skill", SKILLS)
def test_pi_render_has_no_lowercase_ai_team_or_cli_token(skill) -> None:
    body = _rendered_for_pi(skill)

    assert "ai-team" not in body
    assert not re.search(r"\bCLI\b", body)


def test_status_report_pi_render_calls_status_and_report_as_tool_calls() -> None:
    body = _rendered_for_pi("status-report")

    assert 'Call the `ai_team` tool with `{"command": "status"}`.' in body
    assert 'Call the `ai_team` tool with `{"command": "report"}`.' in body
    assert "- **AI team tool** —" in body


def test_dev_loop_pi_render_lists_pending_tasks_through_the_tool() -> None:
    body = _rendered_for_pi("dev-loop")

    assert "using the `ai_team` tool:" in body
    assert '"command": "list tasks"' in body


@pytest.mark.parametrize("skill", SKILLS)
def test_pi_skill_file_has_no_lowercase_ai_team_or_cli_token(skill) -> None:
    skill_md = (PI_SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")

    assert "ai-team" not in skill_md
    assert not re.search(r"\bCLI\b", skill_md)
