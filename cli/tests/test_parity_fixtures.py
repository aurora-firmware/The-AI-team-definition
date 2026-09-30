"""Parity fixture format and the Python fixture runner (S-005, ADR-004)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tests import parity_support as parity

FIXTURES = parity.FIXTURES_ROOT
CASES = parity.discover_cases(FIXTURES)


# --- tree manifests ---------------------------------------------------------


def test_tree_manifest_round_trips_empty_dirs_dotfiles_and_exact_bytes(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    (source / "empty").mkdir(parents=True)
    (source / "project").mkdir()
    (source / "project" / ".gitignore").write_bytes(b"a\r\nb\n")
    (source / "project" / ".ai-team.lock").write_bytes(b"")
    (source / "blob.bin").write_bytes(b"\xff\xfe\x00")

    manifest = parity.serialize_tree(source)
    target = tmp_path / "target"
    parity.materialize_tree(manifest, target)

    assert parity.serialize_tree(target) == manifest
    assert (target / "empty").is_dir()
    assert (target / "project" / ".gitignore").read_bytes() == b"a\r\nb\n"
    assert (target / "blob.bin").read_bytes() == b"\xff\xfe\x00"


def test_materialize_tree_rejects_paths_escaping_the_target(tmp_path: Path) -> None:
    manifest = [{"path": "../evil", "type": "file", "text": "x"}]

    with pytest.raises(ValueError, match="../evil"):
        parity.materialize_tree(manifest, tmp_path / "target")


# --- lock scoping -----------------------------------------------------------


def test_lock_scoping_file_lists_exactly_the_two_literal_paths() -> None:
    assert parity.load_lock_exclusions(FIXTURES) == [
        "<project_dir>/.ai-team.lock",
        "<project_dir>/.ai-team-ts.lock",
    ]


def test_exclusion_drops_both_lock_paths_and_a_ts_lock_subtree_only() -> None:
    tree = [
        {"path": "project", "type": "dir"},
        {"path": "project/.ai-team.lock", "type": "file", "text": ""},
        {"path": "project/.ai-team-ts.lock", "type": "dir"},
        {"path": "project/.ai-team-ts.lock/holder", "type": "file", "text": "1"},
        {"path": "project/.gitignore", "type": "file", "text": ".ai-team.lock\n"},
        {"path": "project/sub/.ai-team.lock", "type": "file", "text": ""},
    ]

    kept = parity.exclude_lock_paths(
        tree, "project", parity.load_lock_exclusions(FIXTURES)
    )

    assert [entry["path"] for entry in kept] == [
        "project",
        "project/.gitignore",
        "project/sub/.ai-team.lock",
    ]


# --- discovery --------------------------------------------------------------


def test_discover_cases_finds_a_new_case_directory_without_registration(
    tmp_path: Path,
) -> None:
    (tmp_path / "status--brand-new").mkdir()
    (tmp_path / "status--brand-new" / "case.json").write_text("{}")
    (tmp_path / "README.md").write_text("ignored")

    assert [case.name for case in parity.discover_cases(tmp_path)] == [
        "status--brand-new"
    ]


# --- running and comparing --------------------------------------------------


def _empty_project_tree(tmp_path: Path) -> Path:
    before = tmp_path / "before"
    for folder in (
        "specs",
        "tasks/pending",
        "tasks/in-progress",
        "tasks/completed",
        "tasks/blocked",
        "bugs/open",
        "bugs/in-progress",
        "bugs/resolved",
        "change-requests",
        "decisions",
        "docs",
    ):
        (before / "project" / folder).mkdir(parents=True, exist_ok=True)
    return before


def _record(fixtures: Path, tmp_path: Path, **overrides) -> Path:
    settings = {
        "command": "status",
        "case": "empty",
        "input": {},
        "before_dir": _empty_project_tree(tmp_path),
        "today": "2031-02-03",
        "version": "9.9.9",
    }
    settings.update(overrides)
    return parity.record_case(fixtures, **settings)


def test_recorded_case_passes_when_run_again(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    case = _record(fixtures, tmp_path)

    assert case.name == "status--empty"
    assert parity.compare_case(case) == []


def test_compare_fails_with_a_diff_naming_the_path_when_after_tree_differs(
    tmp_path: Path,
) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    case = _record(fixtures, tmp_path)
    after = json.loads((case / "after.json").read_text())
    after.append({"path": "project/stray.md", "type": "file", "text": "x"})
    (case / "after.json").write_text(json.dumps(after))

    diffs = parity.compare_case(case)

    assert any("project/stray.md" in diff for diff in diffs)


def test_compare_fails_with_a_diff_when_exit_status_differs(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    case = _record(fixtures, tmp_path)
    data = json.loads((case / "case.json").read_text())
    data["expected"]["status"] = 1
    (case / "case.json").write_text(json.dumps(data))

    diffs = parity.compare_case(case)

    assert any('"status"' in diff for diff in diffs)


def test_compare_fails_with_a_diff_when_error_message_differs(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    case = _record(fixtures, tmp_path, before_dir=None, case="no-project")
    data = json.loads((case / "case.json").read_text())
    assert data["expected"]["status"] == 1
    assert "<ROOT>" in data["expected"]["message"]
    data["expected"]["message"] = "something else"
    (case / "case.json").write_text(json.dumps(data))

    diffs = parity.compare_case(case)

    assert any("something else" in diff for diff in diffs)


def test_compare_ignores_the_remediation_hint_on_errors(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    case = _record(fixtures, tmp_path, before_dir=None, case="no-project")

    data = json.loads((case / "case.json").read_text())

    assert "hint" not in data["expected"]
    assert "ai-team init" not in data["expected"]["message"]


def test_record_refuses_to_overwrite_an_existing_case(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    case = _record(fixtures, tmp_path)
    original = (case / "case.json").read_text()

    with pytest.raises(FileExistsError, match="status--empty"):
        _record(fixtures, tmp_path, today="2040-01-01")

    assert (case / "case.json").read_text() == original


def test_record_rejects_case_names_that_are_not_slug_dash_dash_case(
    tmp_path: Path,
) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()

    with pytest.raises(ValueError, match="case"):
        _record(fixtures, tmp_path, case="Not A Slug")


def test_lock_sentinels_in_the_after_tree_are_ignored(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    before = _empty_project_tree(tmp_path)
    (before / "project" / ".ai-team.lock").write_bytes(b"")
    case = _record(
        fixtures,
        tmp_path,
        command="task new",
        input={"title": "Locked"},
        before_dir=before,
    )

    after_paths = [e["path"] for e in json.loads((case / "after.json").read_text())]
    before_paths = [e["path"] for e in json.loads((case / "before.json").read_text())]

    assert "project/.ai-team.lock" in before_paths
    assert "project/.ai-team.lock" not in after_paths
    assert parity.compare_case(case) == []


def test_clock_and_version_come_only_from_the_case_overrides(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("AI_TEAM_TODAY", "1999-09-09")
    monkeypatch.setenv("AI_TEAM_FRAMEWORK_VERSION", "0.0.1")
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    task_case = _record(
        fixtures,
        tmp_path,
        command="task new",
        input={"title": "Dated"},
        case="dated",
    )
    init_case = _record(
        fixtures,
        tmp_path,
        command="init",
        input={},
        before_dir=None,
        case="versioned",
    )

    task_after = json.loads((task_case / "after.json").read_text())
    task_file = next(e for e in task_after if e["path"].endswith("-dated.md"))
    init_after = json.loads((init_case / "after.json").read_text())
    marker = next(e for e in init_after if e["path"] == ".ai-team.toml")

    assert "created: '2031-02-03'" in task_file["text"]
    assert 'framework_version = "9.9.9"' in marker["text"]
    assert os.environ["AI_TEAM_TODAY"] == "1999-09-09"


def test_case_without_clock_or_version_is_rejected(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    case = _record(fixtures, tmp_path)
    data = json.loads((case / "case.json").read_text())
    del data["today"]
    (case / "case.json").write_text(json.dumps(data))

    with pytest.raises(ValueError, match="today"):
        parity.compare_case(case)


def test_results_carry_the_root_as_a_placeholder(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    case = _record(
        fixtures, tmp_path, command="task new", input={"title": "Path check"}
    )

    expected = json.loads((case / "case.json").read_text())["expected"]

    assert expected["payload"]["path"] == (
        "<ROOT>/project/tasks/pending/T-001-path-check.md"
    )


# --- isolation --------------------------------------------------------------


def test_run_unsets_ai_team_root_unless_the_case_sets_it(
    tmp_path: Path, monkeypatch
) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    case = _record(fixtures, tmp_path)
    monkeypatch.setenv("AI_TEAM_ROOT", str(tmp_path / "elsewhere"))

    assert parity.compare_case(case) == []
    assert os.environ["AI_TEAM_ROOT"] == str(tmp_path / "elsewhere")


def test_case_can_resolve_its_root_through_ai_team_root(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    case = _record(
        fixtures,
        tmp_path,
        before_dir=None,
        case="env-root-missing",
        env={"AI_TEAM_ROOT": "<ROOT>"},
    )

    expected = json.loads((case / "case.json").read_text())["expected"]

    assert (
        expected["message"] == "No 'project/' folder found under AI_TEAM_ROOT=<ROOT>."
    )
    assert parity.compare_case(case) == []


def test_isolated_environment_sets_git_ceiling_and_clears_ai_team_root(
    tmp_path: Path, monkeypatch
) -> None:
    import subprocess

    monkeypatch.setenv("AI_TEAM_ROOT", "/nope")
    case = {"today": "2031-02-03", "version": "1.0.0", "env": {}}
    with parity.materialized_root() as root:
        with parity.isolated_environment(root, case):
            assert "AI_TEAM_ROOT" not in os.environ
            assert os.environ["GIT_CEILING_DIRECTORIES"] == str(root.parent)
            inside = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
            )
            assert inside.returncode != 0


# --- the committed fixtures -------------------------------------------------


def test_fixture_suite_has_the_status_smoke_case() -> None:
    assert "status--empty" in [case.name for case in CASES]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_parity_case_matches_python_implementation(case: Path) -> None:
    diffs = parity.compare_case(case)

    assert diffs == [], "\n".join(diffs)


# --- seed helper script -----------------------------------------------------

SEED_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "seed_parity_fixture.py"


def _run_seed(fixtures: Path, before: Path, *extra: str):
    import subprocess
    import sys

    return subprocess.run(
        [
            sys.executable,
            str(SEED_SCRIPT),
            "--fixtures-root",
            str(fixtures),
            "--command",
            "status",
            "--case",
            "seeded",
            "--before-tree",
            str(before),
            "--today",
            "2031-02-03",
            "--version",
            "9.9.9",
            *extra,
        ],
        capture_output=True,
        text=True,
    )


def test_seed_script_records_a_case_then_refuses_to_overwrite_it(
    tmp_path: Path,
) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    before = _empty_project_tree(tmp_path)

    first = _run_seed(fixtures, before)
    second = _run_seed(fixtures, before)

    assert first.returncode == 0, first.stderr
    assert parity.compare_case(fixtures / "status--seeded") == []
    assert second.returncode != 0
    assert "status--seeded" in second.stderr
