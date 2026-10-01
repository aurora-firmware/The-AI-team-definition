"""Every command and enum value in the command map is covered by a parity fixture.

The command map is the list of leaf commands, their tool fields and their enum
choices (T-094). The parity fixtures are the shared behavioural contract (ADR-004).
A command or enum value with no fixture is untested by both implementations, so
these checks fail and name what is missing.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from tests import parity_support as parity

COMMAND_MAP_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "ai_team"
    / "init"
    / "sources"
    / "command_map.json"
)

Case = dict[str, Any]


def _load_command_map() -> dict[str, Any]:
    return json.loads(COMMAND_MAP_PATH.read_text(encoding="utf-8"))


def _load_cases() -> list[Case]:
    return [
        json.loads((case_dir / parity.CASE_FILE).read_text(encoding="utf-8"))
        for case_dir in parity.discover_cases(parity.FIXTURES_ROOT)
    ]


def _tool_fields(entry: dict[str, Any]) -> set[str]:
    """Return the tool-contract field names of one command map entry."""
    positional_fields = {p["field"] for p in entry["positionals"] if p["field"]}
    flag_fields = {
        f["field"] for f in entry["flags"] if not f["cliOnly"] and f["field"]
    }
    return positional_fields | flag_fields


def missing_commands(command_map: dict[str, Any], cases: list[Case]) -> list[str]:
    covered = {case["command"] for case in cases}
    return [
        entry["command"]
        for entry in command_map["commands"]
        if entry["command"] not in covered
    ]


def missing_enum_values(command_map: dict[str, Any], cases: list[Case]) -> list[str]:
    missing: list[str] = []
    for entry in command_map["commands"]:
        command_cases = [c for c in cases if c["command"] == entry["command"]]
        for flag in entry["flags"]:
            for value in flag["choices"] or []:
                used = any(
                    c["input"].get(flag["field"]) == value for c in command_cases
                )
                if not used:
                    missing.append(f"{entry['command']} {flag['flag']}={value}")
    return missing


def undefined_input_fields(command_map: dict[str, Any], cases: list[Case]) -> list[str]:
    fields_by_command = {
        entry["command"]: _tool_fields(entry) for entry in command_map["commands"]
    }
    problems: list[str] = []
    for case in cases:
        defined = fields_by_command.get(case["command"], set())
        for field in sorted(set(case["input"]) - defined):
            problems.append(f"{case['command']} input field {field!r}")
    return problems


def _sample_case(command: str, **input_fields: Any) -> Case:
    return {"command": command, "input": input_fields}


# --- the real fixtures ------------------------------------------------------


def test_every_leaf_command_has_a_parity_case() -> None:
    assert missing_commands(_load_command_map(), _load_cases()) == []


def test_every_enum_value_appears_in_a_parity_case() -> None:
    assert missing_enum_values(_load_command_map(), _load_cases()) == []


def test_every_parity_case_input_field_is_defined_for_its_command() -> None:
    assert undefined_input_fields(_load_command_map(), _load_cases()) == []


# --- the checks detect gaps -------------------------------------------------


def test_missing_command_is_reported_by_name() -> None:
    command_map = _load_command_map()
    cases = [c for c in _load_cases() if c["command"] != "task block"]

    assert missing_commands(command_map, cases) == ["task block"]


def test_missing_enum_value_is_reported_by_command_flag_and_value() -> None:
    command_map = _load_command_map()
    command_map = copy.deepcopy(command_map)
    bug_new = next(e for e in command_map["commands"] if e["command"] == "bug new")
    severity = next(f for f in bug_new["flags"] if f["flag"] == "--severity")
    severity["choices"].append("catastrophic")

    assert missing_enum_values(command_map, _load_cases()) == [
        "bug new --severity=catastrophic"
    ]


def test_undefined_input_field_is_reported_by_command_and_field() -> None:
    command_map = _load_command_map()
    cases = [*_load_cases(), _sample_case("task start", id="T-001", bogus="x")]

    assert undefined_input_fields(command_map, cases) == [
        "task start input field 'bogus'"
    ]


def test_cli_only_flag_is_not_a_valid_input_field() -> None:
    command_map = _load_command_map()
    cases = [_sample_case("status", json=True)]

    assert undefined_input_fields(command_map, cases) == ["status input field 'json'"]
