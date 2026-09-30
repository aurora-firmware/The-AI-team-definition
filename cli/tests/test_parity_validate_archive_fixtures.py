"""Coverage contract for the validate and archive parity cases (S-005 SC-3, SC-4, SC-5).

The fixtures are the contract; these tests only guard that the seeded set keeps
covering every validate flag, the malformed-frontmatter findings, the archive
duration and dry-run inputs, and both sides of the archive age cut-off. Running
the cases against the Python implementation is done by ``test_parity_fixtures.py``.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from tests import parity_support as parity

VALIDATE_FLAGS = {
    "tasks": "project/tasks/",
    "bugs": "project/bugs/",
    "specs": "project/specs/",
    "adrs": "project/decisions/",
    "changeRequests": "project/change-requests/",
}
DURATION_DAYS = {"d": 1, "w": 7, "m": 30, "y": 365}


def _for_command(command: str) -> list[tuple[Path, dict]]:
    loaded = []
    for case_dir in parity.discover_cases(parity.FIXTURES_ROOT):
        definition = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
        if definition["command"] == command:
            loaded.append((case_dir, definition))
    return loaded


def _finding_codes(definition: dict) -> set[str]:
    return {finding["code"] for finding in definition["expected"]["payload"]}


def _moved_names(definition: dict) -> set[str]:
    return {
        Path(move["source"]).name for move in definition["expected"]["payload"]["moves"]
    }


def _before_files(case_dir: Path) -> dict[str, str]:
    before = json.loads((case_dir / "before.json").read_text(encoding="utf-8"))
    return {e["path"]: e["text"] for e in before if e["type"] == "file"}


def test_validate_and_archive_cases_are_named_for_their_command() -> None:
    for command in ("validate", "archive"):
        cases = _for_command(command)
        assert cases
        assert all(path.name.startswith(f"{command}--") for path, _ in cases)


@pytest.mark.parametrize("flag", VALIDATE_FLAGS)
def test_each_validate_flag_alone_reports_only_its_own_scope(flag: str) -> None:
    alone = [
        d
        for _, d in _for_command("validate")
        if d["input"] == {flag: True} and d["expected"]["payload"]
    ]

    assert alone, f"no validate case with only {flag} and findings"
    for definition in alone:
        assert all(
            f["path"].startswith(VALIDATE_FLAGS[flag])
            for f in definition["expected"]["payload"]
        )


def test_validate_covers_combined_all_and_no_flag_runs() -> None:
    inputs = [d["input"] for _, d in _for_command("validate")]

    assert any(
        len([v for v in i.values() if v]) >= 2 and "all" not in i for i in inputs
    )
    assert {"all": True} in inputs
    assert {} in inputs


def test_validate_all_and_no_flags_report_every_scope() -> None:
    for wanted in ({"all": True}, {}):
        broken = [
            d
            for _, d in _for_command("validate")
            if d["input"] == wanted and d["expected"]["payload"]
        ]
        assert broken
        for definition in broken:
            paths = [f["path"] for f in definition["expected"]["payload"]]
            for prefix in VALIDATE_FLAGS.values():
                assert any(p.startswith(prefix) for p in paths)


def test_validate_has_a_clean_case_that_exits_zero() -> None:
    clean = [
        d
        for _, d in _for_command("validate")
        if d["expected"] == {"status": 0, "payload": []}
    ]

    assert clean


def test_validate_reports_malformed_frontmatter_and_invalid_ids() -> None:
    codes: set[str] = set()
    for _, definition in _for_command("validate"):
        codes |= _finding_codes(definition)

    assert {"frontmatter-invalid", "id-pattern"} <= codes


@pytest.mark.parametrize(
    "fragment",
    ["missing-fence", "missing-required-key", "invalid-id-pattern"],
)
def test_each_malformed_frontmatter_kind_has_a_failing_case(fragment: str) -> None:
    matching = [
        d for p, d in _for_command("validate") if p.name == f"validate--{fragment}"
    ]

    assert len(matching) == 1
    assert matching[0]["expected"]["status"] == 1
    assert matching[0]["expected"]["payload"]


def test_archive_covers_each_duration_unit_and_dry_run() -> None:
    cases = [d for _, d in _for_command("archive")]
    units = {
        d["input"]["olderThan"][-1]
        for d in cases
        if "olderThan" in d["input"] and d["expected"]["status"] == 0
    }

    assert units == set(DURATION_DAYS)
    assert any("olderThan" not in d["input"] for d in cases)
    assert any(d["input"].get("dryRun") is True for d in cases)
    assert any(d["input"].get("dryRun") is not True for d in cases)


def test_archive_rejects_an_invalid_older_than_value() -> None:
    invalid = [
        d
        for _, d in _for_command("archive")
        if d["expected"]["status"] == 1
        and "Invalid --older-than" in d["expected"]["message"]
    ]

    assert invalid


def test_archive_age_boundary_moves_before_cutoff_and_keeps_on_and_after() -> None:
    boundary = [
        (p, d) for p, d in _for_command("archive") if p.name == "archive--age-boundary"
    ]
    assert len(boundary) == 1
    path, definition = boundary[0]
    amount = definition["input"]["olderThan"]
    cutoff = date.fromisoformat(definition["today"]) - timedelta(
        days=int(amount[:-1]) * DURATION_DAYS[amount[-1]]
    )
    moved = _moved_names(definition)

    created_by_name = {}
    for file_path, text in _before_files(path).items():
        if "/completed/" in file_path or "/resolved/" in file_path:
            created = next(
                line.split(": ", 1)[1].strip("'")
                for line in text.splitlines()
                if line.startswith("created:")
            )
            created_by_name[Path(file_path).name] = date.fromisoformat(created)

    offsets = {(created - cutoff).days for created in created_by_name.values()}
    assert {-1, 0, 1} <= offsets
    for name, created in created_by_name.items():
        assert (name in moved) == (created < cutoff)


def test_archive_dry_run_leaves_the_tree_untouched() -> None:
    dry_runs = [
        (p, d)
        for p, d in _for_command("archive")
        if d["input"].get("dryRun") is True and d["expected"]["status"] == 0
    ]

    assert dry_runs
    for path, definition in dry_runs:
        assert definition["expected"]["payload"]["moves"]
        assert (path / "before.json").read_bytes() == (path / "after.json").read_bytes()
