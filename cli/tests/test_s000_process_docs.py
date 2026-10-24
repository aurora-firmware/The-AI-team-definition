"""T-092: the workflow overview and component map describe S-000."""

from __future__ import annotations

import re
from pathlib import Path

PROCESS_DIR = Path(__file__).resolve().parents[2] / "ai-process"
WORKFLOW_PATH = PROCESS_DIR / "processes" / "workflow-overview.md"
COMPONENT_MAP_PATH = PROCESS_DIR / "architecture" / "component-map.md"
QUALITY_GATES_PATH = PROCESS_DIR / "processes" / "quality-gates.md"

SKILL_PATH = "`.claude/skills/new-system-overview/SKILL.md`"


def _section(text: str, heading: str) -> str:
    """Return the text under `heading` up to the next heading of equal or higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    start = text.index(heading) + len(heading)
    following = re.search(rf"^#{{1,{level}}} ", text[start:], flags=re.MULTILINE)
    end = start + following.start() if following else len(text)
    return text[start:end]


def _workflow() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def _component_map() -> str:
    return COMPONENT_MAP_PATH.read_text(encoding="utf-8")


def _row(text: str, heading: str, first_cell: str) -> str:
    for line in _section(text, heading).splitlines():
        if line.startswith(f"| {first_cell} |"):
            return line
    raise AssertionError(f"no row starting with {first_cell!r} under {heading!r}")


def _s000_phase() -> str:
    return _section(_workflow(), "### 0. System Overview (S-000)")


def test_workflow_overview_has_an_s000_phase_before_brainstorm():
    text = _workflow()

    assert text.index("### 0. System Overview (S-000)") < text.index(
        "### 1. Brainstorm"
    )


def test_workflow_overview_proposes_new_system_overview_for_new_projects():
    phase = _s000_phase()

    assert "`new-system-overview`" in phase
    assert "new project" in phase


def test_workflow_overview_marks_s000_optional_for_projects_with_specs():
    phase = _s000_phase()

    assert "optional" in phase
    assert "already have specs" in phase


def test_workflow_overview_describes_brownfield_adoption():
    assert "brownfield" in _s000_phase()


def test_workflow_overview_states_s000_produces_only_bootstrap_tasks():
    phase = _s000_phase()

    assert "only the project bootstrap tasks" in phase
    assert "never broken down into tasks" not in phase


def test_workflow_overview_describes_completing_s000_after_gate_1():
    phase = _s000_phase()

    assert "After Gate 1" in phase
    assert "`approved`" in phase
    assert "`--no-ff`" in phase


def test_workflow_overview_describes_the_brownfield_change_request():
    phase = _s000_phase()

    assert "change request" in phase
    assert "overlaps, gaps" in phase


def test_workflow_overview_describes_the_project_bootstrap_phase():
    text = _workflow()
    phase = _section(text, "### Project bootstrap")

    assert text.index("### 0. System Overview (S-000)") < text.index(
        "### Project bootstrap"
    )
    assert text.index("### Project bootstrap") < text.index("### 1. Brainstorm")
    assert "**Role:** Planner" in phase
    assert "`spec-breakdown`" in phase
    assert "**Input:**" in phase
    assert "approved S-000" in phase
    assert "**Output:**" in phase
    assert "Gate 2" in phase
    assert "development loop" in phase


def test_workflow_overview_requires_no_baseline_confirmation_for_bootstrap():
    phase = _section(_workflow(), "### Project bootstrap")

    assert "no baseline test command" in phase
    assert "human confirms that no automated baseline is available" in phase


def _s000_gate_1_criteria() -> str:
    text = QUALITY_GATES_PATH.read_text(encoding="utf-8")
    start = text.index("**S-000 pass criteria:**")
    return text[start : text.index("**On failure:**", start)]


def test_quality_gates_s000_criteria_require_solution_and_infrastructure_groups():
    criteria = _s000_gate_1_criteria()

    assert "solution" in criteria
    assert "development-infrastructure" in criteria


def test_quality_gates_s000_criteria_require_decisions_needed_on_infrastructure():
    criteria = _s000_gate_1_criteria()

    assert "Decisions needed" in criteria
    assert "infrastructure component" in criteria


def test_quality_gates_keep_s000_out_of_the_completion_review_with_reason():
    text = QUALITY_GATES_PATH.read_text(encoding="utf-8")
    sentence = next(
        line for line in text.splitlines() if "does not include S-000" in line
    )

    assert "bootstrap tasks answer questions S-000 only asks" in sentence
    assert "makes no assertion" in sentence


def test_workflow_overview_names_s000_merge_as_landing_exception():
    text = _section(_workflow(), "## Git Branching Strategy")
    rule = next(
        line
        for line in text.splitlines()
        if line.startswith("- Spec and change-request work never lands")
    )

    assert "follow-up task" in rule
    assert "S-000" in rule
    assert "after Gate 1" in rule


def test_component_map_procedures_has_new_system_overview_row():
    row = _row(_component_map(), "## Procedures", "New System Overview")
    cells = [cell.strip() for cell in row.strip("|").split("|")]

    assert len(cells) == 4
    assert "Planner" in cells[2]
    assert cells[3] == SKILL_PATH


def test_component_map_planner_row_mentions_reading_s000_at_session_start():
    row = _row(_component_map(), "## Roles", "Planner")

    assert "S-000" in row
    assert "session start" in row


def test_component_map_architect_row_mentions_reading_s000_and_checking_specs():
    row = _row(_component_map(), "## Roles", "Architect")

    assert "S-000" in row
    assert "session start" in row
    assert "checking specs against" in row


def test_component_map_cli_mapping_maps_new_system_overview_to_spec_new_overview():
    row = _row(_component_map(), "## CLI Command Mapping", "`new-system-overview`")

    assert "`ai-team spec new --overview`" in row


def test_component_map_keeps_existing_rows_and_table_widths():
    text = _component_map()
    expected_columns = {
        "## Roles": 6,
        "## Procedures": 4,
        "## CLI Command Mapping": 3,
    }

    for heading, columns in expected_columns.items():
        rows = [
            line
            for line in _section(text, heading).splitlines()
            if line.startswith("|")
        ]
        assert all(line.strip("|").count("|") == columns - 1 for line in rows)

    for first_cell in ("Brainstorm", "Spec Breakdown", "Status Report", "New ADR"):
        _row(text, "## Procedures", first_cell)
    for first_cell in ("`new-spec`", "`status-report`", "*(change-request intake)*"):
        _row(text, "## CLI Command Mapping", first_cell)
