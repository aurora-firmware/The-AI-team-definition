"""`ai-team spec` command group for specification artifact operations."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import typer
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from slugify import slugify

from ai_team.core.fs import ArtifactExists
from ai_team.core.ids import next_spec_id
from ai_team.core.locator import find_project_root
from ai_team.core.lock import LockTimeout, create_artifact_with_lock
from ai_team.core.models import Spec
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


@app.command("new")
def new_spec(
    title: str,
    author: str = typer.Option("planner", "--author"),
    status: SpecStatus = typer.Option("draft", "--status"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Create a new specification artifact from the bundled template."""
    root = find_project_root(Path.cwd())

    def build(spec_id: str) -> tuple[Path, Spec, str]:
        slug = slugify(title)
        dest = root.specs / f"{spec_id}-{slug}.md"

        template = load_template("spec")
        source_map, body = _template_parts(template)
        source_map["id"] = spec_id

        model = Spec(
            title=title,
            version="0.1",
            status=status,
            created=date.today().isoformat(),
            author=author,
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
    except ArtifactExists as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    except LockTimeout as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    absolute_path = str(dest.resolve())
    if as_json:
        print_json({"id": spec_id, "path": absolute_path})
        return

    typer.echo(absolute_path)
