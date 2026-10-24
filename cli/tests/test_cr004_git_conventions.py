"""Regression tests for CR-004: the S-000 planning-branch merge exception."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_BODY = (
    REPO_ROOT
    / "cli"
    / "src"
    / "ai_team"
    / "init"
    / "sources"
    / "skills"
    / "git-conventions"
    / "body.md"
)
GUIDELINE = REPO_ROOT / "ai-process" / "guidelines" / "git-conventions.md"

MERGE_RULE_MARKER = "The Planner merges the planning branch into"
TABLE_ROW_MARKER = "One merge commit per planning branch"
NEVER_CARRIES_MARKER = "never carries a spec amendment"

DOCUMENTS = {"skill": SKILL_BODY, "guideline": GUIDELINE}
MARKERS = [MERGE_RULE_MARKER, TABLE_ROW_MARKER, NEVER_CARRIES_MARKER]


def _statement(path: Path, marker: str) -> str:
    matches = [line for line in path.read_text().splitlines() if marker in line]
    assert len(matches) == 1, f"{path}: expected one line with {marker!r}"
    return matches[0]


@pytest.mark.parametrize("marker", MARKERS)
@pytest.mark.parametrize("document", DOCUMENTS)
def test_statement_names_s000_exception_after_gate_1_once_approved(
    document: str, marker: str
) -> None:
    statement = _statement(DOCUMENTS[document], marker)

    assert "S-000" in statement
    assert "Gate 1" in statement
    assert "`approved`" in statement


@pytest.mark.parametrize("document", DOCUMENTS)
def test_merge_rule_keeps_gate_2_and_no_ff_for_other_planning_branches(
    document: str,
) -> None:
    statement = _statement(DOCUMENTS[document], MERGE_RULE_MARKER)

    assert "only after Gate 2 passes" in statement
    assert statement.count("`--no-ff`") == 2


def test_skill_names_integration_branch_by_placeholder_in_exception() -> None:
    text = SKILL_BODY.read_text()

    assert "dev-agent" not in text
    assert "{{integration_branch}}" in _statement(SKILL_BODY, MERGE_RULE_MARKER)
