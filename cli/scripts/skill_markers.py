"""Parse and render the `{{ai-team ...}}` skill markers (S-005 marker contract).

Three marker kinds are recognised, each validated against the command map:

- command: ``{{ai-team <argv>}}``
- flag:    ``{{ai-team-flag <command> <flags>}}``
- noun:    ``{{ai-team-cli|<claude/codex text>|<pi text>}}``

Only the claude and codex targets are rendered here; both emit the marker
content verbatim.
"""

from __future__ import annotations

import re
from typing import Any

SUPPORTED_TARGETS = ("claude", "codex")

_MARKER_PATTERN = re.compile(r"\{\{(.*?)\}\}")
_COMMAND_PREFIX = "ai-team "
_FLAG_PREFIX = "ai-team-flag "
_NOUN_PREFIX = "ai-team-cli|"
_MAX_COMMAND_WORDS = 2


class MarkerError(ValueError):
    """A marker is of an unknown kind or its content does not parse."""


def render_markers(
    text: str, target: str, command_map: dict[str, Any], source: str
) -> str:
    """Return ``text`` with every marker rendered for ``target``.

    ``source`` names the file the text came from and is used in error messages.
    """
    if target not in SUPPORTED_TARGETS:
        raise ValueError(
            f"Cannot render markers for target '{target}' "
            f"(supported: {', '.join(SUPPORTED_TARGETS)})"
        )
    flags_by_command = _flags_by_command(command_map)

    def render(match: re.Match[str]) -> str:
        marker = match.group(0)
        try:
            return _render_marker(match.group(1), flags_by_command)
        except MarkerError as error:
            raise MarkerError(f"{source}: invalid marker {marker}: {error}") from None

    return _MARKER_PATTERN.sub(render, text)


def _flags_by_command(command_map: dict[str, Any]) -> dict[str, set[str]]:
    return {
        entry["command"]: {flag["flag"] for flag in entry["flags"]}
        for entry in command_map["commands"]
    }


def _render_marker(content: str, flags_by_command: dict[str, set[str]]) -> str:
    # Check the longer prefixes first: "ai-team-flag " and "ai-team-cli|" both
    # begin with "ai-team".
    if content.startswith(_FLAG_PREFIX):
        return _render_flag_marker(content[len(_FLAG_PREFIX) :], flags_by_command)
    if content.startswith(_NOUN_PREFIX):
        return _render_noun_marker(content[len(_NOUN_PREFIX) :])
    if content.startswith(_COMMAND_PREFIX):
        return _render_command_marker(content[len(_COMMAND_PREFIX) :], flags_by_command)
    raise MarkerError(
        "unknown marker kind; expected 'ai-team ', 'ai-team-flag ' or 'ai-team-cli|'"
    )


def _split_command(
    tokens: list[str], flags_by_command: dict[str, set[str]]
) -> tuple[str, list[str]]:
    for word_count in range(min(_MAX_COMMAND_WORDS, len(tokens)), 0, -1):
        command = " ".join(tokens[:word_count])
        if command in flags_by_command:
            return command, tokens[word_count:]
    raise MarkerError(f"unknown command in '{' '.join(tokens)}'")


def _flag_name(token: str) -> str | None:
    """Return the flag name of a token such as ``[--status`` or ``--x=1``."""
    stripped = token.lstrip("[").rstrip("]")
    if not stripped.startswith("--"):
        return None
    return stripped.split("=", maxsplit=1)[0]


def _render_command_marker(argv: str, flags_by_command: dict[str, set[str]]) -> str:
    tokens = argv.split()
    if not tokens:
        raise MarkerError("command marker has no command")
    command, rest = _split_command(tokens, flags_by_command)
    for token in rest:
        name = _flag_name(token)
        if name is not None and name not in flags_by_command[command]:
            raise MarkerError(f"flag {name} is not defined for command '{command}'")
    return _COMMAND_PREFIX + argv


def _render_flag_marker(body: str, flags_by_command: dict[str, set[str]]) -> str:
    tokens = body.split()
    command, rest = _split_command(tokens, flags_by_command)
    if not rest:
        raise MarkerError(f"flag marker names no flags for command '{command}'")
    for token in rest:
        if not token.startswith("--"):
            raise MarkerError(f"'{token}' is not a flag")
        if token not in flags_by_command[command]:
            raise MarkerError(f"flag {token} is not defined for command '{command}'")
    return " ".join(rest)


def _render_noun_marker(body: str) -> str:
    parts = body.split("|")
    if len(parts) != 2 or not all(part.strip() for part in parts):
        raise MarkerError(
            "noun marker needs exactly two non-empty texts: "
            "{{ai-team-cli|<claude/codex text>|<pi text>}}"
        )
    return parts[0]
