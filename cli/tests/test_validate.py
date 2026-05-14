"""Tests for T-017: ai-team validate command."""

import json
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
    """`ai-team validate` exits 0 with zero findings for valid artifacts."""
    from ai_team.cli import app

    _seed_valid_project(tmp_path)

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["validate"])

    assert result.exit_code == 0
    assert "0 finding" in result.output


def test_validate_emits_error_when_status_disagrees_with_state_folder(
    monkeypatch, tmp_path
):
    """Task and bug status fields must match the state folder they live in."""
    from ai_team.cli import app

    _seed_valid_project(tmp_path)
    _write(
        tmp_path / "project" / "tasks" / "pending" / "T-002-status-mismatch.md",
        _task("T-002", "Mismatch Task", "completed"),
    )

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["validate", "--json"])

    assert result.exit_code != 0
    findings = json.loads(result.output)
    assert any(
        finding["code"] == "status-mismatch"
        and finding["path"].endswith("project/tasks/pending/T-002-status-mismatch.md")
        for finding in findings
    )


def test_validate_emits_error_when_cross_references_do_not_resolve(
    monkeypatch, tmp_path
):
    """Missing task->spec, bug->task, and ADR supersedes references are errors."""
    from ai_team.cli import app

    _seed_valid_project(tmp_path)
    _write(
        tmp_path / "project" / "tasks" / "pending" / "T-003-missing-spec.md",
        _task(
            "T-003",
            "Task Missing Spec",
            "pending",
            extra_frontmatter='spec: "missing-spec"\n',
        ),
    )
    _write(
        tmp_path / "project" / "bugs" / "open" / "B-002-missing-task.md",
        _bug(
            "B-002",
            "Bug Missing Task",
            "open",
            extra_frontmatter='task: "T-999"\n',
        ),
    )
    _write(
        tmp_path / "project" / "decisions" / "ADR-002-missing-supersedes.md",
        _adr(
            "ADR-002",
            "Missing Supersedes",
            extra_frontmatter='supersedes: "ADR-999"\n',
        ),
    )

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["validate", "--json"])

    assert result.exit_code != 0
    findings = json.loads(result.output)
    assert any(
        finding["code"] == "task-spec-missing" and "missing-spec" in finding["message"]
        for finding in findings
    )
    assert any(
        finding["code"] == "bug-task-missing" and "T-999" in finding["message"]
        for finding in findings
    )
    assert any(
        finding["code"] == "adr-supersedes-missing" and "ADR-999" in finding["message"]
        for finding in findings
    )


def test_validate_json_outputs_plain_list_without_rich_table(monkeypatch, tmp_path):
    """`validate --json` prints only a JSON list and no Rich table/frame output."""
    from ai_team.cli import app

    _seed_valid_project(tmp_path)
    _write(
        tmp_path / "project" / "tasks" / "pending" / "T-010-bad-status.md",
        _task("T-010", "Bad status", "completed"),
    )

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["validate", "--json"])

    assert result.exit_code != 0
    parsed = json.loads(result.output)
    assert isinstance(parsed, list)
    assert "┏" not in result.output
    assert "Validation Findings" not in result.output


def test_validate_exits_non_zero_when_any_error_finding_exists(monkeypatch, tmp_path):
    """Any error-level finding causes a non-zero exit code."""
    from ai_team.cli import app

    _seed_valid_project(tmp_path)
    _write(
        tmp_path / "project" / "bugs" / "open" / "B-010-status-mismatch.md",
        _bug("B-010", "Bad bug status", "resolved"),
    )

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["validate"])

    assert result.exit_code != 0
    assert "status-mismatch" in result.output


def test_validate_detects_frontmatter_id_and_filename_violations(monkeypatch, tmp_path):
    """Validation reports required-frontmatter, id pattern, and filename issues."""
    from ai_team.cli import app

    _seed_valid_project(tmp_path)
    _write(
        tmp_path / "project" / "tasks" / "pending" / "not-task.md",
        _task("TASK-001", "Bad Task ID", "pending"),
    )
    _write(
        tmp_path / "project" / "specs" / "Bad Spec Name.md",
        """\
---
title: "Bad Spec"
version: "0.1"
status: approved
created: 2026-05-10
---

Body.
""",
    )
    _write(
        tmp_path / "project" / "decisions" / "ADR-010.md",
        _adr("ADR-010", "Missing Slug"),
    )

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["validate", "--json"])

    assert result.exit_code != 0
    findings = json.loads(result.output)
    codes = {finding["code"] for finding in findings}
    assert "frontmatter-invalid" in codes
    assert "id-pattern" in codes
    assert "filename-pattern" in codes


def test_validate_scope_flags_limit_checked_artifact_kinds(monkeypatch, tmp_path):
    """Selecting `--tasks` excludes unrelated bug validation findings."""
    from ai_team.cli import app

    _seed_valid_project(tmp_path)
    _write(
        tmp_path / "project" / "bugs" / "open" / "B-010-status-mismatch.md",
        _bug("B-010", "Bad bug status", "resolved"),
    )

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["validate", "--tasks", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == []
