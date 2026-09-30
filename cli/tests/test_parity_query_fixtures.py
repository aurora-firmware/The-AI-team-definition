"""Coverage contract for the read-only query parity cases (S-005 SC-3, SC-5).

The fixtures are the contract; these tests only guard that the seeded set keeps
covering every list, show, status and report leaf command, and every list state
value. Running the cases against the Python implementation is done by
``test_parity_fixtures.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests import parity_support as parity

QUERY_COMMANDS = (
    "list tasks",
    "list bugs",
    "list specs",
    "list adrs",
    "list change-requests",
    "show",
    "status",
    "report",
)

# command -> (payload field holding the state, every value the listing can show)
LIST_STATES: dict[str, tuple[str, set[str]]] = {
    "list tasks": ("state", {"pending", "in-progress", "completed", "blocked"}),
    "list bugs": ("state", {"open", "in-progress", "resolved"}),
    "list specs": ("status", {"draft", "review", "approved", "superseded"}),
    "list adrs": ("status", {"proposed", "accepted", "superseded"}),
    "list change-requests": ("state", {"pending"}),
}

SHOWN_KINDS = {"task": "tasks", "bug": "bugs", "spec": "specs", "adr": "decisions"}


def _for_command(command: str) -> list[tuple[Path, dict]]:
    loaded = []
    for case_dir in parity.discover_cases(parity.FIXTURES_ROOT):
        definition = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
        if definition["command"] == command:
            loaded.append((case_dir, definition))
    return loaded


@pytest.mark.parametrize("command", QUERY_COMMANDS)
def test_every_query_command_has_a_success_case_named_for_it(command: str) -> None:
    cases = _for_command(command)
    slug = command.replace(" ", "-")

    assert any(d["expected"]["status"] == 0 for _, d in cases)
    assert all(path.name.startswith(f"{slug}--") for path, _ in cases)


@pytest.mark.parametrize("command", LIST_STATES)
def test_every_list_state_value_appears_in_an_unfiltered_listing(
    command: str,
) -> None:
    field, states = LIST_STATES[command]
    seen = {
        row[field]
        for _, d in _for_command(command)
        if "state" not in d["input"] and d["expected"]["status"] == 0
        for row in d["expected"]["payload"]
    }

    assert states <= seen


@pytest.mark.parametrize("command", ["list tasks", "list bugs"])
def test_every_state_filter_value_has_a_case_returning_only_that_state(
    command: str,
) -> None:
    _, states = LIST_STATES[command]
    filtered = {
        d["input"]["state"]: d["expected"]["payload"]
        for _, d in _for_command(command)
        if "state" in d["input"]
    }

    for state in states:
        assert filtered.get(state), f"{command} has no non-empty --state {state} case"
        assert {row["state"] for row in filtered[state]} == {state}


@pytest.mark.parametrize("command", ["list tasks", "list bugs"])
def test_an_unknown_state_filter_lists_nothing(command: str) -> None:
    unknown = [
        d
        for _, d in _for_command(command)
        if d["input"].get("state") not in (None, *LIST_STATES[command][1])
    ]

    assert unknown
    assert all(d["expected"] == {"status": 0, "payload": []} for d in unknown)


def test_show_has_a_case_for_each_artifact_kind() -> None:
    shown = set()
    for path, definition in _for_command("show"):
        if definition["expected"]["status"] != 0:
            continue
        shown_path = definition["expected"]["payload"]["path"]
        shown.update(
            kind for kind, folder in SHOWN_KINDS.items() if f"/{folder}/" in shown_path
        )

    assert shown == set(SHOWN_KINDS)


def test_show_reports_an_unknown_identifier_as_not_found() -> None:
    missing = [
        d
        for _, d in _for_command("show")
        if d["expected"]["status"] == 1 and "not found" in d["expected"]["message"]
    ]

    assert missing


def test_status_has_a_populated_case_with_blocked_and_high_severity_entries() -> None:
    populated = [
        d["expected"]["payload"]
        for _, d in _for_command("status")
        if d["expected"]["payload"]["blocked_tasks"]
        and d["expected"]["payload"]["critical_high_open_bugs"]
        and d["expected"]["payload"]["in_progress_tasks"]
    ]

    assert populated


def test_report_has_default_and_explicit_out_cases_that_write_the_report() -> None:
    cases = _for_command("report")
    defaults = [(p, d) for p, d in cases if "out" not in d["input"]]
    explicit = [(p, d) for p, d in cases if "out" in d["input"]]

    assert defaults
    assert explicit
    for path, definition in defaults + explicit:
        after = json.loads((path / "after.json").read_text(encoding="utf-8"))
        written = {e["path"] for e in after if e["type"] == "file"}
        reported = definition["expected"]["payload"]["path"]
        assert reported.removeprefix("<ROOT>/") in written
