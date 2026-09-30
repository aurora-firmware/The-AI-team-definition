"""`ai-team bug` command group for bug artifact operations."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from slugify import slugify

from ai_team.core.fs import (
    ArtifactExists,
    move_artifact,
    update_status,
)
from ai_team.core.ids import next_bug_id
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.lock import LockTimeout, create_artifact_with_lock
from ai_team.core.models import Bug
from ai_team.core.result import Result
from ai_team.core.runtime import today
from ai_team.core.templates import load_template
from ai_team.render import print_json

NAME = "bug"
app = typer.Typer(help="Create and manage bug artifacts.")

Severity = Literal["critical", "high", "medium", "low"]
BugState = Literal["open", "in-progress", "resolved"]


def _bug_matches_id(path: Path, bug_id: str) -> bool:
    stem = path.stem
    return stem == bug_id or stem.startswith(f"{bug_id}-")


def _find_bug_file(bug_id: str, folder: Path) -> Path | None:
    if not folder.exists():
        return None
    for path in sorted(folder.glob("*.md")):
        if path.name == ".gitkeep" or path.match("TEMPLATE-*.md"):
            continue
        if _bug_matches_id(path, bug_id):
            return path
    return None


def _bug_state_folders(root: ProjectRoot) -> dict[BugState, Path]:
    return {
        "open": root.bugs_open,
        "in-progress": root.bugs_in_progress,
        "resolved": root.bugs_resolved,
    }


def _not_found(bug_id: str, folders: list[Path]) -> Result:
    searched = ", ".join(str(path) for path in folders)
    return Result(
        status=1,
        message=f"Bug '{bug_id}' not found. Searched folders: {searched}",
    )


def _transition_bug(
    root: ProjectRoot,
    bug_id: str,
    *,
    source_state: BugState,
    destination_state: BugState,
    new_status: BugState,
) -> Result:
    folders = _bug_state_folders(root)

    in_destination = _find_bug_file(bug_id, folders[destination_state])
    if in_destination is not None:
        return Result(
            status=0,
            payload={
                "id": bug_id,
                "path": str(in_destination.resolve()),
                "changed": False,
            },
            message=f"Bug {bug_id} already in {destination_state}.",
        )

    source = _find_bug_file(bug_id, folders[source_state])
    if source is None:
        return _not_found(
            bug_id,
            [folders["open"], folders["in-progress"], folders["resolved"]],
        )

    destination = folders[destination_state] / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    update_status(source, new_status)
    move_artifact(source, destination)
    return Result(
        status=0,
        payload={"id": bug_id, "path": str(destination.resolve()), "changed": True},
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
        raise ValueError("Bug template is missing opening frontmatter fence.")

    rest = template[3:]
    close_idx = rest.find("\n---")
    if close_idx == -1:
        raise ValueError("Bug template is missing closing frontmatter fence.")

    body = rest[close_idx + 5 :]
    if body.startswith("\n"):
        body = body[1:]
    return body


def create_bug(
    root: ProjectRoot,
    title: str,
    severity: Severity = "medium",
    task: str | None = None,
) -> Result:
    """Create an open bug under *root*; return its id/path or a domain-error result."""

    def build(bug_id: str) -> tuple[Path, Bug, str]:
        slug = slugify(title)
        dest = root.bugs_open / f"{bug_id}-{slug}.md"

        template = load_template("bug")
        body = _template_body(template)
        body = body.replace("# [Bug Title]", f"# {title}", 1)
        model = Bug(
            id=bug_id,
            title=title,
            severity=severity,
            status="open",
            created=today().isoformat(),
            task=task,
        )
        return dest, model, body

    try:
        bug_id, dest = create_artifact_with_lock(
            root.project_dir,
            allocate_id=lambda: next_bug_id(root),
            build=build,
        )
    except (ArtifactExists, LockTimeout) as exc:
        return Result(status=1, message=str(exc))

    return Result(status=0, payload={"id": bug_id, "path": str(dest.resolve())})


def start_bug(root: ProjectRoot, bug_id: str) -> Result:
    """Move an open bug to in-progress and update status."""
    return _transition_bug(
        root,
        bug_id,
        source_state="open",
        destination_state="in-progress",
        new_status="in-progress",
    )


def resolve_bug(root: ProjectRoot, bug_id: str) -> Result:
    """Move an in-progress bug to resolved and update status."""
    return _transition_bug(
        root,
        bug_id,
        source_state="in-progress",
        destination_state="resolved",
        new_status="resolved",
    )


@app.command("new")
def new_bug(
    title: str,
    severity: Severity = typer.Option("medium", "--severity"),
    task: str | None = typer.Option(None, "--task"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Create a new open bug artifact from the bundled template."""
    root = find_project_root(Path.cwd())
    result = create_bug(root, title, severity, task)
    if result.status != 0:
        typer.echo(result.text(), err=True)
        raise typer.Exit(code=result.status)

    if as_json:
        print_json(result.payload)
        return

    typer.echo(result.payload["path"])


@app.command("start")
def start_bug_command(bug_id: str) -> None:
    """Move an open bug to in-progress and update status."""
    _emit_transition(start_bug(find_project_root(Path.cwd()), bug_id))


@app.command("resolve")
def resolve_bug_command(bug_id: str) -> None:
    """Move an in-progress bug to resolved and update status."""
    _emit_transition(resolve_bug(find_project_root(Path.cwd()), bug_id))
