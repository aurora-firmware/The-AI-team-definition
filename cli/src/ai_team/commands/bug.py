"""`ai-team bug` command group for bug artifact operations."""

from __future__ import annotations

from datetime import date
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


def _exit_not_found(bug_id: str, folders: list[Path]) -> None:
    searched = ", ".join(str(path) for path in folders)
    typer.echo(
        f"Bug '{bug_id}' not found. Searched folders: {searched}",
        err=True,
    )
    raise typer.Exit(code=1)


def _transition_bug(
    bug_id: str,
    *,
    source_state: BugState,
    destination_state: BugState,
    new_status: BugState,
) -> None:
    root = find_project_root(Path.cwd())
    folders = _bug_state_folders(root)

    in_destination = _find_bug_file(bug_id, folders[destination_state])
    if in_destination is not None:
        typer.echo(f"Bug {bug_id} already in {destination_state}.")
        return

    source = _find_bug_file(bug_id, folders[source_state])
    if source is None:
        _exit_not_found(
            bug_id,
            [folders["open"], folders["in-progress"], folders["resolved"]],
        )

    destination = folders[destination_state] / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    update_status(source, new_status)
    move_artifact(source, destination)
    typer.echo(str(destination.resolve()))


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
            created=date.today().isoformat(),
            task=task,
        )
        return dest, model, body

    try:
        bug_id, dest = create_artifact_with_lock(
            root.project_dir,
            allocate_id=lambda: next_bug_id(root),
            build=build,
        )
    except ArtifactExists as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    except LockTimeout as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    absolute_path = str(dest.resolve())
    if as_json:
        print_json({"id": bug_id, "path": absolute_path})
        return

    typer.echo(absolute_path)


@app.command("start")
def start_bug(bug_id: str) -> None:
    """Move an open bug to in-progress and update status."""
    _transition_bug(
        bug_id,
        source_state="open",
        destination_state="in-progress",
        new_status="in-progress",
    )


@app.command("resolve")
def resolve_bug(bug_id: str) -> None:
    """Move an in-progress bug to resolved and update status."""
    _transition_bug(
        bug_id,
        source_state="in-progress",
        destination_state="resolved",
        new_status="resolved",
    )
