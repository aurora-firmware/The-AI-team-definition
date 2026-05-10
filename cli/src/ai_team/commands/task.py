"""`ai-team task` command group for task artifact operations."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import typer
from slugify import slugify

from ai_team.core.fs import ArtifactExists, move_artifact, update_status, write_artifact
from ai_team.core.ids import next_task_id
from ai_team.core.locator import find_project_root
from ai_team.core.models import Task
from ai_team.core.templates import load_template
from ai_team.render import print_json

NAME = "task"
app = typer.Typer(help="Create and manage task artifacts.")

Priority = Literal["critical", "high", "medium", "low"]


def _task_matches_id(path: Path, task_id: str) -> bool:
    stem = path.stem
    return stem == task_id or stem.startswith(f"{task_id}-")


def _find_task_file(task_id: str, folders: list[Path]) -> Path | None:
    for folder in folders:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.md")):
            if path.name == ".gitkeep" or path.match("TEMPLATE-*.md"):
                continue
            if _task_matches_id(path, task_id):
                return path
    return None


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


@app.command("start")
def start_task(task_id: str) -> None:
    """Move a pending task to in-progress and update status."""
    root = find_project_root(Path.cwd())

    in_progress = _find_task_file(task_id, [root.tasks_in_progress])
    if in_progress is not None:
        typer.echo(f"Task {task_id} already in in-progress.")
        return

    source = _find_task_file(task_id, [root.tasks_pending])
    if source is None:
        searched = ", ".join(str(path) for path in [root.tasks_pending, root.tasks_in_progress])
        typer.echo(
            f"Task '{task_id}' not found. Searched folders: {searched}",
            err=True,
        )
        raise typer.Exit(code=1)

    destination = root.tasks_in_progress / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    update_status(source, "in-progress")
    move_artifact(source, destination)
    typer.echo(str(destination.resolve()))
