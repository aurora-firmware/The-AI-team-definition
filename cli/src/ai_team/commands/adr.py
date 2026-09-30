"""`ai-team adr` command group for ADR artifact operations."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from slugify import slugify

from ai_team.core.fs import ArtifactExists, write_artifact
from ai_team.core.ids import next_adr_id
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.models import Adr
from ai_team.core.result import Result
from ai_team.core.runtime import today
from ai_team.core.templates import load_template
from ai_team.render import print_json

NAME = "adr"
app = typer.Typer(help="Create and manage ADR artifacts.")

AdrStatus = Literal["proposed", "accepted", "superseded"]


def _template_body(template: str) -> str:
    """Return markdown body text after the YAML frontmatter block."""
    if not template.startswith("---"):
        raise ValueError("ADR template is missing opening frontmatter fence.")

    rest = template[3:]
    close_idx = rest.find("\n---")
    if close_idx == -1:
        raise ValueError("ADR template is missing closing frontmatter fence.")

    body = rest[close_idx + 5 :]
    if body.startswith("\n"):
        body = body[1:]
    return body


def create_adr(
    root: ProjectRoot,
    title: str,
    status: AdrStatus = "proposed",
    supersedes: str | None = None,
) -> Result:
    """Create an ADR under *root*; return its id/path or a domain-error result."""
    adr_id = next_adr_id(root)
    slug = slugify(title)
    dest = root.decisions / f"{adr_id}-{slug}.md"

    template = load_template("adr")
    body = _template_body(template)
    model = Adr(
        id=adr_id,
        title=title,
        status=status,
        created=today().isoformat(),
        supersedes=supersedes,
    )

    try:
        write_artifact(dest, model, body, overwrite=False)
    except ArtifactExists as exc:
        return Result(status=1, message=str(exc))

    return Result(status=0, payload={"id": adr_id, "path": str(dest.resolve())})


@app.command("new")
def new_adr(
    title: str,
    status: AdrStatus = typer.Option("proposed", "--status"),
    supersedes: str | None = typer.Option(None, "--supersedes"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Create a new ADR artifact from the bundled template."""
    root = find_project_root(Path.cwd())
    result = create_adr(root, title, status, supersedes)
    if result.status != 0:
        typer.echo(result.text(), err=True)
        raise typer.Exit(code=result.status)

    if as_json:
        print_json(result.payload)
        return

    typer.echo(result.payload["path"])
