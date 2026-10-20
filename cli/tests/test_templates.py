from pathlib import Path

import pytest

from ai_team.core.templates import load_template


def test_load_template_task_matches_bundled_source() -> None:
    source_template = (
        Path(__file__).resolve().parents[1] / "src/ai_team/templates/task.md"
    )

    assert load_template("task") == source_template.read_text(encoding="utf-8")


def test_load_template_change_request_matches_bundled_source() -> None:
    source_template = (
        Path(__file__).resolve().parents[1] / "src/ai_team/templates/change-request.md"
    )

    assert load_template("change-request") == source_template.read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize(
    "kind",
    ["task", "bug", "spec", "adr", "report", "change-request", "system-overview"],
)
def test_load_template_returns_non_empty_frontmatter_for_each_kind(kind: str) -> None:
    content = load_template(kind)

    assert content
    assert content.startswith("---")


def test_change_request_template_mentions_desired_changes_and_spec_amendments() -> None:
    content = load_template("change-request").lower()

    assert "desired changes" in content
    assert "spec amendments" in content


def test_load_template_rejects_unknown_kind_with_supported_kinds() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Unsupported template kind 'unknown'. Supported kinds: task, bug, spec, adr, report, change-request, system-overview"
        ),
    ):
        load_template("unknown")


def _headings(content: str, prefix: str) -> list[str]:
    return [
        line[len(prefix) :].strip()
        for line in content.splitlines()
        if line.startswith(prefix)
    ]


def test_system_overview_template_matches_bundled_source() -> None:
    source_template = (
        Path(__file__).resolve().parents[1] / "src/ai_team/templates/system-overview.md"
    )

    assert load_template("system-overview") == source_template.read_text(
        encoding="utf-8"
    )


def test_system_overview_template_has_the_s000_sections_in_order() -> None:
    assert _headings(load_template("system-overview"), "## ") == [
        "Purpose",
        "Users",
        "Pain points",
        "Use cases",
        "Solution overview",
        "Components",
        "Project exclusions",
        "Amendment Log",
    ]


@pytest.mark.parametrize(
    "heading",
    ["Architecture", "Workflow", "Configuration Requirements", "Implementation Order"],
)
def test_system_overview_template_omits_feature_spec_heading(heading: str) -> None:
    assert heading not in _headings(load_template("system-overview"), "## ")


def test_system_overview_template_uses_the_spec_title_placeholders() -> None:
    content = load_template("system-overview")

    assert 'title: "[Specification Title]"' in content
    assert "\n# [Specification Title]\n" in content


def test_system_overview_template_shows_one_component_example_with_all_fields() -> None:
    content = load_template("system-overview")

    for label in ("Name", "Responsibility", "Boundary", "Works with"):
        assert f"- **{label}:**" in content
