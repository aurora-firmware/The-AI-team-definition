"""T-089: the Planner reads S-000 at session start and owns the new-system-overview skill."""

from __future__ import annotations

from pathlib import Path

import pytest

AGENTS_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "ai_team"
    / "init"
    / "sources"
    / "agents"
)

PLANNER_SOURCES = [
    pytest.param(AGENTS_DIR / "claude" / "planner.md", id="claude"),
    pytest.param(AGENTS_DIR / "codex" / "planner.toml", id="codex"),
]

NON_PLANNER_ROLES = ["developer", "reviewer", "integrator"]


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).split())


@pytest.mark.parametrize("path", PLANNER_SOURCES)
def test_planner_reads_approved_s000_at_session_start_before_other_specs(path):
    text = _flat(path)

    assert "reads S-000 at the start of a session" in text
    assert "exists and is approved" in text
    assert "before other specs" in text


@pytest.mark.parametrize("path", PLANNER_SOURCES)
def test_planner_lists_the_new_system_overview_skill(path):
    assert "`new-system-overview`" in _text(path)


def test_claude_planner_frontmatter_skills_include_new_system_overview():
    frontmatter_skills = next(
        line
        for line in _text(AGENTS_DIR / "claude" / "planner.md").splitlines()
        if line.startswith("skills:")
    )

    assert "new-system-overview" in frontmatter_skills.split()


@pytest.mark.parametrize("path", PLANNER_SOURCES)
def test_planner_proposes_s000_first_for_a_project_with_no_specs(path):
    text = _flat(path)

    assert "no specs" in text
    assert "proposes writing S-000 first" in text


@pytest.mark.parametrize("path", PLANNER_SOURCES)
def test_planner_does_not_require_s000_when_specs_exist(path):
    assert "S-000 stays optional when specs exist" in _flat(path)


@pytest.mark.parametrize("path", PLANNER_SOURCES)
def test_planner_quality_bar_holds_s000_to_gate_1_criteria_replacing_task_derivation(
    path,
):
    text = _flat(path)

    assert "S-000 Gate 1 criteria" in text
    assert "new-system-overview" in text
    assert "pre-submission checklist" in text
    assert "ai-process/" not in text
    assert "replace" in text


@pytest.mark.parametrize("role", NON_PLANNER_ROLES)
@pytest.mark.parametrize("platform,suffix", [("claude", "md"), ("codex", "toml")])
def test_non_planner_roles_do_not_mention_s000(role, platform, suffix):
    path = AGENTS_DIR / platform / f"{role}.{suffix}"

    assert "S-000" not in _text(path)


@pytest.mark.parametrize("path", PLANNER_SOURCES)
def test_planner_states_the_three_steps_after_s000_gate_1(path):
    text = _flat(path)

    assert "After Gate 1 approves S-000" in text
    assert "completes S-000 with `new-system-overview`" in text
    assert "creates the project bootstrap tasks with `spec-breakdown` on S-000" in text
    assert "proposes the change request from its findings" in text
    assert "brownfield" in text


@pytest.mark.parametrize("path", PLANNER_SOURCES)
def test_planner_states_s000_merges_after_gate_1_as_exception_to_gate_2(path):
    text = _flat(path)

    assert "merging it into `{{integration_branch}}` after Gate 2" in text
    assert (
        "except the S-000 planning branch, which merges into "
        "`{{integration_branch}}` after Gate 1"
    ) in text
