"""Issue #31: process practices adopted from the superpowers comparison report.

Each test pins one adopted practice to the skill, template, or guide that owns it,
so a later edit cannot silently drop it.
"""

from __future__ import annotations

from pathlib import Path

CLI = Path(__file__).resolve().parents[1]
REPO = CLI.parent
SOURCES = CLI / "src" / "ai_team" / "init" / "sources"


def skill(name: str) -> str:
    return (SOURCES / "skills" / name / "body.md").read_text(encoding="utf-8")


def agent(name: str) -> str:
    return (SOURCES / "agents" / "claude" / f"{name}.md").read_text(encoding="utf-8")


# -- Phase 1: rationalization tables and review calibration ------------------


def test_enforcement_skills_carry_a_rationalizations_table():
    for name in ("tdd", "debug", "integrate", "code-review", "git-conventions"):
        body = skill(name)
        assert "## Rationalizations" in body, name
        section = body.split("## Rationalizations", 1)[1].split("\n## ", 1)[0]
        rows = [line for line in section.splitlines() if line.startswith('| "')]
        assert len(rows) >= 5, name
        assert body.index("## Rationalizations") < body.index("## Common Pitfalls"), (
            name
        )


def test_code_review_defines_severity_and_ties_the_verdict_to_it():
    body = skill("code-review")

    for term in ("**Critical**", "**Important**", "**Minor**"):
        assert term in body
    assert "cannot be trusted until it is fixed" in body
    assert "Critical or Important finding" in body


def test_code_review_does_not_trust_the_report_or_rerun_developer_tests():
    body = skill("code-review")

    assert "unverified claims" in body
    assert "never lowers a finding's severity" in body
    assert "Do not re-run tests the Work Log already shows passing" in body


def test_code_review_has_a_cannot_verify_category_without_a_new_verdict_word():
    body = skill("code-review")

    assert "⚠️ Cannot verify from diff" in body
    assert "Verdict: `PASS`" in body and "Verdict: `FAIL`" in body
    assert "Verdict: `CANNOT" not in body


def test_loops_keep_reviewer_prompts_neutral_and_resolve_unverifiable_items():
    for name in ("dev-loop", "bug-loop"):
        body = skill(name)
        assert "Keep the Reviewer prompt neutral" in body, name
        for phrase in ("do not flag", "at most Minor", "the plan chose"):
            assert phrase in body, (name, phrase)
        assert "Do not re-run tests the Work Log already shows passing" in body, name
        assert "Cannot verify from diff" in body, name
        assert "Deferred Minor findings" in body, name


def test_status_report_rolls_up_deferred_minor_findings_for_gate_5():
    body = skill("status-report")

    assert "Deferred Minor findings" in body
    assert "### Deferred Minor Findings" in body
    assert "silent discard" in body
