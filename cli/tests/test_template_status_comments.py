"""Template frontmatter matches the fields and statuses the CLI writes."""

from ai_team.core.templates import load_template
from ai_team.core.tracker import TASK_STATUSES


def test_adr_template_uses_id_and_cli_statuses() -> None:
    frontmatter = load_template("adr").split("---")[1]
    assert 'id: "ADR-000"' in frontmatter
    assert "number:" not in frontmatter
    assert "# proposed | accepted | superseded" in frontmatter


def test_task_template_status_comment_lists_every_task_status() -> None:
    frontmatter = load_template("task").split("---")[1]
    assert "# " + " | ".join(TASK_STATUSES) in frontmatter


def test_progress_report_decision_sample_uses_accepted() -> None:
    assert "| 001 | Decision title | accepted |" in load_template("report")
