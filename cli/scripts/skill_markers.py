"""Parse and render the `{{ai-team ...}}` skill markers (S-005 marker contract).

Three marker kinds are recognised, each validated against the command map:

- command: ``{{ai-team <argv>}}``
- flag:    ``{{ai-team-flag <command> <flags>}}``
- noun:    ``{{ai-team-cli|<claude/codex text>|<pi text>}}``

The claude and codex targets emit the marker content verbatim. The pi target
renders the ``ai_team`` tool instructions the marker contract describes, and
``derive_pi_header`` builds a pi skill header from a ``[claude]`` header.
"""

from __future__ import annotations

import json
import re
import shlex
from collections.abc import Mapping
from typing import Any

SUPPORTED_TARGETS = ("claude", "codex", "pi")

_MARKER_PATTERN = re.compile(r"\{\{(.*?)\}\}")
_COMMAND_PREFIX = "ai-team "
_FLAG_PREFIX = "ai-team-flag "
_NOUN_PREFIX = "ai-team-cli|"
_MAX_COMMAND_WORDS = 2
_TOOL_NAME = "ai_team"
_JSON_FLAG = "--json"
_INLINE_MARKER_PATTERN = re.compile(r"(`?)\{\{(.*?)\}\}(`?)")
_FENCE_PATTERN = re.compile(
    r"^(?P<indent>[ \t]*)```[^\n]*\n(?P<body>.*?)^[ \t]*```[ \t]*$",
    re.DOTALL | re.MULTILINE,
)
_FENCE_COMMAND_LINE = re.compile(r"\s*\{\{(ai-team [^}]*)\}\}\s*")


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
    if target == "pi":
        return _render_pi(text, command_map, source)
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
    tokens: list[str], flags_by_command: Mapping[str, Any]
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


def _entries_by_command(command_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["command"]: entry for entry in command_map["commands"]}


def _render_pi(text: str, command_map: dict[str, Any], source: str) -> str:
    entries = _entries_by_command(command_map)
    flags_by_command = _flags_by_command(command_map)

    def with_source(error: MarkerError, marker: str) -> MarkerError:
        return MarkerError(f"{source}: invalid marker {marker}: {error}")

    def render_fence(match: re.Match[str]) -> str:
        body = match.group("body")
        if "{{" not in body:
            return match.group(0)
        lines = [line for line in body.splitlines() if line.strip()]
        argvs = [_FENCE_COMMAND_LINE.fullmatch(line) for line in lines]
        if not all(argvs):
            raise MarkerError(
                f"{source}: code fence mixes markers with other lines; "
                "a pi fence may hold only command markers"
            )
        prose = []
        for command_match in argvs:
            assert command_match is not None
            content = command_match.group(1)
            try:
                form = _command_form(
                    content[len(_COMMAND_PREFIX) :], flags_by_command, entries
                )
            except MarkerError as error:
                raise with_source(error, "{{" + content + "}}") from None
            if form.call is None:
                raise MarkerError(
                    f"{source}: invalid marker {{{{{content}}}}}: a fence line must "
                    "be a complete tool call, but it omits a required positional"
                )
            prose.append(f"{match.group('indent')}Call the {form.call_text()}.")
        return "\n".join(prose)

    def render_inline(match: re.Match[str]) -> str:
        opening, content, closing = match.group(1), match.group(2), match.group(3)
        marker = match.group(0).strip("`")
        line_start = text.rfind("\n", 0, match.start()) + 1
        before = text[line_start : match.start()]
        ticks_before = before.count("`")
        inside_span = (ticks_before + len(opening)) % 2 == 1
        sole_span = bool(opening) and bool(closing) and ticks_before % 2 == 0
        try:
            if content.startswith(_FLAG_PREFIX):
                rendered = _render_pi_flag_marker(
                    content[len(_FLAG_PREFIX) :], entries, inside_span
                )
            elif content.startswith(_NOUN_PREFIX):
                rendered = _render_noun_marker_pi(content[len(_NOUN_PREFIX) :])
            elif content.startswith(_COMMAND_PREFIX):
                form = _command_form(
                    content[len(_COMMAND_PREFIX) :], flags_by_command, entries
                )
                if inside_span and not sole_span:
                    raise MarkerError(
                        "a pi command render contains code spans and cannot sit "
                        "inside a longer inline code span"
                    )
                rendered = form.inline_text()
                if sole_span:
                    return rendered
            else:
                return opening + _render_marker(content, flags_by_command) + closing
        except MarkerError as error:
            raise with_source(error, marker) from None
        return opening + rendered + closing

    without_fences = _FENCE_PATTERN.sub(render_fence, text)
    return _INLINE_MARKER_PATTERN.sub(render_inline, without_fences)


