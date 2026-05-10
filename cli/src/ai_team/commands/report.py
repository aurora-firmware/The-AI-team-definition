"""`ai-team report` command for writing Gate 5 progress-report markdown files."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import typer

from ai_team.core.locator import find_project_root
from ai_team.core.templates import load_template

NAME = "report"
app = typer.Typer(help="Write a Gate 5 progress report.", invoke_without_command=True)


@app.callback()
def default(
    out: Path | None = typer.Option(
        None,
        "--out",
        help="Override destination path.",
    ),
) -> None:
    """Write the bundled progress-report template to disk."""
    root = find_project_root(Path.cwd())

    destination = out
    if destination is None:
        destination = (
            root.docs
            / "reports"
            / f"progress-report-{date.today().isoformat()}.md"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(load_template("report"), encoding="utf-8")
    typer.echo(str(destination.resolve()))
