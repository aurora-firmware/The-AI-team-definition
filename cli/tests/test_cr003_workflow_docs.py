"""T-119: the workflow overview and component map describe design-review tasks."""

from __future__ import annotations

import re
from pathlib import Path

PROCESS_DIR = Path(__file__).resolve().parents[2] / "ai-process"
WORKFLOW_PATH = PROCESS_DIR / "processes" / "workflow-overview.md"
COMPONENT_MAP_PATH = PROCESS_DIR / "architecture" / "component-map.md"


def _section(text: str, heading: str) -> str:
    """Return the text under `heading` up to the next heading of equal or higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    start = text.index(heading) + len(heading)
    following = re.search(rf"^#{{1,{level}}} ", text[start:], flags=re.MULTILINE)
    end = start + following.start() if following else len(text)
    return text[start:end]


def _breakdown_section() -> str:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    return _section(text, "### 2. Task Breakdown + Gate 2")


def _developer_details() -> str:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    return _section(text, "#### Developer details")


def test_breakdown_states_planner_chooses_test_or_design_review_mode() -> None:
    section = _breakdown_section()
    assert "verification mode" in section
    assert "design review" in section


def test_breakdown_names_design_review_references() -> None:
    section = _breakdown_section()
    assert "source spec" in section
    assert "accepted ADRs" in section
    assert "S-000" in section


def test_breakdown_states_each_task_regenerates_its_own_generated_files() -> None:
    section = _breakdown_section()
    assert "regenerates the generated files its own change affects" in section
    assert "Files to Touch" in section


def test_breakdown_states_no_trailing_regenerate_everything_task() -> None:
    section = _breakdown_section()
    assert 'no trailing "regenerate everything" task' in section


def test_developer_details_name_recorded_design_review_as_output() -> None:
    details = _developer_details()
    assert details.count("design review") >= 2
    assert "Work Log" in details


def test_component_map_tdd_row_mentions_design_review_record() -> None:
    text = COMPONENT_MAP_PATH.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines() if line.startswith("| TDD |"))
    assert "design-review task" in row
    assert "listed references" in row
    assert "record the review" in row
