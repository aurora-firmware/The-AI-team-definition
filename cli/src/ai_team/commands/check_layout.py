"""``ai-team check-layout`` command."""

from __future__ import annotations

import os
from pathlib import Path

import typer

from ai_team.core.layout import LayoutFinding
from ai_team.core.layout import check_layout as run_layout_checks
from ai_team.core.result import Result

NAME = "check-layout"
app = typer.Typer(
    help="Check the repository layout and report actionable findings.",
    invoke_without_command=True,
)


def _repository_root(cwd: Path) -> Path:
    configured_root = os.environ.get("AI_TEAM_ROOT")
    if configured_root:
        return Path(configured_root).resolve()

    cwd = cwd.resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / ".ai-team.toml").exists() or (candidate / "project").is_dir():
            return candidate
    return cwd


def _sort_key(finding: LayoutFinding) -> tuple[int, str, str, str]:
    return (
        finding.level,
        finding.path,
        finding.problem,
        finding.suggested_fix,
    )


def check_repository_layout(repo: Path) -> Result:
    """Run all layout checks; status is 1 when any finding exists.

    Findings are sorted and keep the suggested fix apart from the message.
    """
    findings = sorted(run_layout_checks(repo), key=_sort_key)
    return Result(
        status=1 if findings else 0,
        payload={
            "findings": [
                {
                    "level": finding.level,
                    "path": finding.path,
                    "message": finding.problem,
                    "suggested_fix": finding.suggested_fix,
                }
                for finding in findings
            ]
        },
    )


def _render_findings(findings: list[dict[str, object]]) -> None:
    if not findings:
        typer.echo("Layout check passed: no findings.")
        return

    typer.echo(f"{len(findings)} layout findings")
    for finding in findings:
        typer.echo()
        typer.echo(f"Level: {finding['level']}")
        typer.echo(f"Path: {finding['path']}")
        typer.echo(f"Problem: {finding['message']}")
        typer.echo(f"Suggested fix: {finding['suggested_fix']}")


@app.callback()
def default() -> None:
    """Run all repository layout checks without changing the repository."""
    result = check_repository_layout(_repository_root(Path.cwd()))
    _render_findings(result.payload["findings"])
    if result.status:
        raise typer.Exit(code=result.status)
