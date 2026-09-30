"""Coverage contract for the check-layout and init parity cases (S-005 SC-3 to SC-8).

The fixtures are the contract; these tests only guard that the seeded set keeps
covering every init field, the broken-tree findings for each layout level, the
root-not-found and tool-scaffold cases, the T-087 ``.gitignore`` entry, and the
init to check-layout chain. Running the cases against the Python implementation
is done by ``test_parity_fixtures.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests import parity_support as parity

TS_LOCK_ENTRY = ".ai-team-ts.lock"
INIT_FIELDS = ("path", "force", "dryRun", "createRootGuidance")
ROOT_GUIDANCE_FILES = ("CLAUDE.md", "AGENTS.md")
CHAIN_PREFIX = "check-layout--after-init-"


def _for_command(command: str) -> list[tuple[Path, dict]]:
    loaded = []
    for case_dir in parity.discover_cases(parity.FIXTURES_ROOT):
        definition = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
        if definition["command"] == command:
            loaded.append((case_dir, definition))
    return loaded


def _tree(case_dir: Path, name: str) -> list[dict]:
    return json.loads((case_dir / name).read_text(encoding="utf-8"))


def _files(tree: list[dict]) -> dict[str, str]:
    return {e["path"]: e["text"] for e in tree if e["type"] == "file"}


def _levels(definition: dict) -> set[int]:
    return {f["level"] for f in definition["expected"]["payload"]["findings"]}


def _findings_text(definition: dict) -> str:
    return "\n".join(
        f["message"] for f in definition["expected"]["payload"]["findings"]
    )


def _successful_inits() -> list[tuple[Path, dict]]:
    return [
        (p, d)
        for p, d in _for_command("init")
        if d["expected"]["status"] == 0 and not d["input"].get("dryRun")
    ]


def test_layout_and_init_cases_are_named_for_their_command() -> None:
    for command in ("check-layout", "init"):
        cases = _for_command(command)
        assert cases
        assert all(path.name.startswith(f"{command}--") for path, _ in cases)


def test_init_cases_cover_every_tool_contract_field_both_ways() -> None:
    inputs = [d["input"] for _, d in _for_command("init")]

    assert {} in inputs
    for field in INIT_FIELDS:
        assert any(field in i for i in inputs), field
    for flag in ("force", "dryRun", "createRootGuidance"):
        assert any(i.get(flag) is True for i in inputs), flag
        assert any(i.get(flag) is False for i in inputs), flag
    assert any(i.get("path", ".") != "." for i in inputs)


def test_init_covers_a_refused_overwrite_and_a_forced_overwrite() -> None:
    cases = [d for _, d in _for_command("init")]

    assert any(
        d["expected"]["status"] == 1
        and "Refusing to overwrite" in d["expected"]["message"]
        for d in cases
    )
    assert any(
        d["input"].get("force") is True and d["expected"]["status"] == 0 for d in cases
    )


def test_init_with_and_without_root_guidance_differ_in_the_after_tree() -> None:
    with_guidance = [
        p
        for p, d in _successful_inits()
        if d["input"].get("createRootGuidance") is True
        and d["input"].get("path", ".") == "."
        and not _files(_tree(p, "before.json"))
    ]
    without_guidance = [
        p
        for p, d in _successful_inits()
        if not d["input"].get("createRootGuidance")
        and not _files(_tree(p, "before.json"))
    ]

    assert with_guidance
    assert without_guidance
    for path in with_guidance:
        assert set(ROOT_GUIDANCE_FILES) <= set(_files(_tree(path, "after.json")))
    for path in without_guidance:
        assert not set(ROOT_GUIDANCE_FILES) & set(_files(_tree(path, "after.json")))


def test_init_fixtures_never_include_tool_directories() -> None:
    for path, _ in _for_command("init"):
        for name in ("before.json", "after.json"):
            for entry in _tree(path, name):
                assert not entry["path"].split("/")[0].startswith(".claude")
                assert not entry["path"].split("/")[0].startswith(".codex")
                assert "/.claude" not in entry["path"]
                assert "/.codex" not in entry["path"]


def test_init_uses_the_empty_tool_list_in_the_marker() -> None:
    for path, _ in _successful_inits():
        markers = [
            text
            for file_path, text in _files(_tree(path, "after.json")).items()
            if file_path.endswith(".ai-team.toml")
        ]
        assert markers
        assert all("tools = []" in text for text in markers)


def test_init_after_trees_contain_the_ts_lock_gitignore_entry() -> None:
    for path, _ in _successful_inits():
        gitignores = [
            text
            for file_path, text in _files(_tree(path, "after.json")).items()
            if file_path.endswith("project/.gitignore")
        ]
        assert gitignores, path.name
        assert all(TS_LOCK_ENTRY in text for text in gitignores), path.name


def test_init_dry_run_leaves_the_tree_untouched_and_lists_planned_files() -> None:
    dry_runs = [
        (p, d)
        for p, d in _for_command("init")
        if d["input"].get("dryRun") is True and d["expected"]["status"] == 0
    ]

    assert dry_runs
    for path, definition in dry_runs:
        assert definition["expected"]["payload"]["dry_run"] is True
        assert definition["expected"]["payload"]["files"]
        assert (path / "before.json").read_bytes() == (path / "after.json").read_bytes()


def test_every_successful_init_has_a_chained_check_layout_with_zero_findings() -> None:
    chained = {p.name: (p, d) for p, d in _for_command("check-layout")}
    for init_path, init_definition in _successful_inits():
        name = CHAIN_PREFIX + init_path.name.removeprefix("init--")
        assert name in chained, f"missing chained check-layout case {name}"
        chain_path, chain_definition = chained[name]
        assert chain_definition["expected"] == {
            "status": 0,
            "payload": {"findings": []},
        }
        after = _tree(init_path, "after.json")
        prefix = init_definition["input"].get("path", ".").removeprefix("./")
        prefix = "" if prefix == "." else prefix
        assert _rebased(after, prefix) == _tree(chain_path, "before.json")


def _rebased(tree: list[dict], prefix: str) -> list[dict]:
    if not prefix:
        return tree
    return [
        {**entry, "path": entry["path"].removeprefix(prefix + "/")}
        for entry in tree
        if entry["path"].startswith(prefix + "/")
    ]


def test_check_layout_has_a_clean_case_and_broken_cases_for_every_level() -> None:
    cases = [d for _, d in _for_command("check-layout")]

    assert any(d["expected"]["payload"]["findings"] == [] for d in cases)
    levels: set[int] = set()
    for definition in cases:
        assert definition["input"] == {}
        levels |= _levels(definition)
    assert levels == {1, 2, 3, 4}


@pytest.mark.parametrize(
    ("fragment", "expected_text"),
    [
        ("missing-dirs", "Required scaffold directory"),
        ("invalid-marker", "is invalid"),
        ("placeholder-root-guidance", "placeholder content"),
        ("version-mismatch", "does not exactly match"),
    ],
)
def test_each_broken_tree_kind_has_a_failing_case(
    fragment: str, expected_text: str
) -> None:
    matching = [
        d
        for p, d in _for_command("check-layout")
        if p.name == f"check-layout--{fragment}"
    ]

    assert len(matching) == 1
    assert matching[0]["expected"]["status"] == 1
    assert expected_text in _findings_text(matching[0])


def test_root_not_found_case_sets_ai_team_root_and_reports_missing_marker() -> None:
    matching = [
        d
        for p, d in _for_command("check-layout")
        if p.name == "check-layout--root-not-found"
    ]

    assert len(matching) == 1
    assert matching[0]["env"] == {"AI_TEAM_ROOT": "<ROOT>"}
    assert matching[0]["expected"]["status"] == 1
    assert "Repository marker .ai-team.toml is missing" in _findings_text(matching[0])


def test_check_layout_covers_claude_and_codex_with_only_their_scaffold_dirs() -> None:
    for tools in (["claude"], ["codex"], ["claude", "codex"]):
        marker_text = "tools = [" + ", ".join(f'"{t}"' for t in tools) + "]"
        found = False
        for path, definition in _for_command("check-layout"):
            files = _files(_tree(path, "before.json"))
            if marker_text not in files.get(".ai-team.toml", ""):
                continue
            tool_paths = {
                e["path"].split("/")[0] for e in _tree(path, "before.json")
            } & {".claude", ".codex"}
            if tool_paths == {f".{t}" for t in tools}:
                assert not any(p.startswith((".claude/", ".codex/")) for p in files), (
                    "tool scaffolds are directories only"
                )
                found = True
        assert found, tools
