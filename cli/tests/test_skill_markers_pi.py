"""Pi rendering of skill markers and derived pi headers (S-005 marker contract)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

CLI_DIR = Path(__file__).resolve().parents[1]
COMMAND_MAP_PATH = CLI_DIR / "src" / "ai_team" / "init" / "sources" / "command_map.json"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "skill_markers_pi_under_test", CLI_DIR / "scripts" / "skill_markers.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


markers = _load_module()


@pytest.fixture
def command_map() -> dict:
    return json.loads(COMMAND_MAP_PATH.read_text(encoding="utf-8"))


def _pi(text: str, command_map: dict, source: str = "body.md") -> str:
    return markers.render_markers(text, "pi", command_map, source)


# AC-1: call vs mention form, no --json.


def test_command_with_all_required_positionals_renders_call_form(command_map) -> None:
    rendered = _pi(
        'Run `{{ai-team bug new "<title>" --severity "<severity>" --json}}`.',
        command_map,
    )

    assert rendered == (
        "Run the `ai_team` tool call "
        '`{"command": "bug new", "title": "<title>", "severity": "<severity>"}`.'
    )


def test_call_form_drops_json_flag(command_map) -> None:
    rendered = _pi("{{ai-team status --json}}", command_map)

    assert "json" not in rendered
    assert '"command": "status"' in rendered


def test_command_without_required_positionals_always_renders_call_form(
    command_map,
) -> None:
    rendered = _pi("`{{ai-team list tasks --state <state>}}`", command_map)

    assert rendered == (
        'the `ai_team` tool call `{"command": "list tasks", "state": "<state>"}`'
    )


def test_command_missing_required_positional_renders_mention_form(command_map) -> None:
    rendered = _pi("Use `{{ai-team adr new --json}}` to file it.", command_map)

    assert rendered == "Use the `ai_team` tool's `adr new` command to file it."


def test_mention_form_is_not_a_call(command_map) -> None:
    rendered = _pi("{{ai-team task new}}", command_map)

    assert rendered == "the `ai_team` tool's `task new` command"


def test_optional_bracketed_flag_becomes_a_field(command_map) -> None:
    rendered = _pi('{{ai-team adr new "<title>" [--status <status>]}}', command_map)

    assert '"status": "<status>"' in rendered


def test_marker_inside_longer_code_span_is_rejected(command_map) -> None:
    with pytest.raises(markers.MarkerError):
        _pi("`first run {{ai-team status}}`", command_map)


# AC-1 / AC-2: fences.


def test_fence_of_only_command_markers_becomes_prose(command_map) -> None:
    text = (
        "Steps:\n\n```bash\n"
        '{{ai-team task start "<id>"}}\n'
        "{{ai-team status --json}}\n"
        "```\n\nDone."
    )
    rendered = _pi(text, command_map)

    assert "```" not in rendered
    assert rendered == (
        "Steps:\n\n"
        'Call the `ai_team` tool with `{"command": "task start", "id": "<id>"}`.\n'
        'Call the `ai_team` tool with `{"command": "status"}`.\n\n'
        "Done."
    )


def test_fence_mixing_markers_with_shell_lines_fails(command_map) -> None:
    text = "```bash\ncd repo\n{{ai-team status}}\n```\n"

    with pytest.raises(markers.MarkerError, match="fence"):
        _pi(text, command_map, "body.md")


def test_fence_mixing_command_and_noun_markers_fails(command_map) -> None:
    text = "```\n{{ai-team status}}\n{{ai-team-cli|a|b}}\n```\n"

    with pytest.raises(markers.MarkerError, match="fence"):
        _pi(text, command_map)


def test_fence_without_markers_is_left_alone(command_map) -> None:
    text = "```bash\ngit status\n```\n"

    assert _pi(text, command_map) == text


def test_mixed_fence_is_fine_for_claude(command_map) -> None:
    text = "```bash\ncd repo\n{{ai-team status}}\n```\n"

    rendered = markers.render_markers(text, "claude", command_map, "b.md")

    assert rendered == "```bash\ncd repo\nai-team status\n```\n"


# AC-3: flag markers.


def test_flag_marker_outside_backticks_renders_set_field(command_map) -> None:
    rendered = _pi("Pass {{ai-team-flag adr new --supersedes}} to link.", command_map)

    assert rendered == "Pass set `supersedes` to link."


def test_flag_marker_inside_backticks_renders_bare_field(command_map) -> None:
    rendered = _pi("Use `{{ai-team-flag adr new --supersedes}}` here.", command_map)

    assert rendered == "Use `supersedes` here."


def test_flag_marker_uses_camel_case_field_name(command_map) -> None:
    rendered = _pi("`{{ai-team-flag task new --assigned-role}}`", command_map)

    assert rendered == "`assignedRole`"


def test_flag_marker_for_cli_only_flag_is_rejected(command_map) -> None:
    with pytest.raises(markers.MarkerError, match="--json"):
        _pi("{{ai-team-flag adr new --json}}", command_map)


# Noun markers.


def test_noun_marker_renders_pi_text(command_map) -> None:
    rendered = _pi(
        "via {{ai-team-cli|the `ai-team` CLI|the `ai_team` tool}}.", command_map
    )

    assert rendered == "via the `ai_team` tool."


# AC-5: placeholders.


def test_call_form_with_missing_required_flag_field_fails(command_map) -> None:
    with pytest.raises(markers.MarkerError, match="reason"):
        _pi('{{ai-team task block "<id>"}}', command_map)


def test_call_form_with_extra_positional_fails(command_map) -> None:
    with pytest.raises(markers.MarkerError, match="positional"):
        _pi('{{ai-team status "<extra>"}}', command_map)


def test_call_form_flag_without_tool_field_fails(command_map) -> None:
    with pytest.raises(markers.MarkerError, match="--tools"):
        _pi("{{ai-team init --tools <tools>}}", command_map)


def test_call_form_flag_missing_value_fails(command_map) -> None:
    with pytest.raises(markers.MarkerError, match="--severity"):
        _pi('{{ai-team bug new "<title>" --severity}}', command_map)


def test_enum_field_accepts_placeholder_value(command_map) -> None:
    rendered = _pi('{{ai-team bug new "<title>" --severity <severity>}}', command_map)

    assert '"severity": "<severity>"' in rendered


def test_error_names_source_and_marker(command_map) -> None:
    with pytest.raises(markers.MarkerError) as exc:
        _pi('{{ai-team status "<extra>"}}', command_map, "x.md")

    assert "x.md" in str(exc.value)
    assert '{{ai-team status "<extra>"}}' in str(exc.value)


# AC-4: derived pi header.

CLAUDE_HEADER = (
    "---\n"
    "name: demo\n"
    "description: Create things {{ai-team-cli|via the ai-team CLI|via the ai_team tool}}.\n"
    "allowed-tools: Read, Bash, Skill(git-conventions)\n"
    "---"
)


def test_pi_header_keeps_only_name_and_description(command_map) -> None:
    header = markers.derive_pi_header(CLAUDE_HEADER, command_map, "m.toml")

    assert header == (
        "---\nname: demo\ndescription: Create things via the ai_team tool.\n---"
    )


def test_pi_header_omits_allowed_tools(command_map) -> None:
    header = markers.derive_pi_header(CLAUDE_HEADER, command_map, "m.toml")

    assert "allowed-tools" not in header


def test_pi_header_without_description_fails(command_map) -> None:
    with pytest.raises(markers.MarkerError, match="description"):
        markers.derive_pi_header("---\nname: demo\n---", command_map, "m.toml")


def test_pi_header_without_name_fails(command_map) -> None:
    with pytest.raises(markers.MarkerError, match="name"):
        markers.derive_pi_header("---\ndescription: x\n---", command_map, "m.toml")
