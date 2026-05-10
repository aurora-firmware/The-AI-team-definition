"""Tests for T-017: ai-team validate command."""

from pathlib import Path

from typer.testing import CliRunner


TASK_TEMPLATE = """\
---
id: "{id}"
title: "{title}"
status: {status}
priority: medium
assigned-role: developer
created: 2026-05-10
{extra_frontmatter}
---

Body.
"""

BUG_TEMPLATE = """\
---
id: "{id}"
title: "{title}"
severity: medium
status: {status}
created: 2026-05-10
{extra_frontmatter}
---

Body.
"""

SPEC_TEMPLATE = """\
---
title: "{title}"
version: "0.1"
status: approved
created: 2026-05-10
author: planner
id: "{id}"
---

Body.
"""

ADR_TEMPLATE = """\
---
id: "{id}"
title: "{title}"
status: accepted
created: 2026-05-10
{extra_frontmatter}
---

Body.
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _task(task_id: str, title: str, status: str, *, extra_frontmatter: str = "") -> str:
    return TASK_TEMPLATE.format(
        id=task_id,
        title=title,
        status=status,
        extra_frontmatter=extra_frontmatter,
    )


def _bug(bug_id: str, title: str, status: str, *, extra_frontmatter: str = "") -> str:
    return BUG_TEMPLATE.format(
        id=bug_id,
        title=title,
        status=status,
        extra_frontmatter=extra_frontmatter,
    )


def _spec(spec_id: str, title: str) -> str:
    return SPEC_TEMPLATE.format(id=spec_id, title=title)


def _adr(adr_id: str, title: str, *, extra_frontmatter: str = "") -> str:
    return ADR_TEMPLATE.format(
        id=adr_id,
        title=title,
        extra_frontmatter=extra_frontmatter,
    )


def _seed_valid_project(root: Path) -> None:
    _write(
        root / "project" / "specs" / "roadmap-spec.md",
        _spec("S-001", "Roadmap Spec"),
    )
    _write(
        root / "project" / "tasks" / "pending" / "T-001-roadmap-task.md",
        _task(
            "T-001",
            "Roadmap Task",
            "pending",
            extra_frontmatter='spec: "roadmap-spec"\n',
        ),
    )
    _write(
        root / "project" / "bugs" / "open" / "B-001-roadmap-bug.md",
        _bug(
            "B-001",
            "Roadmap Bug",
            "open",
            extra_frontmatter='task: "T-001"\n',
        ),
    )
    _write(
        root / "project" / "decisions" / "ADR-001-roadmap-decision.md",
        _adr("ADR-001", "Roadmap Decision"),
    )


def test_validate_exits_zero_and_reports_zero_findings_for_clean_project(
    monkeypatch, tmp_path
):
    """`ai-team validate` exits 0 and reports zero findings when all artifacts are valid."""
    from ai_team.cli import app

    _seed_valid_project(tmp_path)

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["validate"])

    assert result.exit_code == 0
    assert "0 finding" in result.output
