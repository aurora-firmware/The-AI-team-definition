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
