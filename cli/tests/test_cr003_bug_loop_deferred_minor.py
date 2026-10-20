"""CR-003 section 3: bug-loop promotes a deferred Minor that proves a real failure."""

from __future__ import annotations

from pathlib import Path

CLI = Path(__file__).resolve().parents[1]
SOURCES = CLI / "src" / "ai_team" / "init" / "sources"
SCAFFOLDS = CLI / "src" / "ai_team" / "init" / "scaffolds"

COPIES = {
    "source": SOURCES / "skills" / "bug-loop" / "body.md",
    "claude": SCAFFOLDS / "claude" / "skills" / "bug-loop" / "SKILL.md",
    "codex": SCAFFOLDS / "codex" / "skills" / "bug-loop" / "SKILL.md",
}


def on_pass_section(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index("#### On PASS")
    end = text.index("#### On FAIL")
    return text[start:end]


def test_on_pass_treats_a_deferred_minor_that_is_a_real_failure_as_fail():
    for name, path in COPIES.items():
        section = on_pass_section(path)
        assert "deferred Minor finding" in section, name
        assert "breaks CI" in section, name
        assert "contradicts the bug's fix contract" in section, name
        assert "treat the verdict as FAIL for that item" in section, name


def test_on_pass_names_promotion_as_the_same_handling_as_cannot_verify():
    for name, path in COPIES.items():
        section = on_pass_section(path)
        assert "same handling as an unconfirmable" in section, name
        assert "`⚠️ Cannot verify from diff`" in section, name


def test_on_pass_appends_resolved_marker_to_the_promoted_deferred_entry():
    for name, path in COPIES.items():
        section = on_pass_section(path)
        assert "`#### Deferred Minor findings`" in section, name
        assert "` — resolved: promoted to FAIL`" in section, name
