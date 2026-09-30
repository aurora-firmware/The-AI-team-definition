"""`ai-team change-request` command group for change-request artifact operations."""

from __future__ import annotations

from pathlib import Path

import typer
from slugify import slugify

from ai_team.core.fs import ArtifactExists, write_artifact
from ai_team.core.ids import next_change_request_id
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.models import ChangeRequest
from ai_team.core.result import Result
from ai_team.core.runtime import today
from ai_team.core.templates import load_template
from ai_team.render import print_json

NAME = "change-request"
app = typer.Typer(help="Create and manage change-request artifacts.")


def _template_body(template: str) -> str:
    """Return markdown body text after the YAML frontmatter block."""
    if not template.startswith("---"):
        raise ValueError(
            "Change-request template is missing opening frontmatter fence."
        )

    rest = template[3:]
    close_idx = rest.find("\n---")
    if close_idx == -1:
        raise ValueError(
            "Change-request template is missing closing frontmatter fence."
        )

    body = rest[close_idx + 5 :]
    if body.startswith("\n"):
        body = body[1:]
    return body


def create_change_request(root: ProjectRoot, title: str) -> Result:
    """Create a change request under *root*; return its id/path or an error result."""
    cr_id = next_change_request_id((root.change_requests,))
    slug = slugify(title)
    dest = root.change_requests / f"{cr_id}-{slug}.md"

    template = load_template("change-request")
    body = _template_body(template)
    body = body.replace("# [Change Request Title]", f"# {title}", 1)
    model = ChangeRequest(
        id=cr_id,
        title=title,
        status="pending",
        created=today().isoformat(),
    )

    try:
        write_artifact(dest, model, body, overwrite=False)
    except ArtifactExists as exc:
        return Result(status=1, message=str(exc))

    return Result(status=0, payload={"id": cr_id, "path": str(dest.resolve())})


@app.command("new")
def new_change_request(
    title: str,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Create a new change-request artifact from the bundled template."""
    root = find_project_root(Path.cwd())
    result = create_change_request(root, title)
    if result.status != 0:
        typer.echo(result.text(), err=True)
        raise typer.Exit(code=result.status)

    if as_json:
        print_json(result.payload)
        return

    typer.echo(result.payload["path"])
