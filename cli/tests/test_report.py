"""Tests for T-018: ai-team report command."""

from datetime import date
from pathlib import Path

from typer.testing import CliRunner

TASK_TEMPLATE = """\
---
id: "{id}"
title: "{title}"
status: {status}
priority: medium
assigned-role: {assigned_role}
created: 2026-05-10
{extra_frontmatter}
---

Body.
"""

BUG_TEMPLATE = """\
---
id: "{id}"
title: "{title}"
severity: {severity}
status: {status}
created: 2026-05-10
---

Body.
"""

SPEC_TEMPLATE = """\
---
title: "{title}"
version: "0.1"
status: {status}
created: 2026-05-10
author: planner
---

Body.
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_report_writes_default_dated_file_and_creates_reports_dir(
    monkeypatch, tmp_path: Path
) -> None:
    """`ai-team report` writes to project/docs/reports/progress-report-YYYY-MM-DD.md."""
    from ai_team.cli import app

    (tmp_path / "project").mkdir()

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["report"])

    assert result.exit_code == 0
    expected = (
        tmp_path
        / "project"
        / "docs"
        / "reports"
        / f"progress-report-{date.today().isoformat()}.md"
    )
    assert expected.exists()
    assert expected.read_text(encoding="utf-8").startswith("---")


def test_report_out_writes_populated_report_with_status_summary_fields(
    monkeypatch, tmp_path: Path
) -> None:
    """`ai-team report --out` writes a populated report to the requested path."""
    from ai_team.cli import app

    _write(
        tmp_path / "project" / "specs" / "S-001.md",
        SPEC_TEMPLATE.format(title="Spec 1", status="approved"),
    )
    _write(
        tmp_path / "project" / "tasks" / "pending" / "T-001.md",
        TASK_TEMPLATE.format(
            id="T-001",
            title="Pending task",
            status="pending",
            assigned_role="developer",
            extra_frontmatter="",
        ),
    )
    _write(
        tmp_path / "project" / "tasks" / "in-progress" / "T-002.md",
        TASK_TEMPLATE.format(
            id="T-002",
            title="Build report",
            status="in-progress",
            assigned_role="reviewer",
            extra_frontmatter="",
        ),
    )
    _write(
        tmp_path / "project" / "tasks" / "blocked" / "T-003.md",
        TASK_TEMPLATE.format(
            id="T-003",
            title="Blocked task",
            status="blocked",
            assigned_role="developer",
            extra_frontmatter="blocking-reason: waiting on API contract\n",
        ),
    )
    _write(
        tmp_path / "project" / "bugs" / "open" / "B-001.md",
        BUG_TEMPLATE.format(
            id="B-001",
            title="Critical issue",
            severity="critical",
            status="open",
        ),
    )

    out_path = tmp_path / "custom" / "reports" / "status.md"
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["report", "--out", str(out_path)])

    assert result.exit_code == 0
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")

    assert "Active specs: 1" in content
    assert "Pending tasks: 1" in content
    assert "In progress tasks: 1" in content
    assert "Blocked tasks: 1" in content
    assert "Open bugs: 1" in content

    assert "| T-002 | Build report | reviewer | actively progressing |" in content
    assert (
        "| T-003 | Blocked task | waiting on API contract | "
        "Resolve blocker: waiting on API contract |"
    ) in content
    assert "| B-001 | Critical issue | critical | open | n/a |" in content

    assert "1. Unblock T-003: waiting on API contract" in content
    assert "- Blocked tasks may delay delivery." in content


def test_report_succeeds_with_legacy_bug_missing_created(
    monkeypatch, tmp_path: Path
) -> None:
    """`ai-team report` exits 0 when a resolved bug artifact has no 'created' field.

    B-004 regression: parse_bug used to call _require(data, "created", path)
    which aborts on legacy artifacts that pre-date the 'created' requirement.
    The report must complete and write the dated file even when resolved bugs
    are missing that field.
    """
    from ai_team.cli import app

    legacy_bug = """\
---
id: "B-001"
title: "Legacy resolved bug"
severity: medium
status: resolved
---

Body.
"""
    _write(tmp_path / "project" / "bugs" / "resolved" / "B-001.md", legacy_bug)

    out_path = tmp_path / "report.md"
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["report", "--out", str(out_path)])

    assert result.exit_code == 0, f"Command failed: {result.output}"
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "B-001" in content
