"""Coverage contract for the artifact-creation parity cases (S-005 SC-3, SC-4).

The fixtures are the contract; these tests only guard that the seeded set keeps
covering every creation command and every enum value. Running the cases against
the Python implementation is done by ``test_parity_fixtures.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests import parity_support as parity

CREATION_COMMANDS = ("spec new", "task new", "bug new", "adr new", "change-request new")

# command -> input field -> every value the CLI accepts for it
ENUM_VALUES: dict[str, dict[str, set[str]]] = {
    "spec new": {
        "status": {"draft", "review", "approved", "superseded"},
        "author": {"planner", "architect", "developer", "human"},
    },
    "task new": {
        "priority": {"critical", "high", "medium", "low"},
        "assignedRole": {
            "unassigned",
            "planner",
            "architect",
            "developer",
            "reviewer",
            "integrator",
        },
    },
    "bug new": {"severity": {"critical", "high", "medium", "low"}},
    "adr new": {"status": {"proposed", "accepted", "superseded"}},
}


def _cases() -> list[tuple[Path, dict, list[dict], list[dict]]]:
    loaded = []
    for case_dir in parity.discover_cases(parity.FIXTURES_ROOT):
        definition = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
        before = json.loads((case_dir / "before.json").read_text(encoding="utf-8"))
        after = json.loads((case_dir / "after.json").read_text(encoding="utf-8"))
        loaded.append((case_dir, definition, before, after))
    return loaded


def _for_command(command: str) -> list[tuple[Path, dict, list[dict], list[dict]]]:
    return [case for case in _cases() if case[1]["command"] == command]


@pytest.mark.parametrize("command", CREATION_COMMANDS)
def test_every_creation_command_has_a_success_and_a_case_dir_named_for_it(
    command: str,
) -> None:
    cases = _for_command(command)

    assert any(c[1]["expected"]["status"] == 0 for c in cases)
    slug = command.replace(" ", "-")
    assert all(c[0].name.startswith(f"{slug}--") for c in cases)


@pytest.mark.parametrize(
    ("command", "field"),
    [(cmd, field) for cmd, fields in ENUM_VALUES.items() for field in fields],
)
def test_every_enum_value_appears_in_a_case_input(command: str, field: str) -> None:
    seen = {
        c[1]["input"][field] for c in _for_command(command) if field in c[1]["input"]
    }

    assert ENUM_VALUES[command][field] <= seen


@pytest.mark.parametrize(
    ("command", "field"),
    [
        ("task new", "spec"),
        ("bug new", "task"),
        ("adr new", "supersedes"),
    ],
)
def test_optional_reference_is_covered_both_present_and_absent(
    command: str, field: str
) -> None:
    inputs = [c[1]["input"] for c in _for_command(command)]

    assert any(field in i for i in inputs)
    assert any(field not in i for i in inputs)


def test_title_cases_cover_unicode_punctuation_and_a_yaml_folding_length() -> None:
    titles = [
        c[1]["input"]["title"] for name in CREATION_COMMANDS for c in _for_command(name)
    ]

    assert any(not title.isascii() for title in titles)
    assert any(any(ch in title for ch in ":#\"'&*[]{}|>%@`") for title in titles)
    assert any(len(title) > 120 for title in titles)


def test_id_allocation_cases_cover_gaps_and_archived_or_completed_only_ids() -> None:
    def before_paths(command: str) -> list[str]:
        return [e["path"] for c in _for_command(command) for e in c[2]]

    assert any("specs/archive/" in p for p in before_paths("spec new"))
    assert any("tasks/completed/" in p for p in before_paths("task new"))
    assert any("bugs/resolved/" in p for p in before_paths("bug new"))


def test_a_task_new_case_starts_with_the_python_lock_sentinel() -> None:
    task_befores = [c[2] for c in _for_command("task new")]

    assert any(
        entry["path"] == "project/.ai-team.lock"
        for before in task_befores
        for entry in before
    )


@pytest.mark.parametrize("command", CREATION_COMMANDS)
def test_an_artifact_exists_or_error_case_exists_for_reachable_commands(
    command: str,
) -> None:
    errors = [c for c in _for_command(command) if c[1]["expected"]["status"] != 0]

    assert errors, f"{command} has no error case"
    assert all("already exists" in c[1]["expected"]["message"] for c in errors)
