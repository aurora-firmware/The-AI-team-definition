"""T-088: using-ai-team and brainstorm suggest the system overview when S-000 is absent."""

from __future__ import annotations

import re
from pathlib import Path

SKILLS = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "ai_team"
    / "init"
    / "sources"
    / "skills"
)
USING = (SKILLS / "using-ai-team" / "body.md").read_text(encoding="utf-8")
BRAINSTORM = (SKILLS / "brainstorm" / "body.md").read_text(encoding="utf-8")


def _step_zero_opening_paragraph(body: str) -> str:
    section = body.split("### Step 0: Triage the Scope\n", 1)[1]
    return section.strip().split("\n\n", 1)[0]


def test_using_ai_team_suggests_system_overview_when_no_s000_exists():
    assert "`ai-team list specs`" in USING
    assert "S-000" in USING
    suggestion = USING.split("`ai-team list specs`", 1)[1]
    assert "`new-system-overview`" in suggestion.split("\n\n", 1)[0]


def test_brainstorm_step_zero_opens_with_the_system_overview_suggestion():
    opening = _step_zero_opening_paragraph(BRAINSTORM)

    assert "`ai-team list specs`" in opening
    assert "S-000" in opening
    assert "`new-system-overview`" in opening


def test_brainstorm_keeps_its_step_headings_unchanged():
    headings = re.findall(r"^### Step \d+: .*$", BRAINSTORM, flags=re.MULTILINE)

    assert headings[0] == "### Step 0: Triage the Scope"
    numbers = [int(re.search(r"\d+", heading).group()) for heading in headings]
    assert numbers == list(range(len(numbers)))


def test_both_skills_say_the_human_may_decline_and_it_is_not_repeated():
    for body in (USING, BRAINSTORM):
        assert "declines" in body
        assert "not repeated in the same session" in body


def test_using_ai_team_dispatch_row_for_system_overview_is_unchanged():
    assert (
        "| The project has no S-000, or is being adopted into the ai-team process "
        "| `new-system-overview` |"
    ) in USING
