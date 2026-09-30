"""Coverage contract for the lifecycle-transition parity cases (S-005 SC-3, SC-4).

The fixtures are the contract; these tests only guard that the seeded set keeps
covering every transition command: a valid case, every invalid source state, the
already-in-destination no-op and not-found. Running the cases against the Python
implementation is done by ``test_parity_fixtures.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests import parity_support as parity

# command -> (destination folder, every other state folder that is not a valid source)
TASK_FOLDERS = ("pending", "in-progress", "completed", "blocked")
BUG_FOLDERS = ("open", "in-progress", "resolved")

# command -> (artifact kind, states a valid transition starts from, destination state)
TRANSITIONS: dict[str, tuple[str, tuple[str, ...], str]] = {
    "task start": ("tasks", ("pending",), "in-progress"),
    "task complete": ("tasks", ("in-progress",), "completed"),
    "task unblock": ("tasks", ("blocked",), "in-progress"),
    "task block": (
        "tasks",
        ("pending", "in-progress", "completed", "blocked"),
        "blocked",
    ),
    "bug start": ("bugs", ("open",), "in-progress"),
    "bug resolve": ("bugs", ("in-progress",), "resolved"),
}


def _cases_for(command: str) -> list[tuple[Path, dict, list[dict], list[dict]]]:
    loaded = []
    for case_dir in parity.discover_cases(parity.FIXTURES_ROOT):
        definition = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
        if definition["command"] != command:
            continue
        before = json.loads((case_dir / "before.json").read_text(encoding="utf-8"))
        after = json.loads((case_dir / "after.json").read_text(encoding="utf-8"))
        loaded.append((case_dir, definition, before, after))
    return loaded


def _artifact_folders(tree: list[dict], kind: str) -> set[str]:
    """State folders under ``project/<kind>/`` that hold an artifact file."""
    prefix = f"project/{kind}/"
    return {
        entry["path"][len(prefix) :].split("/")[0]
        for entry in tree
        if entry["type"] == "file" and entry["path"].startswith(prefix)
    }


@pytest.mark.parametrize("command", TRANSITIONS)
def test_every_lifecycle_command_has_a_valid_case_per_source_state(
    command: str,
) -> None:
    kind, sources, destination = TRANSITIONS[command]
    cases = _cases_for(command)

    for source in sources:
        if source == destination:
            continue
        moved = [
            c
            for c in cases
            if c[3] != c[2]
            and c[1]["expected"]["status"] == 0
            and source in _artifact_folders(c[2], kind)
            and destination in _artifact_folders(c[3], kind)
        ]
        assert moved, f"{command} has no valid case from {source}"


@pytest.mark.parametrize("command", TRANSITIONS)
def test_every_lifecycle_command_case_dir_is_named_for_it(command: str) -> None:
    slug = command.replace(" ", "-")

    assert all(c[0].name.startswith(f"{slug}--") for c in _cases_for(command))


@pytest.mark.parametrize("command", TRANSITIONS)
def test_every_invalid_source_state_has_a_not_found_case(command: str) -> None:
    kind, sources, destination = TRANSITIONS[command]
    all_states = TASK_FOLDERS if kind == "tasks" else BUG_FOLDERS
    invalid = set(all_states) - set(sources) - {destination}
    not_found = [
        c
        for c in _cases_for(command)
        if "not found" in c[1]["expected"].get("message", "")
    ]

    for state in invalid:
        assert any(
            state in _artifact_folders(c[2], kind) and c[3] == c[2] for c in not_found
        ), f"{command} has no invalid-source case for {state}"


@pytest.mark.parametrize("command", TRANSITIONS)
def test_already_in_destination_reports_unchanged_and_leaves_the_tree_alone(
    command: str,
) -> None:
    kind, _, destination = TRANSITIONS[command]
    unchanged = [
        c
        for c in _cases_for(command)
        if c[1]["expected"]["status"] == 0
        and c[1]["expected"]["payload"]["changed"] is False
    ]

    assert unchanged, f"{command} has no already-in-destination case"
    for _, definition, before, after in unchanged:
        assert after == before
        assert f"already in {destination}" in definition["expected"]["message"]


@pytest.mark.parametrize("command", TRANSITIONS)
def test_every_lifecycle_command_has_a_not_found_case_on_an_empty_project(
    command: str,
) -> None:
    kind, _, _ = TRANSITIONS[command]
    missing = [
        c
        for c in _cases_for(command)
        if c[1]["expected"]["status"] == 1
        and not _artifact_folders(c[2], kind)
        and "not found" in c[1]["expected"]["message"]
    ]

    assert missing, f"{command} has no not-found case"


def test_task_block_with_a_reason_appends_a_work_log_entry_on_the_fixed_clock() -> None:
    appended = [
        c
        for c in _cases_for("task block")
        if c[1]["expected"]["status"] == 0 and c[3] != c[2]
    ]

    assert appended
    for _, definition, _, after in appended:
        text = "\n".join(e.get("text", "") for e in after)
        assert (
            f"— {definition['today']}\nBlocked: {definition['input']['reason']}" in text
        )


def test_task_block_numbers_the_entry_after_existing_sessions() -> None:
    texts = [
        e.get("text", "")
        for c in _cases_for("task block")
        for e in c[3]
        if e["type"] == "file"
    ]

    assert any("### Session 2 — " in text for text in texts)
