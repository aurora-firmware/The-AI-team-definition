"""
Tests for T-125: usage guide documents the Work Log heading `ai-team status` reads.

Covers:
  AC-1: the Gate 5 status section states the integration result is read only
        from headings of the form `### Session N — YYYY-MM-DD`.
  AC-2: the section states other heading forms report `not found`.
  AC-3: the documented heading, instantiated, matches `_SESSION_HEADING`.
  AC-4: phrases read by tests/test_usage_guide.py remain.
"""

from __future__ import annotations

import re
from pathlib import Path

from ai_team.commands.status import _SESSION_HEADING

USAGE_MD = Path(__file__).resolve().parents[1] / "docs" / "usage.md"
DOCUMENTED_HEADING = "### Session N — YYYY-MM-DD"


def _status_section() -> str:
    content = USAGE_MD.read_text(encoding="utf-8")
    start = content.index("### Generate a Gate 5 status report")
    end = content.index("\n### ", start + 1)
    return content[start:end]


def _status_paragraph() -> str:
    section = _status_section()
    paragraph = next(
        p for p in section.split("\n\n") if p.startswith("`ai-team status` shows")
    )
    return " ".join(paragraph.split())


def test_status_section_documents_session_heading_form_in_code_span() -> None:
    assert f"`{DOCUMENTED_HEADING}`" in _status_paragraph()


def test_status_section_states_integration_result_is_read_only_from_that_form() -> None:
    paragraph = _status_paragraph()
    assert "only from Work Log headings" in paragraph


def test_status_section_states_other_heading_forms_report_not_found() -> None:
    paragraph = _status_paragraph()
    assert "any other heading form" in paragraph
    assert "reports `not found`" in paragraph


def test_documented_heading_instantiated_matches_session_heading_regex() -> None:
    documented = re.search(r"`(### Session [^`]+)`", _status_paragraph())
    assert documented is not None
    instantiated = (
        documented.group(1).replace("N", "3").replace("YYYY-MM-DD", "2026-10-20")
    )
    assert _SESSION_HEADING.match(instantiated)


def test_usage_guide_keeps_gate_5_status_and_report_commands() -> None:
    section = _status_section()
    assert "ai-team status" in section
    assert "ai-team report" in section
