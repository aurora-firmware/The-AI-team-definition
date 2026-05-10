"""`ai-team task` command group for task artifact operations."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import re
from typing import Callable, Literal

import typer
from slugify import slugify

from ai_team.core.fs import (
    ArtifactExists,
    move_artifact,
    read_artifact,
    update_status,
    write_artifact,
)
from ai_team.core.ids import next_task_id
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.models import Task
from ai_team.core.templates import load_template
from ai_team.render import print_json

NAME = "task"
app = typer.Typer(help="Create and manage task artifacts.")

Priority = Literal["critical", "high", "medium", "low"]
TaskState = Literal["pending", "in-progress", "completed", "blocked"]


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


def _task_state_folders(root: ProjectRoot) -> dict[TaskState, Path]:
    return {
        "pending": root.tasks_pending,
        "in-progress": root.tasks_in_progress,
        "completed": root.tasks_completed,
        "blocked": root.tasks_blocked,
    }


def _exit_not_found(task_id: str, folders: list[Path]) -> None:
    searched = ", ".join(str(path) for path in folders)
    typer.echo(
        f"Task '{task_id}' not found. Searched folders: {searched}",
        err=True,
    )
    raise typer.Exit(code=1)


def _append_work_log_entry(path: Path, reason: str) -> None:
    model, body = read_artifact(path, "task")
    lines = body.splitlines()
    heading = "## Work Log"

    try:
        start = lines.index(heading)
    except ValueError:
        lines.extend(["", heading, ""])
        start = len(lines) - 3

    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break

    session_numbers: list[int] = []
    for line in lines[start:end]:
        match = re.match(r"^### Session (\d+)\b", line)
        if match is not None:
            session_numbers.append(int(match.group(1)))
    next_session = max(session_numbers, default=0) + 1

    entry = [
        "",
        f"### Session {next_session} — {date.today().isoformat()}",
        f"Blocked: {reason}",
    ]
    lines = lines[:end] + entry + lines[end:]
    new_body = "\n".join(lines).rstrip() + "\n"
    write_artifact(path, model, new_body, overwrite=True)


def _transition_task(
    task_id: str,
    *,
    source_states: list[TaskState],
    destination_state: TaskState,
    new_status: TaskState,
    before_transition: Callable[[Path], None] | None = None,
) -> None:
    root = find_project_root(Path.cwd())
    folders = _task_state_folders(root)

    destination_folder = folders[destination_state]
    in_destination = _find_task_file(task_id, [destination_folder])
    if in_destination is not None:
        typer.echo(f"Task {task_id} already in {destination_state}.")
        return

    source = _find_task_file(task_id, [folders[state] for state in source_states])
    if source is None:
        _exit_not_found(
            task_id,
            [folders["pending"], folders["in-progress"], folders["completed"], folders["blocked"]],
        )

    if before_transition is not None:
        before_transition(source)

    destination = destination_folder / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    update_status(source, new_status)
    move_artifact(source, destination)
    typer.echo(str(destination.resolve()))


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
    _transition_task(
        task_id,
        source_states=["pending"],
        destination_state="in-progress",
        new_status="in-progress",
    )


@app.command("complete")
def complete_task(task_id: str) -> None:
    """Move an in-progress task to completed and update status."""
    _transition_task(
        task_id,
        source_states=["in-progress"],
        destination_state="completed",
        new_status="completed",
    )


@app.command("unblock")
def unblock_task(task_id: str) -> None:
    """Move a blocked task to in-progress and update status."""
    _transition_task(
        task_id,
        source_states=["blocked"],
        destination_state="in-progress",
        new_status="in-progress",
    )


@app.command("block")
def block_task(
    task_id: str,
    reason: str = typer.Option(..., "--reason"),
) -> None:
    """Move a task to blocked, update status, and append blocking reason."""
    _transition_task(
        task_id,
        source_states=["pending", "in-progress", "completed", "blocked"],
        destination_state="blocked",
        new_status="blocked",
        before_transition=lambda source: _append_work_log_entry(source, reason),
    )
