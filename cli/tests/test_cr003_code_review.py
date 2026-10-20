"""CR-003 section 3: the code-review severity rubric for CI and Description findings."""

from __future__ import annotations

from pathlib import Path

CLI = Path(__file__).resolve().parents[1]
SOURCES = CLI / "src" / "ai_team" / "init" / "sources"
SCAFFOLDS = CLI / "src" / "ai_team" / "init" / "scaffolds"

COPIES = {
    "source": SOURCES / "skills" / "code-review" / "body.md",
    "claude": SCAFFOLDS / "claude" / "skills" / "code-review" / "SKILL.md",
    "codex": SCAFFOLDS / "codex" / "skills" / "code-review" / "SKILL.md",
}


def severity_section(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index("### Severity")
    end = text.index("### Cannot Verify From the Diff")
    return text[start:end]


def test_severity_makes_ci_breaking_findings_at_least_important():
    for name, path in COPIES.items():
        section = severity_section(path)
        assert "at least **Important**" in section, name
        assert "breaks CI" in section, name
        for example in (
            "local git history",
            "network access",
            "installed tool versions",
        ):
            assert example in section, (name, example)


def test_severity_directs_reviewer_to_compare_new_tests_against_ci_configuration():
    for name, path in COPIES.items():
        section = severity_section(path)
        assert "CI configuration" in section, name
        assert "compare" in section and "new tests" in section, name


def test_severity_names_no_ci_provider_or_file_path():
    section = severity_section(COPIES["source"])
    for forbidden in (
        "GitHub",
        "GitLab",
        ".github",
        ".gitlab-ci",
        "Jenkins",
        "CircleCI",
    ):
        assert forbidden not in section


def test_never_minor_rule_covers_contradicting_a_task_description_sentence():
    for name, path in COPIES.items():
        section = severity_section(path)
        assert "never Minor" in section, name
        assert "explicit sentence of the task Description" in section, name
        assert "The function never raises" in section, name
