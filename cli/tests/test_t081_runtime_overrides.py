"""Tests for T-081: injectable today and framework version."""

from __future__ import annotations

import re
import tomllib
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

FIXED_TODAY = "2031-02-03"
TODAY_VAR = "AI_TEAM_TODAY"
VERSION_VAR = "AI_TEAM_FRAMEWORK_VERSION"
SRC = Path(__file__).resolve().parents[1] / "src" / "ai_team"


def _invoke(monkeypatch, tmp_path: Path, args: list[str]):
    from ai_team.cli import app

    monkeypatch.chdir(tmp_path)
    return CliRunner().invoke(app, args)


def _init_project(monkeypatch, tmp_path: Path) -> None:
    result = _invoke(
        monkeypatch, tmp_path, ["init", "--tools", "claude", "--no-interactive"]
    )
    assert result.exit_code == 0, result.output


def test_today_returns_real_date_without_override(monkeypatch) -> None:
    from ai_team.core.runtime import today

    monkeypatch.delenv(TODAY_VAR, raising=False)

    assert today() == date.today()


def test_today_returns_override_date(monkeypatch) -> None:
    from ai_team.core.runtime import today

    monkeypatch.setenv(TODAY_VAR, FIXED_TODAY)

    assert today() == date(2031, 2, 3)


def test_today_fails_naming_variable_when_override_is_not_iso(monkeypatch) -> None:
    from ai_team.core.runtime import today

    monkeypatch.setenv(TODAY_VAR, "03/02/2031")

    with pytest.raises(ValueError, match=TODAY_VAR):
        today()


def test_framework_version_uses_installed_metadata_without_override(
    monkeypatch,
) -> None:
    from ai_team.core.runtime import framework_version

    monkeypatch.delenv(VERSION_VAR, raising=False)
    monkeypatch.setattr("importlib.metadata.version", lambda name: "7.7.7")

    assert framework_version() == "7.7.7"


def test_framework_version_returns_override(monkeypatch) -> None:
    from ai_team.core.runtime import framework_version

    monkeypatch.setenv(VERSION_VAR, "9.9.9")

    assert framework_version() == "9.9.9"


@pytest.mark.parametrize(
    "args",
    [
        ["spec", "new", "Demo"],
        ["adr", "new", "Demo"],
        ["bug", "new", "Demo"],
        ["change-request", "new", "Demo"],
        ["task", "new", "Demo"],
    ],
)
def test_new_commands_write_overridden_created_date(
    monkeypatch, tmp_path: Path, args: list[str]
) -> None:
    _init_project(monkeypatch, tmp_path)
    monkeypatch.setenv(TODAY_VAR, FIXED_TODAY)

    result = _invoke(monkeypatch, tmp_path, args)

    assert result.exit_code == 0, result.output
    created = Path(result.stdout.strip().splitlines()[-1])
    text = created.read_text(encoding="utf-8")
    assert re.search(rf"^created: '?{FIXED_TODAY}'?$", text, re.MULTILINE)


def test_task_block_work_log_uses_overridden_date(monkeypatch, tmp_path: Path) -> None:
    _init_project(monkeypatch, tmp_path)
    monkeypatch.setenv(TODAY_VAR, FIXED_TODAY)
    created = _invoke(monkeypatch, tmp_path, ["task", "new", "Demo"])
    task_id = Path(created.stdout.strip()).name.split("-demo")[0]
    _invoke(monkeypatch, tmp_path, ["task", "start", task_id])

    result = _invoke(monkeypatch, tmp_path, ["task", "block", task_id, "--reason", "x"])

    assert result.exit_code == 0, result.output
    blocked = next((tmp_path / "project" / "tasks" / "blocked").glob("*.md"))
    assert f"### Session 1 — {FIXED_TODAY}" in blocked.read_text(encoding="utf-8")


def test_report_uses_overridden_date(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "project").mkdir()
    monkeypatch.setenv(TODAY_VAR, FIXED_TODAY)

    result = _invoke(monkeypatch, tmp_path, ["report"])

    assert result.exit_code == 0, result.output
    report = (
        tmp_path / "project" / "docs" / "reports" / f"progress-report-{FIXED_TODAY}.md"
    )
    assert report.is_file()


def test_archive_cutoff_uses_overridden_date(monkeypatch, tmp_path: Path) -> None:
    task = tmp_path / "project" / "tasks" / "completed" / "T-100-old.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        '---\nid: "T-100"\ntitle: "Old"\nstatus: completed\npriority: medium\n'
        "assigned-role: developer\ncreated: 2025-01-15\n---\n\nBody.\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(TODAY_VAR, "2025-02-01")

    result = _invoke(monkeypatch, tmp_path, ["archive"])

    assert result.exit_code == 0, result.output
    assert task.exists()


def test_init_marker_records_overridden_framework_version(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv(VERSION_VAR, "9.9.9")

    result = _invoke(
        monkeypatch, tmp_path, ["init", "--tools", "claude", "--no-interactive"]
    )

    assert result.exit_code == 0, result.output
    data = tomllib.loads((tmp_path / ".ai-team.toml").read_text(encoding="utf-8"))
    assert data["init"]["framework_version"] == "9.9.9"


def test_resolve_layout_compares_against_overridden_framework_version(
    monkeypatch, tmp_path: Path
) -> None:
    from ai_team.core.layout import resolve_layout

    (tmp_path / ".ai-team.toml").write_text(
        '[project]\ndir = "project"\n\n[init]\ntools = ["claude"]\n'
        'framework_version = "9.9.9"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv(VERSION_VAR, "9.9.9")

    contract, _ = resolve_layout(tmp_path)

    assert contract is not None
    assert contract.current_version == "9.9.9"


def test_invalid_today_override_fails_naming_variable_through_cli(
    monkeypatch, tmp_path: Path
) -> None:
    (tmp_path / "project").mkdir()
    monkeypatch.setenv(TODAY_VAR, "not-a-date")

    result = _invoke(monkeypatch, tmp_path, ["spec", "new", "Demo"])

    assert result.exit_code != 0
    assert TODAY_VAR in str(result.exception)


def test_only_runtime_module_supplies_today_and_version() -> None:
    offenders = []
    pattern = re.compile(r"date\.today\(|metadata\.version\(")
    for folder in ("commands", "core"):
        for path in (SRC / folder).glob("*.py"):
            if path.name == "runtime.py":
                continue
            if pattern.search(path.read_text(encoding="utf-8")):
                offenders.append(str(path.relative_to(SRC)))

    assert offenders == []
    runtime = (SRC / "core" / "runtime.py").read_text(encoding="utf-8")
    assert "from importlib.metadata import" not in runtime
