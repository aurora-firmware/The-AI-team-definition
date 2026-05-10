"""Tests for T-018: ai-team report command."""

from datetime import date
from pathlib import Path

from typer.testing import CliRunner


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
