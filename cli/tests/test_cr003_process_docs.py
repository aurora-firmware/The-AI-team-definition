"""T-118: quality gates and the review checklist describe design-review verification."""

from __future__ import annotations

import re
from pathlib import Path

PROCESS_DIR = Path(__file__).resolve().parents[2] / "ai-process"
QUALITY_GATES_PATH = PROCESS_DIR / "processes" / "quality-gates.md"
REVIEW_CHECKLIST_PATH = PROCESS_DIR / "guidelines" / "review-checklist.md"


def _section(text: str, heading: str) -> str:
    """Return the text under `heading` up to the next heading of equal or higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    start = text.index(heading) + len(heading)
    following = re.search(rf"^#{{1,{level}}} ", text[start:], flags=re.MULTILINE)
    end = start + following.start() if following else len(text)
    return text[start:end]


def _gate_2() -> str:
    text = QUALITY_GATES_PATH.read_text(encoding="utf-8")
    return _section(text, "## Gate 2: Task Plan Preflight")


def _gate_3_stage_2() -> str:
    text = QUALITY_GATES_PATH.read_text(encoding="utf-8")
    return _section(text, "### Stage 2: Code Quality")


def _checklist_tests() -> str:
    text = REVIEW_CHECKLIST_PATH.read_text(encoding="utf-8")
    return _section(text, "### Tests")


def test_gate_2_accepts_named_design_review_for_prose_only_task() -> None:
    gate = _gate_2()
    assert "named design review" in gate
    assert "lists its references" in gate
    assert "changes only prose" in gate


def test_gate_2_requires_test_for_behaviour_a_test_can_observe() -> None:
    assert "changes behaviour a test can observe has a test" in _gate_2()


def test_gate_3_stage_2_records_design_review_in_place_of_test_evidence() -> None:
    stage = _gate_3_stage_2()
    assert "design-review task" in stage
    assert "documents checked" in stage
    assert "each conflict found and fixed" in stage
    assert "in place of test evidence" in stage


def test_checklist_tests_flags_dependence_on_environment_ci_does_not_provide() -> None:
    tests = _checklist_tests()
    assert "environment CI does not provide" in tests
    assert "network access" in tests


def test_checklist_tests_requires_design_review_record_covering_every_reference() -> (
    None
):
    tests = _checklist_tests()
    assert "design-review task" in tests
    assert "covers every listed reference" in tests


def test_existing_phrases_remain() -> None:
    assert "independently verifiable" in _gate_2()
    assert "Relevant tests exist for the changed behavior." in _gate_3_stage_2()
    assert "local test evidence" in _checklist_tests()
