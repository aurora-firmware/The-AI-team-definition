"""T-086: the new-system-overview skill and its dispatch-table row."""

from __future__ import annotations

import tomllib
from pathlib import Path

SKILLS = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "ai_team"
    / "init"
    / "sources"
    / "skills"
)
SKILL_DIR = SKILLS / "new-system-overview"


def _body() -> str:
    return (SKILL_DIR / "body.md").read_text(encoding="utf-8")


def test_skill_source_has_body_and_metadata_with_matching_headers():
    metadata = tomllib.loads((SKILL_DIR / "metadata.toml").read_text(encoding="utf-8"))

    assert (SKILL_DIR / "body.md").is_file()
    assert "name: new-system-overview" in metadata["claude"]["header"]
    assert "name: new-system-overview" in metadata["codex"]["header"]
    assert metadata["claude"]["header"] == metadata["codex"]["header"]


def test_body_runs_overview_command_and_names_all_seven_sections():
    body = _body()

    assert "ai-team spec new --overview --json" in body
    assert "ai-team list specs" in body
    assert "spec-authoring-guide.md" in body
    for section in (
        "Purpose",
        "Users",
        "Pain points",
        "Use cases",
        "Solution overview",
        "Components",
        "Project exclusions",
    ):
        assert section in body, section


def test_body_has_checklist_and_architect_then_human_gate_handoff():
    body = _body()

    assert "Pre-submission checklist" in body
    assert "[TODO]" in body
    assert "Architect" in body
    assert "Gate 1" in body
    assert body.index("Architect") < body.rindex("Gate 1")


def test_body_has_brownfield_section_reporting_findings_without_amending():
    body = _body()

    assert "## Brownfield adoption" in body
    brownfield = body.split("## Brownfield adoption", 1)[1]
    assert "finding" in brownfield
    assert "never amend" in brownfield.lower()


def test_dispatch_table_names_new_system_overview():
    body = (SKILLS / "using-ai-team" / "body.md").read_text(encoding="utf-8")
    rows = [line for line in body.splitlines() if line.startswith("| ")]

    assert any("`new-system-overview`" in row for row in rows)
