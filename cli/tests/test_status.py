"""Tests for T-007: ai-team status command."""

import json
from pathlib import Path

from typer.testing import CliRunner


TASK_TEMPLATE = """\
---
id: \"{id}\"
title: \"{title}\"
status: {status}
priority: {priority}
assigned-role: {assigned_role}
created: 2026-05-10
{extra_frontmatter}
---

{body}
"""

BUG_TEMPLATE = """\
---
id: \"{id}\"
title: \"{title}\"
severity: {severity}
status: {status}
created: 2026-05-10
---

Body.
"""

SPEC_TEMPLATE = """\
---
title: \"{title}\"
version: \"{version}\"
status: {status}
created: 2026-05-10
author: planner
---

Body.
"""

ADR_TEMPLATE = """\
---
id: \"{id}\"
title: \"{title}\"
status: {status}
created: 2026-05-10
---

Body.
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _task(
    id: str,
    title: str,
    status: str,
    *,
    priority: str = "medium",
    assigned_role: str = "developer",
    body: str = "Body.",
    extra_frontmatter: str = "",
) -> str:
    return TASK_TEMPLATE.format(
        id=id,
        title=title,
        status=status,
        priority=priority,
        assigned_role=assigned_role,
        body=body,
        extra_frontmatter=extra_frontmatter,
    )


def _bug(id: str, title: str, severity: str, status: str) -> str:
    return BUG_TEMPLATE.format(
        id=id,
        title=title,
        severity=severity,
        status=status,
    )


def _spec(title: str, version: str, status: str) -> str:
    return SPEC_TEMPLATE.format(
        title=title,
        version=version,
        status=status,
    )


def _adr(id: str, title: str, status: str) -> str:
    return ADR_TEMPLATE.format(
        id=id,
        title=title,
        status=status,
    )


def test_status_rich_summary_includes_counts_and_key_lists(monkeypatch, tmp_path):
    """`ai-team status` shows counts, in-progress tasks, blocked tasks, and high/critical bugs."""
    from ai_team.cli import app

    _write(tmp_path / "project" / "specs" / "S-001.md", _spec("Spec 1", "0.1", "approved"))
    _write(
        tmp_path / "project" / "tasks" / "pending" / "T-001.md",
        _task("T-001", "Pending task", "pending"),
    )
    _write(
        tmp_path / "project" / "tasks" / "in-progress" / "T-002.md",
        _task("T-002", "In progress task", "in-progress", assigned_role="reviewer"),
    )
    _write(
        tmp_path / "project" / "tasks" / "completed" / "T-003.md",
        _task("T-003", "Completed task", "completed"),
    )
    _write(
        tmp_path / "project" / "tasks" / "blocked" / "T-004.md",
        _task(
            "T-004",
            "Blocked task",
            "blocked",
            extra_frontmatter="blocking-reason: waiting on dependency\n",
        ),
    )
    _write(tmp_path / "project" / "decisions" / "ADR-001.md", _adr("ADR-001", "Decision 1", "accepted"))

    _write(tmp_path / "project" / "bugs" / "open" / "B-001.md", _bug("B-001", "Critical bug", "critical", "open"))
    _write(tmp_path / "project" / "bugs" / "open" / "B-002.md", _bug("B-002", "High bug", "high", "open"))
    _write(tmp_path / "project" / "bugs" / "open" / "B-003.md", _bug("B-003", "Low bug", "low", "open"))
    _write(tmp_path / "project" / "bugs" / "in-progress" / "B-004.md", _bug("B-004", "In-progress bug", "medium", "in-progress"))
    _write(tmp_path / "project" / "bugs" / "resolved" / "B-005.md", _bug("B-005", "Resolved bug", "medium", "resolved"))

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["status"])

    assert result.exit_code == 0
    assert "Active specs" in result.output
    assert "1" in result.output
    assert "Pending tasks" in result.output
    assert "In progress" in result.output
    assert "Completed" in result.output
    assert "Blocked" in result.output
    assert "Open bugs" in result.output
    assert "Bugs in progress" in result.output
    assert "ADRs" in result.output

    assert "T-002" in result.output
    assert "reviewer" in result.output

    assert "T-004" in result.output
    assert "waiting on dependency" in result.output

    assert "B-001" in result.output
    assert "B-002" in result.output
    assert "B-003" not in result.output


def test_status_json_emits_structured_payload_without_rich_table(monkeypatch, tmp_path):
    """`ai-team status --json` emits a single JSON object and no Rich frame characters."""
    from ai_team.cli import app

    _write(tmp_path / "project" / "specs" / "S-001.md", _spec("Spec 1", "0.1", "approved"))
    _write(
        tmp_path / "project" / "tasks" / "in-progress" / "T-100.md",
        _task("T-100", "Do work", "in-progress", assigned_role="developer"),
    )

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["counts"]["specs_active"] == 1
    assert payload["counts"]["tasks"]["in_progress"] == 1
    assert payload["in_progress_tasks"] == [
        {
            "id": "T-100",
            "title": "Do work",
            "assigned_role": "developer",
        }
    ]
    assert "┏" not in result.output
