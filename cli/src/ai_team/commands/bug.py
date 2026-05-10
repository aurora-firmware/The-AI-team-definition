"""`ai-team bug` command group for bug artifact operations."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import typer
from slugify import slugify

from ai_team.core.fs import ArtifactExists, write_artifact
from ai_team.core.ids import next_bug_id
from ai_team.core.locator import find_project_root
from ai_team.core.models import Bug
from ai_team.core.templates import load_template
from ai_team.render import print_json

NAME = "bug"
app = typer.Typer(help="Create and manage bug artifacts.")

Severity = Literal["critical", "high", "medium", "low"]


def _template_body(template: str) -> str:
    """Return markdown body text after the YAML frontmatter block."""
    if not template.startswith("---"):
        raise ValueError("Bug template is missing opening frontmatter fence.")

    rest = template[3:]
    close_idx = rest.find("\n---")
    if close_idx == -1:
        raise ValueError("Bug template is missing closing frontmatter fence.")

    body = rest[close_idx + 5 :]
    if body.startswith("\n"):
        body = body[1:]
    return body


@app.command("new")
def new_bug(
    title: str,
    severity: Severity = typer.Option("medium", "--severity"),
    task: str | None = typer.Option(None, "--task"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Create a new open bug artifact from the bundled template."""
    root = find_project_root(Path.cwd())
    bug_id = next_bug_id(root)
    slug = slugify(title)
    dest = root.bugs_open / f"{bug_id}-{slug}.md"

    template = load_template("bug")
    body = _template_body(template)
    model = Bug(
        id=bug_id,
        title=title,
        severity=severity,
        status="open",
        created=date.today().isoformat(),
        task=task,
    )

    try:
        write_artifact(dest, model, body, overwrite=False)
    except ArtifactExists as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    absolute_path = str(dest.resolve())
    if as_json:
        print_json({"id": bug_id, "path": absolute_path})
        return

    typer.echo(absolute_path)
