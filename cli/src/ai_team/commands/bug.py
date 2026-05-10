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
    write_artifact,
)
from ai_team.core.ids import next_bug_id
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.models import Bug
from ai_team.core.templates import load_template
from ai_team.render import print_json

NAME = "bug"
app = typer.Typer(help="Create and manage bug artifacts.")

Severity = Literal["critical", "high", "medium", "low"]


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


def _bug_state_folders(root: ProjectRoot) -> dict[str, Path]:
    return {
        "open": root.bugs_open,
        "in-progress": root.bugs_in_progress,
        "resolved": root.bugs_resolved,
    }


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


@app.command("start")
def start_bug(bug_id: str) -> None:
    """Move an open bug to in-progress and update status."""
    root = find_project_root(Path.cwd())
    folders = _bug_state_folders(root)
    source = _find_bug_file(bug_id, folders["open"])
    if source is None:
        typer.echo(f"Bug '{bug_id}' not found in {folders['open']}", err=True)
        raise typer.Exit(code=1)

    destination = folders["in-progress"] / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    update_status(source, "in-progress")
    move_artifact(source, destination)
    typer.echo(str(destination.resolve()))


@app.command("resolve")
def resolve_bug(bug_id: str) -> None:
    """Move an in-progress bug to resolved and update status."""
    root = find_project_root(Path.cwd())
    folders = _bug_state_folders(root)
    source = _find_bug_file(bug_id, folders["in-progress"])
    if source is None:
        typer.echo(
            f"Bug '{bug_id}' not found in {folders['in-progress']}",
            err=True,
        )
        raise typer.Exit(code=1)

    destination = folders["resolved"] / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    update_status(source, "resolved")
    move_artifact(source, destination)
    typer.echo(str(destination.resolve()))