class _CommandForm:
    """A command marker resolved against the command map for pi."""

    def __init__(self, command: str, fields: dict[str, Any] | None) -> None:
        self.command = command
        # ``None`` means mention form: the argv omits a required positional.
        self.call = fields

    def call_text(self) -> str:
        assert self.call is not None
        payload = json.dumps({"command": self.command, **self.call}, ensure_ascii=False)
        return f"`{_TOOL_NAME}` tool with `{payload}`"

    def inline_text(self) -> str:
        if self.call is None:
            return f"the `{_TOOL_NAME}` tool's `{self.command}` command"
        payload = json.dumps({"command": self.command, **self.call}, ensure_ascii=False)
        return f"the `{_TOOL_NAME}` tool call `{payload}`"


def _command_form(
    argv: str,
    flags_by_command: dict[str, set[str]],
    entries: dict[str, dict[str, Any]],
) -> _CommandForm:
    # Reuses the claude/codex validation so unknown commands and flags fail alike.
    _render_command_marker(argv, flags_by_command)
    try:
        tokens = shlex.split(argv)
    except ValueError as error:
        raise MarkerError(f"cannot tokenize '{argv}': {error}") from None
    command, rest = _split_command(tokens, entries)
    entry = entries[command]
    flags = {flag["flag"]: flag for flag in entry["flags"]}
    positional_values, fields = _parse_call_arguments(command, rest, flags)

    required = [p for p in entry["positionals"] if p["required"]]
    if len(positional_values) < len(required):
        return _CommandForm(command, None)
    if len(positional_values) > len(entry["positionals"]):
        raise MarkerError(
            f"command '{command}' takes {len(entry['positionals'])} positional "
            f"argument(s) but the marker gives {len(positional_values)}"
        )
    positional_fields = {
        spec["field"]: value
        for spec, value in zip(entry["positionals"], positional_values)
    }
    all_fields = {**positional_fields, **fields}
    for flag in entry["flags"]:
        if flag["required"] and flag["field"] not in all_fields:
            raise MarkerError(
                f"call form of '{command}' is missing required field '{flag['field']}'"
            )
    return _CommandForm(command, all_fields)


def _strip_brackets(token: str) -> str:
    return token.lstrip("[").rstrip("]")


def _parse_call_arguments(
    command: str, tokens: list[str], flags: dict[str, dict[str, Any]]
) -> tuple[list[str], dict[str, Any]]:
    positionals: list[str] = []
    fields: dict[str, Any] = {}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        name = _flag_name(token)
        if name is None:
            value = _strip_brackets(token)
            if value:
                positionals.append(value)
            continue
        flag = flags[name]
        if name == _JSON_FLAG:
            continue  # The tool always returns structured results.
        if flag["field"] is None:
            raise MarkerError(
                f"flag {name} of '{command}' has no tool field and cannot be "
                "used in a pi tool call"
            )
        if flag["boolean"]:
            fields[flag["field"]] = True
            continue
        if index >= len(tokens) or _flag_name(tokens[index]) is not None:
            raise MarkerError(f"flag {name} of '{command}' needs a value")
        fields[flag["field"]] = _strip_brackets(tokens[index])
        index += 1
    return positionals, fields


def _render_pi_flag_marker(
    body: str, entries: dict[str, dict[str, Any]], inside_span: bool
) -> str:
    flags_by_command = {
        command: {flag["flag"] for flag in entry["flags"]}
        for command, entry in entries.items()
    }
    _render_flag_marker(body, flags_by_command)  # validates command and flags
    command, rest = _split_command(body.split(), entries)
    fields_by_flag = {flag["flag"]: flag["field"] for flag in entries[command]["flags"]}
    names = []
    for flag in rest:
        if fields_by_flag[flag] is None:
            raise MarkerError(f"flag {flag} of '{command}' has no tool field")
        names.append(fields_by_flag[flag])
    if inside_span:
        # Already inside backticks: a nested code span would break the markdown.
        return " ".join(names)
    return "set " + " and ".join(f"`{name}`" for name in names)


def _render_noun_marker_pi(body: str) -> str:
    _render_noun_marker(body)  # validates the two texts
    return body.split("|")[1]


def derive_pi_header(
    claude_header: str, command_map: dict[str, Any], source: str
) -> str:
    """Return the pi skill header derived from a ``[claude]`` header.

    Only ``name`` and ``description`` are kept (ADR-002); markers in the
    description render for pi.
    """
    values: dict[str, str] = {}
    for line in claude_header.splitlines():
        key, separator, value = line.partition(":")
        if separator and key in ("name", "description"):
            values[key] = value.strip()
    for key in ("name", "description"):
        if not values.get(key):
            raise MarkerError(f"{source}: [claude] header has no '{key}' line")
    description = render_markers(values["description"], "pi", command_map, source)
    return f"---\nname: {values['name']}\ndescription: {description}\n---"
