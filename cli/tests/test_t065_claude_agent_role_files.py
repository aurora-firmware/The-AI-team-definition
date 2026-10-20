"""Regression tests for T-065 Claude agent role files."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SOURCE_ROOT = (
    REPO_ROOT / "src" / "ai_team" / "init" / "sources" / "agents" / "claude"
)
CLAUDE_SCAFFOLD_ROOT = (
    REPO_ROOT / "src" / "ai_team" / "init" / "scaffolds" / "claude" / "agents"
)
CLAUDE_ROLES = ("architect", "developer", "integrator", "planner", "reviewer")

CANONICAL_ESCALATION_BLOCK = """Problem: [the criterion that will not pass, or the boundary that was violated]
Attempted: [implementations tried on retry, or why the boundary cannot be honoured as written]
Failed because: [the specific reason — test output, scope mismatch, contradictory requirement]
Question: [specific guidance needed to continue within the approved specification]"""


PLANNER_REQUIRED_SKILLS = frozenset(
    {
        "brainstorm",
        "spec-breakdown",
        "new-spec",
        "new-task",
        "change-request",
        "git-conventions",
    }
)


def _agent_texts(role: str) -> tuple[str, str]:
    source = (CLAUDE_SOURCE_ROOT / f"{role}.md").read_text(encoding="utf-8")
    scaffold = (CLAUDE_SCAFFOLD_ROOT / f"{role}.md").read_text(encoding="utf-8")
    return source, scaffold


def _frontmatter_skills(text: str) -> set[str]:
    """Return the skill names on the frontmatter `skills:` line, in any order."""
    skills_lines = [line for line in text.splitlines() if line.startswith("skills:")]
    assert len(skills_lines) == 1, "expected exactly one `skills:` frontmatter line"
    return set(skills_lines[0].removeprefix("skills:").split())


def test_planner_keeps_change_request_in_skill_surfaces() -> None:
    """AC-1: planner lists change-request in frontmatter and the skill summary."""
    for text in _agent_texts("planner"):
        assert PLANNER_REQUIRED_SKILLS <= _frontmatter_skills(text)
        assert "- `change-request`" in text


def test_reviewer_points_to_code_review_canonical_checklist() -> None:
    """AC-2: reviewer points at code-review instead of owning the full checklist."""
    required_phrases = (
        "The `code-review` skill owns the canonical two-stage checklist",
        "The Reviewer applies that checklist through the skill",
    )
    inlined_checklist_markers = (
        "### Review Checklist",
        "**Stage 1 — Spec compliance**",
        "**Stage 2 — Code quality**",
        "**Bug Fix Addendum**",
        "**Verdict mapping**",
    )

    for text in _agent_texts("reviewer"):
        for phrase in required_phrases:
            assert phrase in text
        for marker in inlined_checklist_markers:
            assert marker not in text


def test_architect_gate_2_output_matches_reconciled_envelope() -> None:
    """AC-3: architect states its role envelope wraps the Gate 2 Findings block."""
    required_phrases = (
        "Gate 2",
        "Findings block",
        "role envelope",
        "does not duplicate Result/Summary fields",
    )

    for text in _agent_texts("architect"):
        for phrase in required_phrases:
            assert phrase in text


def test_all_claude_roles_use_canonical_escalation_request_block() -> None:
    """AC-4: all Claude roles use the frozen four-field escalation request wording."""
    for role in CLAUDE_ROLES:
        for text in _agent_texts(role):
            assert CANONICAL_ESCALATION_BLOCK in text, role
