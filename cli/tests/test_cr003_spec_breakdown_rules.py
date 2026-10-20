"""CR-003 T-109: spec-breakdown chooses each task's verification mode."""

from __future__ import annotations

from pathlib import Path

CLI = Path(__file__).resolve().parents[1]
SOURCE = (
    CLI
    / "src"
    / "ai_team"
    / "init"
    / "sources"
    / "skills"
    / "spec-breakdown"
    / "body.md"
)
SCAFFOLDS = [
    CLI
    / "src"
    / "ai_team"
    / "init"
    / "scaffolds"
    / tool
    / "skills"
    / "spec-breakdown"
    / "SKILL.md"
    for tool in ("claude", "codex")
]


def flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def step3_bullet(text: str) -> str:
    start = text.index("- **Verification mode**")
    return text[start : text.index("During task writing", start)]


def test_step3_requires_choosing_test_or_design_review_per_task():
    bullet = step3_bullet(flat(SOURCE))
    assert "the Planner decides" in bullet
    assert "**test**" in bullet
    assert "**design review**" in bullet


def test_step3_gives_code_cli_output_or_observable_rule_a_test_with_test_file_listed():
    bullet = step3_bullet(flat(SOURCE))
    assert "changes code, CLI output, or a rule a test can observe" in bullet
    assert "test file is in Files to Touch" in bullet
    assert "Anything a test can observe gets a test" in bullet


def test_step3_keeps_baseline_suite_rule_for_shared_interfaces():
    bullet = step3_bullet(flat(SOURCE))
    assert "project's documented baseline/full-suite command" in bullet


def test_step3_prose_only_task_gets_design_review_with_references():
    bullet = step3_bullet(flat(SOURCE))
    assert "changes only prose" in bullet
    assert "`Design review:` Verification form" in bullet
    assert "the source spec" in bullet
    assert "the accepted ADRs" in bullet
    assert "S-000 when it exists" in bullet


def test_verifiable_quality_criterion_accepts_named_design_review():
    text = flat(SOURCE)
    start = text.index("Every task is **verifiable**")
    assert (
        "design review" in text[start : text.index("Every task is **self-contained**")]
    )


def test_verification_pitfall_accepts_named_design_review():
    text = flat(SOURCE)
    start = text.index("- **Forgetting verification")
    assert "design review" in text[start : text.index("- **File conflicts**")]


def test_generated_scaffolds_carry_the_verification_mode_rule():
    for scaffold in SCAFFOLDS:
        assert "**Verification mode**" in flat(scaffold)
