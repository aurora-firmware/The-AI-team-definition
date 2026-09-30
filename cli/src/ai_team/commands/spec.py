"""`ai-team spec` command group for specification artifact operations."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from slugify import slugify

from ai_team.core.fs import ArtifactExists
from ai_team.core.ids import next_spec_id
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.lock import LockTimeout, create_artifact_with_lock
from ai_team.core.models import Spec
from ai_team.core.result import Result
from ai_team.core.runtime import today
from ai_team.core.templates import load_template
from ai_team.render import print_json

NAME = "spec"
app = typer.Typer(help="Create and manage specification artifacts.")

SpecStatus = Literal["draft", "review", "approved", "superseded"]


def _template_parts(template: str) -> tuple[CommentedMap, str]:
    """Return template frontmatter map and markdown body after the frontmatter block."""
    if not template.startswith("---"):
        raise ValueError("Spec template is missing opening frontmatter fence.")

    rest = template[3:]
    close_idx = rest.find("\n---")
    if close_idx == -1:
        raise ValueError("Spec template is missing closing frontmatter fence.")

    frontmatter = rest[:close_idx]
    body = rest[close_idx + 5 :]
    if body.startswith("\n"):
        body = body[1:]

    yaml = YAML(typ="rt")
    parsed = yaml.load(frontmatter)
    if parsed is None:
        return CommentedMap(), body
    return parsed, body


def create_spec(
    root: ProjectRoot,
    title: str,
    author: str = "planner",
    status: SpecStatus = "draft",
) -> Result:
    """Create a spec under *root*; return its id/path or a domain-error result."""

    def build(spec_id: str) -> tuple[Path, Spec, str]:
        slug = slugify(title)
        dest = root.specs / f"{spec_id}-{slug}.md"

        template = load_template("spec")
        source_map, body = _template_parts(template)

        model = Spec(
            title=title,
            version="0.1",
            status=status,
            created=today().isoformat(),
            author=author,
            id=spec_id,
            _source_map=source_map,
        )

        body = body.replace("# [Specification Title]", f"# {title}", 1)
        return dest, model, body

    try:
        spec_id, dest = create_artifact_with_lock(
            root.project_dir,
            allocate_id=lambda: next_spec_id(root),
            build=build,
        )
    except (ArtifactExists, LockTimeout) as exc:
        return Result(status=1, message=str(exc))

    return Result(status=0, payload={"id": spec_id, "path": str(dest.resolve())})


@app.command("new")
def new_spec(
    title: str,
    author: str = typer.Option("planner", "--author"),
    status: SpecStatus = typer.Option("draft", "--status"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Create a new specification artifact from the bundled template."""
    root = find_project_root(Path.cwd())
    result = create_spec(root, title, author, status)
    if result.status != 0:
        typer.echo(result.text(), err=True)
        raise typer.Exit(code=result.status)

    if as_json:
        print_json(result.payload)
        return

    typer.echo(result.payload["path"])
