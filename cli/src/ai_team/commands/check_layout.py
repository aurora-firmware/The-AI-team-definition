"""``ai-team check-layout`` command."""

from __future__ import annotations

import os
from pathlib import Path

import typer

from ai_team.core.layout import LayoutFinding
from ai_team.core.layout import check_layout as run_layout_checks

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


def _render_findings(findings: list[LayoutFinding]) -> None:
    typer.echo(f"{len(findings)} layout findings")
    for finding in sorted(findings, key=_sort_key):
        typer.echo()
        typer.echo(f"Level: {finding.level}")
        typer.echo(f"Path: {finding.path}")
        typer.echo(f"Problem: {finding.problem}")
        typer.echo(f"Suggested fix: {finding.suggested_fix}")


@app.callback()
def default() -> None:
    """Run all repository layout checks without changing the repository."""
    findings = run_layout_checks(_repository_root(Path.cwd()))
    _render_findings(findings)
    if findings:
        raise typer.Exit(code=1)
