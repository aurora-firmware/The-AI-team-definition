"""Tests for T-078: S-000 content contract in the spec authoring guide."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUIDE_PATH = REPO_ROOT / "guides" / "spec-authoring-guide.md"
HEADING = "## The system overview spec (S-000)"
NEXT_HEADING = "## How to write measurable success criteria"
S000_SECTIONS = [
    "Purpose",
    "Users",
    "Pain points",
    "Use cases",
    "Solution overview",
    "Components",
    "Project exclusions",
]


def _s000_section() -> str:
    text = GUIDE_PATH.read_text(encoding="utf-8")
    assert HEADING in text, f"missing heading {HEADING!r}"
    start = text.index(HEADING)
    end = text.index(NEXT_HEADING)
    assert start < end, "S-000 section must precede the success-criteria section"
    return text[start:end]


def test_s000_section_lists_seven_sections_in_order() -> None:
    section = _s000_section()
    positions = []
    for name in S000_SECTIONS:
        match = re.search(rf"^\d+\.\s+\*\*{re.escape(name)}\*\*", section, re.M)
        assert match, f"missing S-000 section entry {name}"
        positions.append(match.start())
    assert positions == sorted(positions)


def test_s000_section_states_component_entry_fields() -> None:
    section = _s000_section().lower()
    for field in ("name", "owned responsibility", "boundary", "works with"):
        assert field in section, f"missing component field {field}"


def test_s000_section_states_exclusions_of_content() -> None:
    section = _s000_section().lower()
    for item in (
        "technology choices",
        "interface definitions",
        "configuration",
        "implementation order",
        "per-component status",
        "plain language",
    ):
        assert item in section, f"missing {item}"


def test_s000_section_states_boundary_rule() -> None:
    section = _s000_section().lower()
    assert "owns the decomposition" in section
    assert "contract of one component or feature" in section
    assert "purpose names the s-000 component" in section


def test_feature_spec_recipes_are_unchanged() -> None:
    base = "22164b36e831dacba12329a5e287b1efd175a856"
    original = subprocess.run(
        ["git", "show", f"{base}:guides/spec-authoring-guide.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    current = GUIDE_PATH.read_text(encoding="utf-8")
    start = original.index("## How to write each section")
    end = original.index(NEXT_HEADING)
    assert original[start:end] in current
