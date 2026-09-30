"""`ai-team task` command group for task artifact operations."""

from __future__ import annotations

import re
from pathlib import Path
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
from ai_team.core.lock import LockTimeout, create_artifact_with_lock
from ai_team.core.models import Task
from ai_team.core.result import Result
from ai_team.core.runtime import today
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


def _not_found(task_id: str, folders: list[Path]) -> Result:
    searched = ", ".join(str(path) for path in folders)
    return Result(
        status=1,
        message=f"Task '{task_id}' not found. Searched folders: {searched}",
    )


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
        f"### Session {next_session} — {today().isoformat()}",
        f"Blocked: {reason}",
    ]
    lines = lines[:end] + entry + lines[end:]
    new_body = "\n".join(lines).rstrip() + "\n"
    write_artifact(path, model, new_body, overwrite=True)


def _transition_task(
    root: ProjectRoot,
    task_id: str,
    *,
    source_states: list[TaskState],
    destination_state: TaskState,
    new_status: TaskState,
    before_transition: Callable[[Path], None] | None = None,
) -> Result:
    folders = _task_state_folders(root)

    destination_folder = folders[destination_state]
    in_destination = _find_task_file(task_id, [destination_folder])
    if in_destination is not None:
        return Result(
            status=0,
            payload={
                "id": task_id,
                "path": str(in_destination.resolve()),
                "changed": False,
            },
            message=f"Task {task_id} already in {destination_state}.",
        )

    source = _find_task_file(task_id, [folders[state] for state in source_states])
    if source is None:
        return _not_found(
            task_id,
            [
                folders["pending"],
                folders["in-progress"],
                folders["completed"],
                folders["blocked"],
            ],
        )

    if before_transition is not None:
        before_transition(source)

    destination = destination_folder / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    update_status(source, new_status)
    move_artifact(source, destination)
    return Result(
        status=0,
        payload={"id": task_id, "path": str(destination.resolve()), "changed": True},
    )


def _emit_transition(result: Result) -> None:
    """Print a transition result exactly as the CLI always has."""
    if result.status != 0:
        typer.echo(result.text(), err=True)
        raise typer.Exit(code=result.status)
    if result.message:
        typer.echo(result.message)
        return
    typer.echo(result.payload["path"])


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


def create_task(
    root: ProjectRoot,
    title: str,
    priority: Priority = "medium",
    assigned_role: str = "unassigned",
    spec: str | None = None,
) -> Result:
    """Create a pending task under *root*; return its id/path or a domain-error result."""

    def build(task_id: str) -> tuple[Path, Task, str]:
        slug = slugify(title)
        dest = root.tasks_pending / f"{task_id}-{slug}.md"

        template = load_template("task")
        body = _template_body(template)
        body = body.replace("# [Task Title]", f"# {title}", 1)
        model = Task(
            id=task_id,
            title=title,
            status="pending",
            priority=priority,
            assigned_role=assigned_role,
            created=today().isoformat(),
            spec=spec,
        )
        return dest, model, body

    try:
        task_id, dest = create_artifact_with_lock(
            root.project_dir,
            allocate_id=lambda: next_task_id(root),
            build=build,
        )
    except (ArtifactExists, LockTimeout) as exc:
        return Result(status=1, message=str(exc))

    return Result(status=0, payload={"id": task_id, "path": str(dest.resolve())})


def start_task(root: ProjectRoot, task_id: str) -> Result:
    """Move a pending task to in-progress and update status."""
    return _transition_task(
        root,
        task_id,
        source_states=["pending"],
        destination_state="in-progress",
        new_status="in-progress",
    )


def complete_task(root: ProjectRoot, task_id: str) -> Result:
    """Move an in-progress task to completed and update status."""
    return _transition_task(
        root,
        task_id,
        source_states=["in-progress"],
        destination_state="completed",
        new_status="completed",
    )


def unblock_task(root: ProjectRoot, task_id: str) -> Result:
    """Move a blocked task to in-progress and update status."""
    return _transition_task(
        root,
        task_id,
        source_states=["blocked"],
        destination_state="in-progress",
        new_status="in-progress",
    )


def block_task(root: ProjectRoot, task_id: str, reason: str) -> Result:
    """Move a task to blocked, update status, and append blocking reason."""
    return _transition_task(
        root,
        task_id,
        source_states=["pending", "in-progress", "completed", "blocked"],
        destination_state="blocked",
        new_status="blocked",
        before_transition=lambda source: _append_work_log_entry(source, reason),
    )


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
    result = create_task(root, title, priority, assigned_role, spec)
    if result.status != 0:
        typer.echo(result.text(), err=True)
        raise typer.Exit(code=result.status)

    if as_json:
        print_json(result.payload)
        return

    typer.echo(result.payload["path"])


@app.command("start")
def start_task_command(task_id: str) -> None:
    """Move a pending task to in-progress and update status."""
    _emit_transition(start_task(find_project_root(Path.cwd()), task_id))


@app.command("complete")
def complete_task_command(task_id: str) -> None:
    """Move an in-progress task to completed and update status."""
    _emit_transition(complete_task(find_project_root(Path.cwd()), task_id))


@app.command("unblock")
def unblock_task_command(task_id: str) -> None:
    """Move a blocked task to in-progress and update status."""
    _emit_transition(unblock_task(find_project_root(Path.cwd()), task_id))


@app.command("block")
def block_task_command(
    task_id: str,
    reason: str = typer.Option(..., "--reason"),
) -> None:
    """Move a task to blocked, update status, and append blocking reason."""
    _emit_transition(block_task(find_project_root(Path.cwd()), task_id, reason))
