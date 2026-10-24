"""Regression tests for CR-004: the project bootstrap in the user-facing docs."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SETUP_GUIDE = (REPO_ROOT / "guides" / "setup-guide.md").read_text(encoding="utf-8")
CUSTOMIZATION_GUIDE = (REPO_ROOT / "guides" / "customization-guide.md").read_text(
    encoding="utf-8"
)
COMPONENT_MAP = (
    REPO_ROOT / "ai-process" / "architecture" / "component-map.md"
).read_text(encoding="utf-8")


def _line_containing(text: str, marker: str) -> str:
    for line in text.splitlines():
        if marker in line:
            return line
    raise AssertionError(f"no line contains {marker!r}")


def test_setup_guide_runs_project_bootstrap_after_s000_approval() -> None:
    assert "project bootstrap" in SETUP_GUIDE
    assert "After S-000 is approved, run the project bootstrap" in SETUP_GUIDE


def test_setup_guide_does_not_tell_reader_to_create_coding_guidelines_by_hand() -> None:
    assert "Create this file and add project-specific rules" not in SETUP_GUIDE
    assert "filled in by the project bootstrap" in SETUP_GUIDE


def test_customization_guide_writes_s000_before_the_bootstrap_fills_guidance() -> None:
    adoption = CUSTOMIZATION_GUIDE.split("## Retrofitting Into an Existing Project")[1]
    s000_at = adoption.index("S-000")
    bootstrap_at = adoption.index("project bootstrap")
    assert s000_at < bootstrap_at
    assert "coding guidelines" in adoption[bootstrap_at:]
    assert "Create `ai-team/docs/coding_guidelines.md`" not in adoption


def test_component_map_limits_new_system_overview_to_bootstrap_tasks() -> None:
    row = _line_containing(COMPONENT_MAP, "| New System Overview |")
    assert "never broken down into tasks" not in row
    assert "only the project bootstrap tasks" in row


def test_component_map_lists_project_bootstrap_procedure_for_planner() -> None:
    row = _line_containing(COMPONENT_MAP, "| Project Bootstrap |")
    assert "Planner" in row
    assert "spec-breakdown" in row
    assert "S-000" in row


def test_setup_guide_force_note_says_coding_guidelines_never_overwritten() -> None:
    note = _line_containing(SETUP_GUIDE, "`ai-team init --force` overwrites")
    assert "docs/coding_guidelines.md" in note
    assert "never overwritten, even with `--force`" in note
