"""`ai-team task` command group for task artifact operations."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import typer
from slugify import slugify

from ai_team.core.fs import ArtifactExists, write_artifact
from ai_team.core.ids import next_task_id
from ai_team.core.locator import find_project_root
from ai_team.core.models import Task
from ai_team.core.templates import load_template
from ai_team.render import print_json

NAME = "task"
app = typer.Typer(help="Create and manage task artifacts.")

Priority = Literal["critical", "high", "medium", "low"]


def _template_body(template: str) -> str:
    """Return markdown body text after the YAML frontmatter block."""
    if not template.startswith("---"):
        raise ValueError("Task template is missing opening frontmatter fence.")

    rest = template[3:]
    close_idx = rest.find("\n---")
    if close_idx == -1:
        raise ValueError("Task template is missing closing frontmatter fence.")

    body = rest[close_idx + 5 :]
    if body.startswith("\n"):
        body = body[1:]
    return body


@app.command("new")
def new_task(
    title: str,
    priority: Priority = typer.Option("medium", "--priority"),
    assigned_role: str = typer.Option("unassigned", "--assigned-role"),
    spec: str | None = typer.Option(None, "--spec"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Create a new pending task artifact from the bundled template."""
    root = find_project_root(Path.cwd())
    task_id = next_task_id(root)
    slug = slugify(title)
    dest = root.tasks_pending / f"{task_id}-{slug}.md"

    template = load_template("task")
    body = _template_body(template)
    model = Task(
        id=task_id,
        title=title,
        status="pending",
        priority=priority,
        assigned_role=assigned_role,
        created=date.today().isoformat(),
        spec=spec,
    )

    try:
        write_artifact(dest, model, body, overwrite=False)
    except ArtifactExists as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    absolute_path = str(dest.resolve())
    if as_json:
        print_json({"id": task_id, "path": absolute_path})
        return

    typer.echo(absolute_path)
