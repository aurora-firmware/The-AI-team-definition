"""The command map must agree with the Typer CLI and the ADR-004 tool contract."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import click
import pytest
import typer

from ai_team.cli import app

COMMAND_MAP_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "ai_team"
    / "init"
    / "sources"
    / "command_map.json"
)

# Required and optional tool fields per leaf command, from the S-005 tool contract.
TOOL_CONTRACT: dict[str, tuple[set[str], set[str]]] = {
    "spec new": ({"title"}, {"author", "status"}),
    "task new": ({"title"}, {"priority", "assignedRole", "spec"}),
    "task start": ({"id"}, set()),
    "task complete": ({"id"}, set()),
    "task unblock": ({"id"}, set()),
    "task block": ({"id", "reason"}, set()),
    "bug new": ({"title"}, {"severity", "task"}),
    "bug start": ({"id"}, set()),
    "bug resolve": ({"id"}, set()),
    "adr new": ({"title"}, {"status", "supersedes"}),
    "change-request new": ({"title"}, set()),
    "list tasks": (set(), {"state"}),
    "list bugs": (set(), {"state"}),
    "list specs": (set(), {"state"}),
    "list adrs": (set(), {"state"}),
    "list change-requests": (set(), set()),
    "show": ({"identifier"}, set()),
    "status": (set(), set()),
    "report": (set(), {"out"}),
    "validate": (
        set(),
        {"all", "tasks", "bugs", "specs", "adrs", "changeRequests"},
    ),
    "archive": (set(), {"olderThan", "dryRun"}),
    "check-layout": (set(), set()),
    "init": (set(), {"path", "force", "dryRun", "createRootGuidance"}),
}

CLI_ONLY_FLAGS = {
    "--json",
    "init --tools",
    "init --no-interactive",
}


def _load_map() -> dict:
    return json.loads(COMMAND_MAP_PATH.read_text(encoding="utf-8"))


def _typer_leaves() -> dict[str, click.Command]:
    leaves: dict[str, click.Command] = {}

    def walk(command: click.Command, path: list[str]) -> None:
        subcommands = getattr(command, "commands", None)
        if subcommands:
            for name, child in subcommands.items():
                walk(child, [*path, name])
        else:
            leaves[" ".join(path)] = command

    walk(typer.main.get_command(app), [])
    return leaves


def _default_text(value: object) -> object:
    if value is None or isinstance(value, bool):
        return value
    return str(value)


def _typer_surface(command: click.Command) -> dict:
    positionals = []
    flags = {}
    for param in command.params:
        if isinstance(param, click.Argument):
            positionals.append(
                {
                    "name": param.name,
                    "required": param.required,
                    "default": _default_text(param.default),
                }
            )
        else:
            flags[param.opts[0]] = {
                "default": _default_text(param.default),
                "choices": (
                    list(param.type.choices)
                    if isinstance(param.type, click.Choice)
                    else None
                ),
                "boolean": bool(param.is_flag),
            }
    return {"positionals": positionals, "flags": flags}


def _map_surface(entry: dict) -> dict:
    return {
        "positionals": [
            {
                "name": p["cliName"],
                "required": p["required"],
                "default": p["default"],
            }
            for p in entry["positionals"]
        ],
        "flags": {
            f["flag"]: {
                "default": f["default"],
                "choices": f["choices"],
                "boolean": f["boolean"],
            }
            for f in entry["flags"]
        },
    }


def _disagreements(command_map: dict) -> list[str]:
    problems: list[str] = []
    leaves = _typer_leaves()
    mapped = {entry["command"]: entry for entry in command_map["commands"]}
    for name in sorted(set(leaves) - set(mapped)):
        problems.append(f"{name}: in Typer but missing from the command map")
    for name in sorted(set(mapped) - set(leaves)):
        problems.append(f"{name}: in the command map but not in Typer")
    for name in sorted(set(leaves) & set(mapped)):
        if _typer_surface(leaves[name]) != _map_surface(mapped[name]):
            problems.append(f"{name}: arguments, flags, defaults or choices differ")
    return problems


def test_command_map_agrees_with_typer_cli() -> None:
    assert _disagreements(_load_map()) == []


def test_every_tool_contract_command_is_mapped_with_its_fields() -> None:
    mapped = {entry["command"]: entry for entry in _load_map()["commands"]}
    assert set(mapped) == set(TOOL_CONTRACT)
    for name, (required, optional) in TOOL_CONTRACT.items():
        entry = mapped[name]
        required_fields = {
            p["field"] for p in entry["positionals"] if p["required"]
        } | {f["field"] for f in entry["flags"] if f["field"] and f["required"]}
        all_fields = {p["field"] for p in entry["positionals"]} | {
            f["field"] for f in entry["flags"] if f["field"]
        }
        assert required_fields == required, name
        assert all_fields - required_fields == optional, name


def test_cli_only_options_have_no_tool_field() -> None:
    for entry in _load_map()["commands"]:
        for flag in entry["flags"]:
            key = (
                "--json"
                if flag["flag"] == "--json"
                else (f"{entry['command']} {flag['flag']}")
            )
            expected_cli_only = key in CLI_ONLY_FLAGS
            assert flag["cliOnly"] is expected_cli_only, key
            assert (flag["field"] is None) is expected_cli_only, key


@pytest.mark.parametrize(
    "mutate",
    [
        lambda m: m["commands"].pop(),
        lambda m: m["commands"].append(
            {"command": "ghost", "positionals": [], "flags": []}
        ),
        lambda m: m["commands"][0]["flags"][0].update(default="changed"),
        lambda m: m["commands"][0]["positionals"][0].update(required=False),
        lambda m: m["commands"][0]["flags"][0].update(choices=["nope"]),
    ],
)
def test_disagreement_with_typer_is_reported(mutate) -> None:
    command_map = copy.deepcopy(_load_map())
    mutate(command_map)
    assert _disagreements(command_map) != []


def test_command_map_holds_no_version_string() -> None:
    text = COMMAND_MAP_PATH.read_text(encoding="utf-8")
    assert not re.search(r"\d+\.\d+\.\d+", text)
    assert "version" not in text.lower()
