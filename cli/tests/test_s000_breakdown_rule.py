"""T-087: spec-breakdown refuses to break down S-000."""

from __future__ import annotations

import re
from pathlib import Path

BODY_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "ai_team"
    / "init"
    / "sources"
    / "skills"
    / "spec-breakdown"
    / "body.md"
)

EXPECTED_HEADINGS = [
    "# Write Plan",
    "## Input Requirements",
    "## Procedure",
    "### Step 0: Check Out the Planning Branch",
    "### Step 1: Identify Components",
    "### Step 2: Define Dependencies",
    "### Step 3: Write Task Files",
    "### Step 4: Validate the Plan",
    "### Step 5: Place Tasks",
    "### Step 6: Architect Preflight",
    "### Step 7: Merge the Planning Branch and Activate the Tasks",
    "## Output Format",
    "## Quality Criteria",
    "## Common Pitfalls",
]


def _body() -> str:
    return BODY_PATH.read_text(encoding="utf-8")


def _section(heading: str) -> str:
    """Return the text under `heading` up to the next heading of any level."""
    body = _body()
    start = body.index(heading) + len(heading)
    following = re.search(r"^#{1,3} ", body[start:], flags=re.MULTILINE)
    end = start + following.start() if following else len(body)
    return body[start:end]


def test_input_requirements_state_that_s000_stops_the_skill():
    section = _section("## Input Requirements")

    assert "S-000" in section
    assert "project overview" in section
    assert "stops" in section


def test_step_zero_opens_with_the_s000_refusal_before_any_checkout():
    section = _section("### Step 0: Check Out the Planning Branch")
    first_paragraph = section.strip().split("\n", 1)[0]

    assert "S-000" in first_paragraph
    assert "stop" in first_paragraph
    assert section.index("S-000") < section.index("check it out")


def test_refusal_names_feature_specs_as_input_and_creates_no_task():
    section = _section("### Step 0: Check Out the Planning Branch")

    assert "feature specs" in section
    assert "no task" in section


def test_refusal_states_the_cli_also_refuses_task_new_for_s000():
    assert "`ai-team task new --spec S-000`" in _section(
        "### Step 0: Check Out the Planning Branch"
    )
    assert "`ai-team task new --spec S-000`" in _section("## Input Requirements")


def test_common_pitfalls_list_breaking_down_s000():
    assert "S-000" in _section("## Common Pitfalls")


def test_step_headings_are_unchanged_with_exactly_one_step_zero():
    headings = re.findall(r"^#{1,3} .*$", _body(), flags=re.MULTILINE)

    assert headings == EXPECTED_HEADINGS
    assert sum(h.startswith("### Step 0") for h in headings) == 1
